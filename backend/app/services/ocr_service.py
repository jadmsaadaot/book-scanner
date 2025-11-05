"""VLM-based service for extracting book titles from images.

This service uses Vision Language Models (VLMs) instead of traditional OCR (Tesseract)
for better accuracy on book covers and shelf photos.
"""

import io
import json
import logging
import re
import time
from typing import Any

from PIL import Image
from pydantic import BaseModel, Field, validator

from app.core.config import settings

# Enable HEIC/HEIF format support (Apple's image format)
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # pillow-heif not installed

logger = logging.getLogger(__name__)

# Configuration constants
MIN_TITLE_LENGTH = getattr(settings, 'OCR_MIN_TITLE_LENGTH', 2)
MAX_TITLE_LENGTH = getattr(settings, 'OCR_MAX_TITLE_LENGTH', 200)
MIN_CONFIDENCE = 0.3  # Minimum confidence threshold to include a title


def repair_json(json_str: str) -> str:
    """
    Attempt to repair common JSON formatting issues from LLM responses.

    Common issues:
    - Trailing commas in arrays/objects
    - Unterminated strings (truncated responses)
    """
    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

    # If the JSON appears truncated (doesn't end with ] or }), try to close it
    stripped = json_str.rstrip()
    if stripped and not stripped.endswith((']', '}')):
        # Count opening brackets/braces to determine what to close
        open_brackets = stripped.count('[') - stripped.count(']')
        open_braces = stripped.count('{') - stripped.count('}')

        # Close any unterminated strings first
        if stripped.count('"') % 2 != 0:
            json_str = stripped + '"'
            stripped = json_str

        # Close objects and arrays
        json_str = stripped + ('}' * open_braces) + (']' * open_brackets)

    return json_str


class VisualContext(BaseModel):
    """Visual context extracted from book cover/spine."""

    cover_style: str | None = Field(None, description="Description of cover art/design style")
    apparent_genre: str | None = Field(None, description="Genre inferred from visual cues")
    target_audience: str | None = Field(None, description="Target audience inferred from design")
    notable_features: str | None = Field(None, description="Distinctive visual elements")


class ExtractedTitle(BaseModel):
    """Validated VLM output for a single book title."""

    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)
    author: str | None = Field(None, description="Book author name if visible")
    confidence: float = Field(ge=0.0, le=1.0)
    visual_context: VisualContext | None = Field(None, description="Visual context from cover/spine")

    @validator('title')
    def validate_title(cls, v):
        """Validate and clean title."""
        # Remove excessive whitespace
        v = " ".join(v.split())

        # Reject if empty after cleaning
        if not v:
            raise ValueError("Title is empty after cleaning")

        return v

    @validator('author')
    def validate_author(cls, v):
        """Validate and clean author name."""
        if v:
            # Remove excessive whitespace
            v = " ".join(v.split())
            # Return None if empty after cleaning
            return v if v else None
        return v


class VLMTitleExtractionResponse(BaseModel):
    """Validated VLM response for title extraction."""

    titles: list[ExtractedTitle] = Field(
        max_items=getattr(settings, 'OCR_LLM_MAX_TITLES', 30)
    )

    @validator('titles')
    def validate_titles(cls, v):
        """Deduplicate titles by normalized form."""
        seen = set()
        unique = []
        for title in v:
            normalized = title.title.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique.append(title)
        return unique


