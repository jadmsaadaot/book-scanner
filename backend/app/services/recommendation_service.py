"""Recommendation service for suggesting books based on user's library."""

import json
import logging
from typing import Any

from sqlmodel import Session, select

from app.core.config import settings
from app.models import Book, UserLibrary

logger = logging.getLogger(__name__)

class RecommendationService:
    """Service for generating book recommendations."""

    @staticmethod
    def calculate_match_score_rule_based(
        detected_book: dict[str, Any], user_library: list[Book]
    ) -> float:
        """
        Calculate how well a detected book matches user's reading preferences.

        Args:
            detected_book: Book metadata from Google Books
            user_library: List of books in user's library

        Returns:
            Match score between 0.0 and 1.0
        """
        if not user_library:
            # No library to compare against, use rating as fallback
            rating = detected_book.get("average_rating", 0.0)
            return min((rating or 0.0) / 5.0, 1.0)

        score = 0.0
        weights = {
            "author": 0.4,
            "category": 0.3,
            "rating": 0.2,
            "popularity": 0.1,
        }

        # Extract detected book info
        detected_author = detected_book.get("author", "").lower()
        detected_categories = RecommendationService._parse_categories(
            detected_book.get("categories")
        )
        detected_rating = detected_book.get("average_rating", 0.0)

        # Author matching
        library_authors = {
            book.author.lower() for book in user_library if book.author
        }
        if detected_author and any(
            author in detected_author or detected_author in author
            for author in library_authors
        ):
            score += weights["author"]

        # Category matching
        library_categories = set()
        for book in user_library:
            if book.categories:
                library_categories.update(
                    RecommendationService._parse_categories(book.categories)
                )

        if detected_categories and library_categories:
            category_overlap = len(
                detected_categories.intersection(library_categories)
            )
            if category_overlap > 0:
                # Scale by overlap (more overlap = higher score)
                category_score = min(category_overlap / 3.0, 1.0)
                score += weights["category"] * category_score

        # Rating score (higher rated books get higher scores)
        if detected_rating:
            rating_score = min(detected_rating / 5.0, 1.0)
            score += weights["rating"] * rating_score

        # Popularity score based on ratings count
        ratings_count = detected_book.get("ratings_count", 0)
        if ratings_count:
            # Log scale for popularity (1000+ ratings = max score)
            popularity_score = min(ratings_count / 1000.0, 1.0)
            score += weights["popularity"] * popularity_score

        return min(score, 1.0)

    @staticmethod
    def _parse_categories(categories_str: str | None) -> set[str]:
        """
        Parse categories JSON string into a set of lowercase categories.

        Args:
            categories_str: JSON string of categories

        Returns:
            Set of lowercase category strings
        """
        if not categories_str:
            return set()

        try:
            categories = json.loads(categories_str)
            return {cat.lower() for cat in categories if isinstance(cat, str)}
        except (json.JSONDecodeError, TypeError):
            return set()

    @staticmethod
    def get_user_library_books(session: Session, user_id: str) -> list[Book]:
        """
        Get all books in user's library.

        Args:
            session: Database session
            user_id: User UUID

        Returns:
            List of Book objects
        """
        statement = (
            select(Book)
            .join(UserLibrary)
            .where(UserLibrary.user_id == user_id)
        )
        results = session.exec(statement)
        return list(results.all())


    @staticmethod
    async def filter_and_rank_recommendations(
        detected_books: list[dict[str, Any]],
        user_library: list[Book],
        user_id: str,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """
        Filter and rank detected books into recommendations.

        Args:
            detected_books: List of books detected from scan
            user_library: User's library books
            user_id: User UUID

        Returns:
            Tuple of (all_detected_books, recommendations)
        """
        all_books = []
        recommendations = []

        # Calculate match scores - use batch scoring for efficiency
        if settings.LLM_ENABLED and detected_books:
            try:
                # Import here to avoid circular imports
                from app.services.llm.factory import calculate_batch_scores_with_fallback
                from app.services.llm.base import sample_library_books

                # Convert Book objects to dicts for LLM
                library_dicts = [
                    {
                        "title": book.title,
                        "author": book.author,
                        "categories": book.categories,
                        "description": book.description,
                        "average_rating": book.average_rating,
                        "ratings_count": book.ratings_count,
                    }
                    for book in user_library
                ]

                # Sample library books with deterministic shuffling to avoid bias
                sampled_library = sample_library_books(library_dicts, user_id)

                # Get all scores in a single batch LLM call
                logger.info(f"Batch scoring {len(detected_books)} books with LLM")
                batch_results = await calculate_batch_scores_with_fallback(
                    detected_books, sampled_library
                )

                # Create a mapping of title -> (score, explanation) for safe matching
                results_by_title = {
                    result["title"]: (result["score"], result["explanation"])
                    for result in batch_results
                }

                # Apply scores to books by matching titles
                for book in detected_books:
                    book_title = book.get("title", "")
                    if book_title in results_by_title:
                        match_score, explanation = results_by_title[book_title]
                        book["match_score"] = match_score
                        book["recommendation_explanation"] = explanation
                    else:
                        # Fallback if LLM didn't return this book (shouldn't happen)
                        logger.warning(f"LLM did not return score for book: {book_title}")
                        book["match_score"] = RecommendationService.calculate_match_score_rule_based(
                            book, user_library
                        )
                        book["recommendation_explanation"] = "Rule-based recommendation (LLM missing)"

            except Exception as e:
                # Fallback to rule-based scoring for all books if batch fails
                logger.error(f"Batch LLM scoring failed: {str(e)}, falling back to rule-based")
                for book in detected_books:
                    match_score = RecommendationService.calculate_match_score_rule_based(
                        book, user_library
                    )
                    book["match_score"] = match_score
                    book["recommendation_explanation"] = "Rule-based recommendation (LLM batch error)"
        else:
            # Use rule-based scoring
            for book in detected_books:
                match_score = RecommendationService.calculate_match_score_rule_based(
                    book, user_library
                )
                book["match_score"] = match_score
                book["recommendation_explanation"] = "Rule-based recommendation"

        # Build set of google_books_ids from user's library for O(1) lookup
        library_google_ids = {
            book.google_books_id
            for book in user_library
            if book.google_books_id
        }

        # Check if each book is in library and build results
        for book in detected_books:
            google_books_id = book.get("google_books_id")
            in_library = google_books_id in library_google_ids if google_books_id else False
            book["in_library"] = in_library

            all_books.append(book)

            # Only recommend books not in library
            if not in_library:
                recommendations.append(book)

        # Sort recommendations by match score (descending)
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)

        return all_books, recommendations
