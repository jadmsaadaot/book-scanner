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
                    "max_output_tokens": 200,
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