class OCRService:
    """Service for extracting book titles from images using VLMs."""

    @staticmethod
    async def extract_text(image_bytes: bytes) -> dict[str, Any]:
        """
        Extract text from image bytes using Vision Language Models.

        This is a compatibility wrapper that maintains the old API
        but uses VLM internally.

        Args:
            image_bytes: Image file bytes

        Returns:
            Dictionary containing extracted text, confidence scores, and metadata
        """
        # For backward compatibility, we'll call extract_book_titles
        # and format the response to match the old Tesseract format
        try:
            # Use await since we're in an async context
            titles = await OCRService.extract_book_titles_vlm(image_bytes)

            # Format as text (one title per line)
            text = "\n".join([t["title"] for t in titles])

            # Calculate average confidence
            avg_confidence = (
                sum(t["confidence"] for t in titles) / len(titles) if titles else 0.0
            )

            return {
                "text": text,
                "confidence": avg_confidence * 100.0,  # Return as 0-100
                "lines": [{"text": t["title"], "confidences": t["confidence"] * 100} for t in titles],
                "detailed_data": {"vlm_titles": titles},
                "rotation_angle": 0,  # VLM handles rotation automatically
                "rotation_time_ms": 0,
                "extraction_method": "vlm"
            }

        except Exception as e:
            logger.error(f"VLM extraction failed: {e}", exc_info=True)
            return {
                "text": "",
                "confidence": 0.0,
                "lines": [],
                "error": str(e),
                "extraction_method": "vlm"
            }

    @staticmethod
    async def extract_book_titles_vlm(image_bytes: bytes) -> list[dict[str, Any]]:
        """
        Extract book titles from image using Vision Language Model.

        Automatically falls back to other configured providers if primary fails.

        Args:
            image_bytes: Raw image bytes

        Returns:
            List of extracted titles with confidence scores
        """
        from app.services.llm.factory import extract_titles_with_fallback

        if not settings.LLM_ENABLED:
            logger.warning("LLM is disabled - cannot use VLM extraction")
            return []

        start_time = time.time()

        try:
            # Extract titles using VLM with automatic fallback
            logger.info("Extracting book titles using VLM (with fallback)")
            raw_response = await extract_titles_with_fallback(image_bytes)

            # Parse and validate JSON response
            try:
                # Clean markdown code blocks if present
                response_text = raw_response.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                # Try to parse JSON, with repair attempt on failure
                try:
                    parsed = json.loads(response_text)
                except json.JSONDecodeError:
                    # Attempt to repair common JSON issues
                    logger.warning("Initial JSON parse failed, attempting repair...")
                    repaired = repair_json(response_text)
                    parsed = json.loads(repaired)  # This will raise if repair didn't work

                # Validate with Pydantic
                validated = VLMTitleExtractionResponse(
                    titles=[ExtractedTitle(**item) for item in parsed]
                )

                # Filter by minimum confidence and include author + visual context
                titles = [
                    {
                        "title": t.title,
                        "author": t.author,
                        "confidence": t.confidence,
                        "visual_context": t.visual_context.dict(exclude_none=True) if t.visual_context else None
                    }
                    for t in validated.titles
                    if t.confidence >= MIN_CONFIDENCE
                ]

                extraction_time_ms = (time.time() - start_time) * 1000

                logger.info(
                    f"VLM extraction completed: {len(titles)} titles found, "
                    f"time_ms={extraction_time_ms:.0f}"
                )

                return titles

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"VLM returned invalid JSON, error: {e}")
                logger.error(f"Raw response (first 500 chars): {raw_response[:500]}")
                logger.error(f"Cleaned response (first 500 chars): {response_text[:500]}")
                return []

        except Exception as e:
            logger.error(f"VLM extraction failed: {str(e)}", exc_info=True)
            return []

    @staticmethod
    async def extract_book_titles(
        ocr_result: dict[str, Any],
        use_llm: bool = True,
        llm_strategy: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Extract book titles from OCR result or image.

        This method is maintained for backward compatibility with the old
        Tesseract-based flow. New code should use extract_book_titles_vlm directly.

        Args:
            ocr_result: Result from extract_text method (contains image data)
            use_llm: Always True for VLM (parameter kept for compatibility)
            llm_strategy: Ignored (kept for compatibility)

        Returns:
            List of potential book titles with confidence scores
        """
        # If the OCR result contains VLM titles, return them
        if "detailed_data" in ocr_result and "vlm_titles" in ocr_result["detailed_data"]:
            return ocr_result["detailed_data"]["vlm_titles"]

        # Otherwise, extract from lines if available
        lines = ocr_result.get("lines", [])
        return [
            {"title": line["text"], "confidence": line.get("confidences", 0) / 100.0}
            for line in lines
        ]
