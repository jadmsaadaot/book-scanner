"""Anthropic Claude provider for LLM-based recommendations."""

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
