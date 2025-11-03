"""Google Gemini provider for LLM-based recommendations."""

import json
from typing import Any

import google.generativeai as genai

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
