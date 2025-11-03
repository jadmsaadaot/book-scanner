"""Base class for LLM providers."""

import hashlib
import random
from abc import ABC, abstractmethod
from typing import Any

# Configuration constants for LLM prompts
MAX_DESCRIPTION_LENGTH = 300  # Characters to include from book descriptions
MAX_LIBRARY_BOOKS = 50  # Maximum number of user library books to send to LLM (tokens are cheap!)


def sample_library_books(
    library: list[dict[str, Any]], user_id: str, max_books: int = MAX_LIBRARY_BOOKS
) -> list[dict[str, Any]]:
    """
    Sample books from user's library with deterministic shuffling.

    Uses user_id as seed to ensure consistent sampling per user (cache-friendly).
    Avoids bias from always taking first N books.

    Args:
        library: Full user library
        user_id: User ID for deterministic seeding
        max_books: Maximum number of books to sample

    Returns:
        Sampled list of books (deterministically shuffled)
    """
    if len(library) <= max_books:
        return library

    # Create deterministic seed from user_id
    seed = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)

    # Shuffle with deterministic seed (same user = same shuffle every time)
    shuffled = library.copy()
    rng = random.Random(seed)
    rng.shuffle(shuffled)

    return shuffled[:max_books]


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def calculate_book_match_score(
        self,
        detected_book: dict[str, Any],
        user_library: list[dict[str, Any]],
    ) -> tuple[float, str]:
        """
        Calculate how well a detected book matches user's reading preferences using LLM.

        Args:
            detected_book: Book metadata (title, author, description, categories, etc.)
            user_library: List of books in user's library with metadata

        Returns:
            Tuple of (match_score, explanation)
            - match_score: Float between 0.0 and 1.0
            - explanation: Human-readable explanation of the recommendation
        """
        pass

    @abstractmethod
    async def extract_titles(self, prompt: str) -> str:
        """
        Extract book titles from OCR text using LLM.

        Args:
            prompt: Formatted prompt with OCR text and instructions

        Returns:
            Raw JSON string response from LLM
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is properly configured and available.

        Returns:
            True if provider has API key and is ready to use
        """
        pass

    def _format_book_summary(self, book: dict[str, Any]) -> str:
        """
        Format book metadata into a concise summary for LLM context.

        Args:
            book: Book metadata dictionary

        Returns:
            Formatted string summary
        """
        parts = []

        if title := book.get("title"):
            parts.append(f"Title: {title}")

        if author := book.get("author"):
            parts.append(f"Author: {author}")

        if categories := book.get("categories"):
            parts.append(f"Categories: {categories}")

        if description := book.get("description"):
            # Truncate long descriptions to stay within token limits
            desc = (
                description[:MAX_DESCRIPTION_LENGTH] + "..."
                if len(description) > MAX_DESCRIPTION_LENGTH
                else description
            )
            parts.append(f"Description: {desc}")

        if rating := book.get("average_rating"):
            parts.append(f"Rating: {rating}/5")

        return "\n".join(parts)

    def _build_recommendation_prompt(
        self,
        detected_book: dict[str, Any],
        user_library: list[dict[str, Any]],
    ) -> str:
        """
        Build the prompt for the LLM to analyze book match.

        Args:
            detected_book: Book to evaluate
            user_library: User's library books

        Returns:
            Formatted prompt string
        """
        # Format user's library
        if not user_library:
            library_summary = "User has an empty library (new user)."
        else:
            # Limit number of books to stay within token limits
            recent_books = user_library[:MAX_LIBRARY_BOOKS]
            library_items = [
                f"- {book.get('title', 'Unknown')} by {book.get('author', 'Unknown')}"
                for book in recent_books
            ]
            library_summary = "User's library:\n" + "\n".join(library_items)

            if len(user_library) > MAX_LIBRARY_BOOKS:
                remaining = len(user_library) - MAX_LIBRARY_BOOKS
                library_summary += f"\n... and {remaining} more books"

        # Format detected book
        detected_summary = self._format_book_summary(detected_book)

        prompt = f"""You are a book recommendation expert. Analyze how well a detected book matches a user's reading preferences based on their library.

{library_summary}

Detected book to evaluate:
{detected_summary}

Please provide:
1. A match score from 0.0 to 1.0 (where 1.0 is a perfect match for this reader)
2. A brief explanation (1-2 sentences) of why this book matches or doesn't match their preferences

Consider:
- Genre and category overlap
- Author familiarity
- Thematic similarities
- Writing style patterns
- Reading level and complexity

Respond in this exact JSON format:
{{"score": 0.85, "explanation": "Your explanation here"}}

Important: Only respond with the JSON object, no other text."""

        return prompt
