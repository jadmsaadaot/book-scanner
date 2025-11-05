"""Anthropic Claude provider for LLM-based recommendations."""

import base64
import json
from typing import Any

from anthropic import AsyncAnthropic

from app.core.config import settings
from app.services.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider for book recommendations."""

    def __init__(self, model: str = "claude-3-5-haiku-20241022") -> None:
        """
        Initialize Anthropic provider.

        Args:
            model: Claude model to use (default: claude-3-5-haiku for cost efficiency)
        """
        self.model = model
        self.client = (
            AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            if settings.ANTHROPIC_API_KEY
            else None
        )

    def is_available(self) -> bool:
        """Check if Anthropic is configured."""
        return bool(settings.ANTHROPIC_API_KEY and self.client)

    async def extract_titles(self, prompt: str) -> str:
        """
        Extract book titles from OCR text using Claude.

        Args:
            prompt: Formatted prompt with OCR text and instructions

        Returns:
            Raw JSON string response from LLM
        """
        if not self.client:
            raise RuntimeError("Anthropic client not initialized. Check API key.")

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text if response.content else ""
            if not content:
                raise ValueError("Empty response from Anthropic")

            return content.strip()

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}") from e

    async def extract_titles_from_image(self, image_bytes: bytes) -> str:
        """
        Extract book titles directly from an image using Claude Vision.

        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)

        Returns:
            Raw JSON string response with extracted titles and confidence scores
        """
        if not self.client:
            raise RuntimeError("Anthropic client not initialized. Check API key.")

        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            # Detect image type (default to jpeg if unsure)
            image_media_type = "image/jpeg"
            if image_bytes.startswith(b'\x89PNG'):
                image_media_type = "image/png"
            elif image_bytes.startswith(b'GIF'):
                image_media_type = "image/gif"
            elif image_bytes.startswith(b'WEBP'):
                image_media_type = "image/webp"

            # Create vision prompt
            prompt = """Analyze this image of a bookshelf or book covers and extract all visible book titles.

For each book you can clearly identify, provide:
1. The full title (as accurately as you can read it)
2. A confidence score from 0.0 to 1.0 based on how clearly you can read the title

Rules:
- Only include actual book titles you can see in the image
- DO NOT include author names, publisher names, or other text
- If you can only partially read a title, include what you can see and lower the confidence
- If text is blurry or unclear, give it a lower confidence score (0.3-0.6)
- If text is crystal clear, give it a high confidence score (0.8-1.0)
- Ignore ISBN numbers, prices, barcodes, or other metadata
- Include both horizontal and vertical text (book spines)

Return ONLY a JSON array with this exact format (no other text):
[{"title": "Book Title Here", "confidence": 0.95}, {"title": "Another Book", "confidence": 0.80}]

If you cannot identify any book titles with reasonable confidence, return an empty array: []"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.2,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": image_media_type,
                                    "data": base64_image,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            content = response.content[0].text if response.content else ""
            if not content:
                raise ValueError("Empty response from Claude Vision")

            return content.strip()

        except Exception as e:
            raise RuntimeError(f"Claude Vision API error: {e}") from e

    async def calculate_book_match_score(
        self,
        detected_book: dict[str, Any],
        user_library: list[dict[str, Any]],
    ) -> tuple[float, str]:
        """
        Calculate book match score using Claude.

        Args:
            detected_book: Book metadata
            user_library: User's library books

        Returns:
            Tuple of (score, explanation)
        """
        if not self.client:
            raise RuntimeError("Anthropic client not initialized. Check API key.")

        prompt = self._build_recommendation_prompt(detected_book, user_library)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.3,  # Lower temperature for more consistent scoring
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text if response.content else ""
            if not content:
                raise ValueError("Empty response from Anthropic")

            # Parse JSON response
            result = json.loads(content.strip())
            score = float(result.get("score", 0.0))
            explanation = result.get("explanation", "No explanation provided")

            # Clamp score to valid range
            score = max(0.0, min(1.0, score))

            return score, explanation

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Anthropic: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}") from e

    async def calculate_batch_match_scores(
        self,
        detected_books: list[dict[str, Any]],
        user_library: list[dict[str, Any]],
    ) -> list[tuple[float, str]]:
        """
        Calculate match scores for multiple books in a single API call.

        Args:
            detected_books: List of book metadata to evaluate
            user_library: User's library books

        Returns:
            List of tuples (score, explanation) in the same order as detected_books
        """
        if not self.client:
            raise RuntimeError("Anthropic client not initialized. Check API key.")

        if not detected_books:
            return []

        prompt = self._build_batch_recommendation_prompt(detected_books, user_library)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,  # More tokens for multiple books
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text if response.content else ""
            if not content:
                raise ValueError("Empty response from Anthropic")

            # Clean markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Parse JSON response
            results = json.loads(content)

            if not isinstance(results, list):
                raise ValueError("Expected JSON array response")

            if len(results) != len(detected_books):
                raise ValueError(
                    f"Expected {len(detected_books)} results, got {len(results)}"
                )

            # Extract scores and explanations
            parsed_results = []
            for result in results:
                score = float(result.get("score", 0.0))
                explanation = result.get("explanation", "No explanation provided")
                # Clamp score to valid range
                score = max(0.0, min(1.0, score))
                parsed_results.append((score, explanation))

            return parsed_results

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Anthropic: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Anthropic batch API error: {e}") from e
