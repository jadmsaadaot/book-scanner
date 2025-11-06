"""API routes for book scanning and library management."""

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Book,
    BookPublic,
    BooksPublic,
    DetectedBook,
    ScanResult,
    User,
    UserLibrary,
)
from app.services.google_books_service import GoogleBooksService
from app.services.recommendation_service import RecommendationService
from app.services.vision_service import VisionService

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/scan", response_model=ScanResult)
@limiter.limit("10/minute")  # 10 scans per minute per IP
async def scan_books(
    request: Request,
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> Any:
    """
    Scan an image of books and return detected books with recommendations.

    This endpoint:
    1. Accepts an image upload
    2. Uses Vision Language Model to extract book titles and authors
    3. Queries Google Books API for each detected title (parallel)
    4. Compares against user's library
    5. Returns recommendations based on user's reading preferences
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read image bytes with size limit (10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        image_bytes = await file.read()

        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB"
            )

        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="File is empty")

        # Extract book titles using Vision Language Model
        detected_titles = await VisionService.extract_book_titles(image_bytes)

        if not detected_titles:
            return ScanResult(detected_books=[], recommendations=[])

        # Search for each title in Google Books (in parallel)
        async def search_title(title_data: dict[str, Any]) -> dict[str, Any] | None:
            """Helper to search a single title and add confidence."""
            title = title_data["title"]
            author = title_data.get("author")
            confidence = title_data["confidence"]

            book_data = await GoogleBooksService.fuzzy_search_book(title, author=author)
            if book_data:
                book_data["confidence"] = confidence
                return book_data
            return None

        # Run all searches in parallel
        search_tasks = [search_title(title_data) for title_data in detected_titles]
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Filter out None results and exceptions
        detected_books_list: list[dict[str, Any]] = [
            book for book in search_results
            if book is not None and not isinstance(book, Exception)
        ]

        # Get user's library
        user_library = RecommendationService.get_user_library_books(
            session, str(current_user.id)
        )

        # Generate recommendations
        all_books, recommendations = (
            await RecommendationService.filter_and_rank_recommendations(
                detected_books_list,
                user_library,
                str(current_user.id),
                session,
            )
        )

        # Convert to response models
        detected_books = [
            DetectedBook(
                title=book["title"],
                author=book.get("author"),
                isbn=book.get("isbn"),
                thumbnail_url=book.get("thumbnail_url"),
                google_books_id=book.get("google_books_id"),
                confidence=book.get("confidence", 0.0),
                match_score=book.get("match_score", 0.0),
                in_library=book.get("in_library", False),
                recommendation_explanation=book.get("recommendation_explanation"),
            )
            for book in all_books
        ]

        recommendation_books = [
            DetectedBook(
                title=book["title"],
                author=book.get("author"),
                isbn=book.get("isbn"),
                thumbnail_url=book.get("thumbnail_url"),
                google_books_id=book.get("google_books_id"),
                confidence=book.get("confidence", 0.0),
                match_score=book.get("match_score", 0.0),
                in_library=False,
                recommendation_explanation=book.get("recommendation_explanation"),
            )
            for book in recommendations
        ]

        return ScanResult(
            detected_books=detected_books, recommendations=recommendation_books
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing image: {str(e)}"
        ) from e


@router.post("/library/add/{google_books_id}", response_model=BookPublic)
async def add_book_to_library(
    *, session: SessionDep, current_user: CurrentUser, google_books_id: str
) -> Any:
    """
    Add a book to user's library by Google Books ID.

    This endpoint:
    1. Fetches book details from Google Books API
    2. Creates book in database if it doesn't exist
    3. Adds to user's library
    """
    # Check if book already in library
    existing = session.exec(
        select(UserLibrary)
        .join(Book)
        .where(
            UserLibrary.user_id == current_user.id,
            Book.google_books_id == google_books_id,
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400, detail="Book already in your library"
        )

    # Fetch book details from Google Books
    book_data = await GoogleBooksService.get_book_by_id(google_books_id)

    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check if book exists in database
    db_book = session.exec(
        select(Book).where(Book.google_books_id == google_books_id)
    ).first()

    if not db_book:
        # Create new book
        db_book = Book(
            title=book_data["title"],
            author=book_data.get("author"),
            isbn=book_data.get("isbn"),
            publisher=book_data.get("publisher"),
            published_date=book_data.get("published_date"),
            description=book_data.get("description"),
            page_count=book_data.get("page_count"),
            categories=book_data.get("categories"),
            thumbnail_url=book_data.get("thumbnail_url"),
            google_books_id=google_books_id,
            average_rating=book_data.get("average_rating"),
            ratings_count=book_data.get("ratings_count"),
        )
        session.add(db_book)
        session.commit()
        session.refresh(db_book)

    # Add to user's library
    user_library_entry = UserLibrary(
        user_id=current_user.id, book_id=db_book.id
    )
    session.add(user_library_entry)
    session.commit()
    session.refresh(db_book)

    return db_book


@router.delete("/library/remove/{book_id}")
async def remove_book_from_library(
    *, session: SessionDep, current_user: CurrentUser, book_id: uuid.UUID
) -> Any:
    """Remove a book from user's library."""
    user_library_entry = session.exec(
        select(UserLibrary).where(
            UserLibrary.user_id == current_user.id,
            UserLibrary.book_id == book_id,
        )
    ).first()

    if not user_library_entry:
        raise HTTPException(status_code=404, detail="Book not in your library")

    session.delete(user_library_entry)
    session.commit()

    return {"message": "Book removed from library"}


@router.get("/library", response_model=BooksPublic)
def get_user_library(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """Get all books in user's library."""
    count_statement = (
        select(func.count())
        .select_from(UserLibrary)
        .where(UserLibrary.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Book)
        .join(UserLibrary)
        .where(UserLibrary.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    books = session.exec(statement).all()

    return BooksPublic(data=list(books), count=count)
