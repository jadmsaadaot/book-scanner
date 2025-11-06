"""OpenAI provider for LLM-based recommendations."""

import base64
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

    async def extract_titles_from_image(self, image_bytes: bytes) -> str:
        """
        Extract book titles directly from an image using OpenAI Vision.

        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)

        Returns:
            Raw JSON string response with extracted titles and confidence scores
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")

        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            # Create vision prompt
            prompt = """Analyze this image of a bookshelf or book covers and extract all visible book titles with author names.

For each book you can clearly identify, provide:
1. title: The full book title (as accurately as you can read it)
2. author: The author's name if visible on the cover/spine (null if not visible or unclear)
3. confidence: Score from 0.0 to 1.0 based on how clearly you can read the title

Rules:
- Only include actual book titles you can see in the image
- Extract author names separately in the "author" field - DO NOT include them in the title
- If you can only partially read a title, include what you can see and lower the confidence
- If text is blurry or unclear, give it a lower confidence score (0.3-0.6)
- If text is crystal clear, give it a high confidence score (0.8-1.0)
- Ignore ISBN numbers, prices, barcodes, or other metadata
- Include both horizontal and vertical text (book spines)

CRITICAL: Return ONLY valid JSON - no markdown formatting, no code blocks, no extra text.
Your entire response must be ONLY the JSON array below:
[{
  "title": "The Hobbit",
  "author": "J.R.R. Tolkien",
  "confidence": 0.95
}, {
  "title": "1984",
  "author": "George Orwell",
  "confidence": 0.85
}]

If you cannot identify any book titles with reasonable confidence, return an empty array: []"""

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use vision-capable model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  # High detail for better text recognition
                                }
                            }
                        ]
                    }
                ],
                temperature=0.2,
                max_tokens=2000,  # Support ~30 books (~65 tokens/book)
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI Vision")

            return content.strip()

        except Exception as e:
            raise RuntimeError(f"OpenAI Vision API error: {e}") from e

    async def calculate_batch_match_scores(
        self,
        detected_books: list[dict[str, Any]],
        user_library: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Calculate match scores for multiple books in a single API call.

        Args:
            detected_books: List of book metadata to evaluate
            user_library: User's library books

        Returns:
            List of dicts with keys: title, score, explanation
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")

        if not detected_books:
            return []

        prompt = self._build_batch_recommendation_prompt(detected_books, user_library)

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
                temperature=0.3,
                max_tokens=2000,  # More tokens for multiple books
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

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

            # Extract scores and explanations with title for safe matching
            parsed_results = []
            for result in results:
                title = result.get("title", "")
                score = float(result.get("score", 0.0))
                explanation = result.get("explanation", "No explanation provided")
                # Clamp score to valid range
                score = max(0.0, min(1.0, score))
                parsed_results.append({
                    "title": title,
                    "score": score,
                    "explanation": explanation
                })

            return parsed_results

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from OpenAI: {e}") from e
        except Exception as e:
            raise RuntimeError(f"OpenAI batch API error: {e}") from e
