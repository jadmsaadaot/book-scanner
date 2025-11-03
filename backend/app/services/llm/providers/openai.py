"""OpenAI provider for LLM-based recommendations."""

import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.services.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider for book recommendations."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        """
        Initialize OpenAI provider.

        Args:
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
        """
        self.model = model
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return bool(settings.OPENAI_API_KEY and self.client)

    async def extract_titles(self, prompt: str) -> str:
        """
        Extract book titles from OCR text using OpenAI GPT.

        Args:
            prompt: Formatted prompt with OCR text and instructions

        Returns:
            Raw JSON string response from LLM
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a book title extraction expert. Respond only with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            return content.strip()

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}") from e

    async def calculate_book_match_score(
        self,
        detected_book: dict[str, Any],
        user_library: list[dict[str, Any]],
    ) -> tuple[float, str]:
        """
        Calculate book match score using OpenAI GPT.

        Args:
            detected_book: Book metadata
            user_library: User's library books

        Returns:
            Tuple of (score, explanation)
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")

        prompt = self._build_recommendation_prompt(detected_book, user_library)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a book recommendation expert. Respond only with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent scoring
                max_tokens=200,  # Keep responses concise
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            # Parse JSON response
            result = json.loads(content.strip())
            score = float(result.get("score", 0.0))
            explanation = result.get("explanation", "No explanation provided")

            # Clamp score to valid range
            score = max(0.0, min(1.0, score))

            return score, explanation

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from OpenAI: {e}") from e
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}") from e
