"""Google Gemini provider for LLM-based recommendations."""

import base64
import json
from typing import Any

import google.generativeai as genai
from PIL import Image
import io

from app.core.config import settings
from app.services.llm.base import LLMProvider


class GoogleProvider(LLMProvider):
    """Google Gemini provider for book recommendations."""

    def __init__(self, model: str = "gemini-2.0-flash-exp") -> None:
        """
        Initialize Google Gemini provider.

        Args:
            model: Gemini model to use (default: gemini-2.0-flash-exp for best cost/performance)
        """
        self.model_name = model
        self.model = None

        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4000,  # Support ~30 books with visual context (~120 tokens/book)
                },
            )

    def is_available(self) -> bool:
        """Check if Google Gemini is configured."""
        return bool(settings.GOOGLE_API_KEY and self.model)

    async def extract_titles(self, prompt: str) -> str:
        """
        Extract book titles from OCR text using Google Gemini.

        Args:
            prompt: Formatted prompt with OCR text and instructions

        Returns:
            Raw JSON string response from LLM
        """
        if not self.model:
            raise RuntimeError("Google Gemini client not initialized. Check API key.")

        try:
            response = await self.model.generate_content_async(prompt)
            content = response.text if response.text else ""

            if not content:
                raise ValueError("Empty response from Google Gemini")

            return content.strip()

        except Exception as e:
            raise RuntimeError(f"Google Gemini API error: {e}") from e

    async def extract_titles_from_image(self, image_bytes: bytes) -> str:
        """
        Extract book titles directly from an image using Google Gemini Vision.

        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)

        Returns:
            Raw JSON string response with extracted titles and confidence scores
        """
        if not self.model:
            raise RuntimeError("Google Gemini client not initialized. Check API key.")

        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes))

            # Create vision prompt with visual context extraction
            prompt = """Analyze this image of a bookshelf or book covers and extract all visible book titles WITH author names and visual context.

For each book you can clearly identify, provide:
1. title: The full book title (as accurately as you can read it)
2. author: The author's name if visible on the cover/spine (null if not visible or unclear)
3. confidence: Score from 0.0 to 1.0 based on how clearly you can read the title
4. visual_context: An object with visual insights about the book:
   - cover_style: Description of the cover art/design (e.g., "Minimalist modern design", "Illustrated fantasy with dragons", "Classic literature leather-bound")
   - apparent_genre: Genre inferred from visual cues (e.g., "Fantasy", "Mystery", "Romance", "Science Fiction", "Non-fiction")
   - target_audience: Target audience inferred from design (e.g., "Young adult", "Children", "Adult literary", "General audience")
   - notable_features: Any distinctive visual elements (e.g., "Award winner badge", "Series volume number", "Well-worn spine indicating frequent reading")

Rules:
- Only include actual book titles you can see in the image
- Extract author names separately in the "author" field - DO NOT include them in the title
- If you can only partially read a title, include what you can see and lower the confidence
- If text is blurry or unclear, give it a lower confidence score (0.3-0.6)
- If text is crystal clear, give it a high confidence score (0.8-1.0)
- Ignore ISBN numbers, prices, barcodes, or other metadata
- Include both horizontal and vertical text (book spines)
- Visual context should be concise (1-5 words per field)
- If you can't determine a visual context field, omit it or set to null

CRITICAL: Return ONLY valid JSON - no markdown formatting, no code blocks, no extra text.
Your entire response must be ONLY the JSON array below:
[{
  "title": "The Hobbit",
  "author": "J.R.R. Tolkien",
  "confidence": 0.95,
  "visual_context": {
    "cover_style": "Illustrated fantasy with dragon artwork",
    "apparent_genre": "Fantasy adventure",
    "target_audience": "Young adult",
    "notable_features": "Leather-bound collector's edition"
  }
}, {
  "title": "1984",
  "author": "George Orwell",
  "confidence": 0.85,
  "visual_context": {
    "cover_style": "Minimalist dystopian design",
    "apparent_genre": "Literary fiction",
    "target_audience": "Adult"
  }
}]

If you cannot identify any book titles with reasonable confidence, return an empty array: []"""

            # Generate content with vision
            response = await self.model.generate_content_async([prompt, image])
            content = response.text if response.text else ""

            if not content:
                raise ValueError("Empty response from Google Gemini Vision")

            return content.strip()

        except Exception as e:
            raise RuntimeError(f"Google Gemini Vision API error: {e}") from e

    async def calculate_book_match_score(
        self,
        detected_book: dict[str, Any],
        user_library: list[dict[str, Any]],
    ) -> tuple[float, str]:
        """
        Calculate book match score using Google Gemini.

        Args:
            detected_book: Book metadata
            user_library: User's library books

        Returns:
            Tuple of (score, explanation)
        """
        if not self.model:
            raise RuntimeError("Google Gemini client not initialized. Check API key.")

        prompt = self._build_recommendation_prompt(detected_book, user_library)

        try:
            response = await self.model.generate_content_async(prompt)

            content = response.text if response.text else ""
            if not content:
                raise ValueError("Empty response from Google Gemini")

            # Parse JSON response
            result = json.loads(content.strip())
            score = float(result.get("score", 0.0))
            explanation = result.get("explanation", "No explanation provided")

            # Clamp score to valid range
            score = max(0.0, min(1.0, score))

            return score, explanation

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Google Gemini: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Google Gemini API error: {e}") from e

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
        if not self.model:
            raise RuntimeError("Google Gemini client not initialized. Check API key.")

        if not detected_books:
            return []

        prompt = self._build_batch_recommendation_prompt(detected_books, user_library)

        try:
            # Use higher max_output_tokens for batch processing
            batch_model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 2000,  # More tokens for multiple books
                },
            )

            response = await batch_model.generate_content_async(prompt)

            content = response.text if response.text else ""
            if not content:
                raise ValueError("Empty response from Google Gemini")

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
            raise ValueError(f"Invalid JSON response from Google Gemini: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Google Gemini batch API error: {e}") from e
