"""Recommendation service for suggesting books based on user's library."""

import hashlib
import json
import logging
from typing import Any

from cachetools import TTLCache
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Book, User, UserLibrary

logger = logging.getLogger(__name__)

# Simple in-memory cache for LLM recommendations
# TTL of 1 hour, max 1000 entries
_recommendation_cache: TTLCache = TTLCache(maxsize=1000, ttl=3600)


class RecommendationService:
    """Service for generating book recommendations."""

    @staticmethod
    async def calculate_match_score_llm(
        detected_book: dict[str, Any], user_library: list[Book], user_id: str
    ) -> tuple[float, str]:
        """
        Calculate match score using LLM with caching.

        Args:
            detected_book: Book metadata from Google Books
            user_library: List of books in user's library
            user_id: User ID for deterministic sampling

        Returns:
            Tuple of (match_score, explanation)
        """
        # Generate cache key based on library and detected book
        library_ids = sorted([str(book.id) for book in user_library])
        library_hash = hashlib.md5(
            "".join(library_ids).encode()
        ).hexdigest()
        detected_book_id = detected_book.get("google_books_id", "")
        cache_key = f"{library_hash}:{detected_book_id}"

        # Check cache
        if cache_key in _recommendation_cache:
            return _recommendation_cache[cache_key]

        try:
            # Import here to avoid circular imports
            from app.services.llm import get_llm_provider
            from app.services.llm.base import sample_library_books

            # Get LLM provider
            provider = get_llm_provider()

            # Convert Book objects to dicts for LLM
            library_dicts = [
                {
                    "title": book.title,
                    "author": book.author,
                    "categories": book.categories,
                    "description": book.description,
                    "average_rating": book.average_rating,
                }
                for book in user_library
            ]

            # Sample library books with deterministic shuffling to avoid bias
            sampled_library = sample_library_books(library_dicts, user_id)

            # Get LLM score and explanation
            score, explanation = await provider.calculate_book_match_score(
                detected_book, sampled_library
            )

            # Cache the result
            result = (score, explanation)
            _recommendation_cache[cache_key] = result

            return result

        except ImportError as e:
            logger.warning(f"LLM provider not available: {str(e)}")
            score = RecommendationService.calculate_match_score_rule_based(
                detected_book, user_library
            )
            return score, "Rule-based recommendation (LLM unavailable)"
        except Exception as e:
            logger.error(f"Error in LLM-based scoring: {str(e)}", exc_info=True)
            score = RecommendationService.calculate_match_score_rule_based(
                detected_book, user_library
            )
            return score, "Rule-based recommendation (LLM error)"

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
    def is_book_in_library(
        session: Session, user_id: str, google_books_id: str | None
    ) -> bool:
        """
        Check if a book is already in user's library.

        Args:
            session: Database session
            user_id: User UUID
            google_books_id: Google Books volume ID

        Returns:
            True if book is in library, False otherwise
        """
        if not google_books_id:
            return False

        statement = (
            select(UserLibrary)
            .join(Book)
            .where(
                UserLibrary.user_id == user_id,
                Book.google_books_id == google_books_id,
            )
        )
        result = session.exec(statement).first()
        return result is not None

    @staticmethod
    async def filter_and_rank_recommendations(
        detected_books: list[dict[str, Any]],
        user_library: list[Book],
        user_id: str,
        session: Session,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """
        Filter and rank detected books into recommendations.

        Args:
            detected_books: List of books detected from scan
            user_library: User's library books
            user_id: User UUID
            session: Database session

        Returns:
            Tuple of (all_detected_books, recommendations)
        """
        all_books = []
        recommendations = []

        for book in detected_books:
            # Calculate match score
            if settings.LLM_ENABLED:
                try:
                    # Use LLM-based scoring with deterministic sampling
                    match_score, explanation = await RecommendationService.calculate_match_score_llm(
                        book, user_library, user_id
                    )
                    book["match_score"] = match_score
                    book["recommendation_explanation"] = explanation
                except Exception as e:
                    # Fallback to rule-based if LLM fails
                    logger.error(f"Error getting LLM score for book '{book.get('title')}': {str(e)}")
                    match_score = RecommendationService.calculate_match_score_rule_based(
                        book, user_library
                    )
                    book["match_score"] = match_score
                    book["recommendation_explanation"] = "Rule-based recommendation (LLM error)"
            else:
                # Use rule-based scoring
                match_score = RecommendationService.calculate_match_score_rule_based(
                    book, user_library
                )
                book["match_score"] = match_score
                book["recommendation_explanation"] = "Rule-based recommendation"

            # Check if in library
            in_library = RecommendationService.is_book_in_library(
                session, user_id, book.get("google_books_id")
            )
            book["in_library"] = in_library

            all_books.append(book)

            # Only recommend books not in library
            if not in_library:
                recommendations.append(book)

        # Sort recommendations by match score (descending)
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)

        return all_books, recommendations
