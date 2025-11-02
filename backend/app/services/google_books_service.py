"""Google Books API service for book metadata retrieval."""

import json
import logging
from typing import Any

import httpx
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)


class GoogleBooksService:
    """Service for interacting with Google Books API."""

    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    @staticmethod
    async def search_book(
        query: str, max_results: int = 5
    ) -> list[dict[str, Any]]:
        """
        Search for books using Google Books API.

        Args:
            query: Search query (title, author, ISBN, etc.)
            max_results: Maximum number of results to return

        Returns:
            List of book metadata dictionaries
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {"q": query, "maxResults": max_results}
                response = await client.get(
                    GoogleBooksService.BASE_URL, params=params, timeout=10.0
                )
                response.raise_for_status()

                data = response.json()
                items = data.get("items", [])

                books = []
                for item in items:
                    book_data = GoogleBooksService._parse_book_item(item)
                    if book_data:
                        books.append(book_data)

                return books
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Google Books API HTTP error for query '{query}': {e.response.status_code} - {e.response.text}"
            )
            return []
        except httpx.TimeoutException:
            logger.error(f"Google Books API timeout for query '{query}'")
            return []
        except httpx.RequestError as e:
            logger.error(f"Google Books API request error for query '{query}': {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in search_book for query '{query}': {str(e)}")
            return []

    @staticmethod
    async def get_book_by_id(google_books_id: str) -> dict[str, Any] | None:
        """
        Get book details by Google Books ID.

        Args:
            google_books_id: Google Books volume ID

        Returns:
            Book metadata dictionary or None
        """
        try:
            async with httpx.AsyncClient() as client:
                url = f"{GoogleBooksService.BASE_URL}/{google_books_id}"
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()

                data = response.json()
                return GoogleBooksService._parse_book_item(data)
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Google Books API HTTP error for ID '{google_books_id}': {e.response.status_code}"
            )
            return None
        except httpx.TimeoutException:
            logger.error(f"Google Books API timeout for ID '{google_books_id}'")
            return None
        except httpx.RequestError as e:
            logger.error(f"Google Books API request error for ID '{google_books_id}': {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_book_by_id for ID '{google_books_id}': {str(e)}")
            return None

    @staticmethod
    def _parse_book_item(item: dict[str, Any]) -> dict[str, Any] | None:
        """
        Parse Google Books API item into our book format.

        Args:
            item: Raw item from Google Books API

        Returns:
            Parsed book data dictionary
        """
        try:
            volume_info = item.get("volumeInfo", {})

            # Get ISBN (prefer ISBN_13 over ISBN_10)
            isbn = None
            identifiers = volume_info.get("industryIdentifiers", [])
            for identifier in identifiers:
                if identifier.get("type") == "ISBN_13":
                    isbn = identifier.get("identifier")
                    break
            if not isbn:
                for identifier in identifiers:
                    if identifier.get("type") == "ISBN_10":
                        isbn = identifier.get("identifier")
                        break

            # Get thumbnail URL
            image_links = volume_info.get("imageLinks", {})
            thumbnail_url = image_links.get("thumbnail") or image_links.get(
                "smallThumbnail"
            )

            # Get authors
            authors = volume_info.get("authors", [])
            author = ", ".join(authors) if authors else None

            # Get categories
            categories = volume_info.get("categories", [])
            categories_str = json.dumps(categories) if categories else None

            return {
                "title": volume_info.get("title", "Unknown"),
                "author": author,
                "isbn": isbn,
                "publisher": volume_info.get("publisher"),
                "published_date": volume_info.get("publishedDate"),
                "description": volume_info.get("description"),
                "page_count": volume_info.get("pageCount"),
                "categories": categories_str,
                "thumbnail_url": thumbnail_url,
                "google_books_id": item.get("id"),
                "average_rating": volume_info.get("averageRating"),
                "ratings_count": volume_info.get("ratingsCount"),
            }
        except KeyError as e:
            logger.warning(f"Missing required field in book item: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing book item: {str(e)}")
            return None

    @staticmethod
    async def fuzzy_search_book(
        title: str, author: str | None = None, threshold: int = 70
    ) -> dict[str, Any] | None:
        """
        Search for a book with fuzzy matching to handle OCR errors.

        Args:
            title: Book title (may contain OCR errors)
            author: Book author (optional)
            threshold: Minimum fuzzy match score (0-100)

        Returns:
            Best matching book or None
        """
        # Build query
        query = title
        if author:
            query = f"{title} {author}"

        # Search Google Books
        results = await GoogleBooksService.search_book(query, max_results=10)

        if not results:
            return None

        # Find best match using fuzzy matching
        best_match = None
        best_score = 0

        for book in results:
            # Calculate title similarity
            title_score = fuzz.token_sort_ratio(
                title.lower(), book.get("title", "").lower()
            )

            # If author provided, factor it into the score
            if author and book.get("author"):
                author_score = fuzz.token_sort_ratio(
                    author.lower(), book.get("author", "").lower()
                )
                # Weighted average: title 70%, author 30%
                combined_score = int(title_score * 0.7 + author_score * 0.3)
            else:
                combined_score = title_score

            if combined_score > best_score and combined_score >= threshold:
                best_score = combined_score
                best_match = book
                best_match["match_score"] = combined_score / 100.0

        return best_match
