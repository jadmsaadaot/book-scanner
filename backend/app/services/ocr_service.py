"""OCR service for extracting text from book spine images using Tesseract."""

import io
import json
import logging
import re
import time
from typing import Any, Optional

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pydantic import BaseModel, Field, validator

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configuration constants (with fallback to old values for compatibility)
MIN_TITLE_LENGTH = getattr(settings, 'OCR_MIN_TITLE_LENGTH', 3)
MAX_TITLE_LENGTH = getattr(settings, 'OCR_MAX_TITLE_LENGTH', 200)
MIN_LINE_CONFIDENCE = 50  # Minimum confidence score (0-100) for a line to be considered
NUMERIC_RATIO_THRESHOLD = getattr(settings, 'OCR_MAX_NUMERIC_RATIO', 0.5)


class ExtractedTitle(BaseModel):
    """Validated LLM output for a single book title."""

    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)
    confidence: float = Field(ge=0.0, le=1.0)

    @validator('title')
    def validate_title(cls, v):
        """Validate and clean title."""
        # Remove excessive whitespace
        v = " ".join(v.split())

        # Reject if empty after cleaning
        if not v:
            raise ValueError("Title is empty after cleaning")

        # Reject if mostly numbers (except special cases like "1984")
        if len(v) > 10:
            numeric_ratio = sum(c.isdigit() for c in v) / len(v)
            if numeric_ratio > NUMERIC_RATIO_THRESHOLD:
                raise ValueError("Title is mostly numeric")

        return v


class LLMTitleExtractionResponse(BaseModel):
    """Validated LLM response for title extraction."""

    titles: list[ExtractedTitle] = Field(
        max_items=getattr(settings, 'OCR_LLM_MAX_TITLES', 20)
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
    """Service for optical character recognition on book images."""

    @staticmethod
    def preprocess_image(image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image object
        """
        # Convert to grayscale
        image = image.convert("L")

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)

        # Resize if too small (OCR works better on larger images)
        width, height = image.size
        if width < 1000 or height < 1000:
            scale_factor = max(1000 / width, 1000 / height)
            new_size = (int(width * scale_factor), int(height * scale_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        return image

    @staticmethod
    def _load_and_preprocess_image(image_bytes: bytes) -> Image.Image:
        """
        Load image from bytes and preprocess it.

        Args:
            image_bytes: Image file bytes

        Returns:
            Preprocessed PIL Image object
        """
        image = Image.open(io.BytesIO(image_bytes))
        return OCRService.preprocess_image(image)

    @staticmethod
    def _detect_rotation_osd(image: Image.Image) -> dict[str, Any]:
        """
        Detect image rotation using Tesseract OSD (Orientation and Script Detection).

        Args:
            image: PIL Image object

        Returns:
            Dictionary with 'angle' (0, 90, 180, 270) and 'confidence' (0-100)
        """
        try:
            osd_data = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
            angle = osd_data.get("rotate", 0)
            confidence = osd_data.get("orientation_conf", 0.0)

            logger.info(f"OSD detected rotation: {angle}°, confidence: {confidence:.2f}")

            return {
                "angle": angle,
                "confidence": confidence / 100.0  # Normalize to 0-1
            }
        except Exception as e:
            logger.warning(f"OSD detection failed: {e}")
            return {"angle": 0, "confidence": 0.0}

    @staticmethod
    def _rotate_image(image: Image.Image, angle: int) -> Image.Image:
        """
        Rotate image by specified angle.

        Args:
            image: PIL Image object
            angle: Rotation angle in degrees (0, 90, 180, 270)

        Returns:
            Rotated PIL Image object
        """
        if angle == 0:
            return image

        # PIL rotates counter-clockwise, so we need to negate for clockwise rotation
        return image.rotate(-angle, expand=True)

    @staticmethod
    def _try_rotation_fallback(
        image: Image.Image,
        initial_confidence: float
    ) -> tuple[Image.Image, int, float]:
        """
        Try fallback rotations (90° and 270°) if initial OCR confidence is low.

        Default order [90°, 270°] prioritizes North American book spine orientation:
        - 90° CW = top-to-bottom text (standard in US/Canada)
        - 270° CCW = bottom-to-top text (imports or edge cases)

        Args:
            image: PIL Image object
            initial_confidence: Initial OCR confidence (0-1)

        Returns:
            Tuple of (best_image, best_angle, best_confidence)
        """
        rotation_mode = getattr(settings, 'OCR_ROTATION_MODE', 'osd_fallback')
        fallback_angles = getattr(settings, 'OCR_ROTATION_FALLBACK_ANGLES', [90, 270])

        if rotation_mode != 'osd_fallback':
            return image, 0, initial_confidence

        logger.info(f"Trying fallback rotations: {fallback_angles}")

        best_image = image
        best_angle = 0
        best_confidence = initial_confidence

        for angle in fallback_angles:
            try:
                rotated = OCRService._rotate_image(image, angle)

                # Run quick OCR to get confidence
                ocr_data = pytesseract.image_to_data(
                    rotated, output_type=pytesseract.Output.DICT
                )

                # Calculate average confidence
                confidences = [
                    int(conf) for conf in ocr_data["conf"]
                    if conf != -1 and conf != "-1"
                ]
                avg_confidence = (
                    sum(confidences) / len(confidences) if confidences else 0.0
                ) / 100.0  # Normalize to 0-1

                logger.info(f"Rotation {angle}°: confidence={avg_confidence:.2f}")

                if avg_confidence > best_confidence:
                    best_image = rotated
                    best_angle = angle
                    best_confidence = avg_confidence

            except Exception as e:
                logger.warning(f"Fallback rotation {angle}° failed: {e}")

        logger.info(f"Best rotation: {best_angle}°, confidence: {best_confidence:.2f}")
        return best_image, best_angle, best_confidence

    @staticmethod
    def _extract_lines_with_confidence(
        ocr_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Extract text lines with their confidence scores from OCR data.

        Args:
            ocr_data: Raw OCR data from pytesseract.image_to_data

        Returns:
            List of dicts with 'text' and 'confidence' for each line
        """
        lines = []
        current_line = []
        current_line_num = -1
        current_confidences = []

        for i, text in enumerate(ocr_data["text"]):
            line_num = ocr_data["line_num"][i]
            conf = ocr_data["conf"][i]

            # Skip empty text or invalid confidence
            if not text.strip() or conf == -1:
                continue

            # New line detected
            if line_num != current_line_num:
                # Save previous line if it exists
                if current_line:
                    line_text = " ".join(current_line)
                    avg_conf = (
                        sum(current_confidences) / len(current_confidences)
                        if current_confidences
                        else 0
                    )
                    lines.append({"text": line_text, "confidence": avg_conf})

                # Start new line
                current_line = [text]
                current_confidences = [conf]
                current_line_num = line_num
            else:
                # Continue current line
                current_line.append(text)
                current_confidences.append(conf)

        # Don't forget the last line
        if current_line:
            line_text = " ".join(current_line)
            avg_conf = (
                sum(current_confidences) / len(current_confidences)
                if current_confidences
                else 0
            )
            lines.append({"text": line_text, "confidence": avg_conf})

        return lines

    @staticmethod
    def extract_text(image_bytes: bytes) -> dict[str, Any]:
        """
        Extract text from image bytes using Tesseract OCR with rotation detection.

        Args:
            image_bytes: Image file bytes

        Returns:
            Dictionary containing extracted text, confidence scores, and rotation info
        """
        try:
            rotation_start = time.time()
            rotation_mode = getattr(settings, 'OCR_ROTATION_MODE', 'osd_fallback')

            # Load and preprocess image
            processed_image = OCRService._load_and_preprocess_image(image_bytes)

            # Phase 1: Rotation detection (if enabled)
            rotation_angle = 0
            rotation_confidence = 1.0

            if rotation_mode in ('osd_only', 'osd_fallback'):
                osd_result = OCRService._detect_rotation_osd(processed_image)
                rotation_angle = osd_result["angle"]
                rotation_confidence = osd_result["confidence"]

                # Rotate image if needed
                if rotation_angle != 0:
                    processed_image = OCRService._rotate_image(processed_image, rotation_angle)
                    logger.info(f"Rotated image by {rotation_angle}° (OSD confidence: {rotation_confidence:.2f})")

            # Phase 2: Initial OCR
            ocr_data = pytesseract.image_to_data(
                processed_image, output_type=pytesseract.Output.DICT
            )
            full_text = pytesseract.image_to_string(processed_image)
            lines_with_confidence = OCRService._extract_lines_with_confidence(ocr_data)

            # Calculate average confidence from all valid words
            confidences = [
                int(conf) for conf in ocr_data["conf"] if conf != -1 and conf != "-1"
            ]
            avg_confidence = (
                sum(confidences) / len(confidences) if confidences else 0.0
            ) / 100.0  # Normalize to 0-1

            # Phase 3: Fallback rotation (if needed and enabled)
            rotation_threshold = getattr(settings, 'OCR_ROTATION_CONFIDENCE_THRESHOLD', 0.7)

            if rotation_mode == 'osd_fallback' and avg_confidence < rotation_threshold:
                logger.info(f"OCR confidence {avg_confidence:.2f} below threshold {rotation_threshold}, trying fallback rotations")

                best_image, best_angle, best_confidence = OCRService._try_rotation_fallback(
                    processed_image, avg_confidence
                )

                # If fallback found a better result, use it
                if best_confidence > avg_confidence:
                    processed_image = best_image
                    rotation_angle = (rotation_angle + best_angle) % 360
                    avg_confidence = best_confidence

                    # Re-run OCR on best rotation
                    ocr_data = pytesseract.image_to_data(
                        processed_image, output_type=pytesseract.Output.DICT
                    )
                    full_text = pytesseract.image_to_string(processed_image)
                    lines_with_confidence = OCRService._extract_lines_with_confidence(ocr_data)

                    logger.info(f"Using fallback rotation: total_angle={rotation_angle}°, confidence={avg_confidence:.2f}")

            rotation_time_ms = (time.time() - rotation_start) * 1000

            # Log rotation metrics
            logger.info(
                f"OCR completed: rotation_mode={rotation_mode}, "
                f"final_angle={rotation_angle}°, confidence={avg_confidence:.2f}, "
                f"rotation_time_ms={rotation_time_ms:.0f}"
            )

            return {
                "text": full_text.strip(),
                "confidence": avg_confidence * 100.0,  # Return as 0-100 for backward compatibility
                "lines": lines_with_confidence,
                "detailed_data": ocr_data,
                "rotation_angle": rotation_angle,
                "rotation_mode": rotation_mode,
                "rotation_time_ms": rotation_time_ms,
            }
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}", exc_info=True)
            return {"text": "", "confidence": 0.0, "lines": [], "error": str(e)}

    @staticmethod
    def _is_likely_title(text: str) -> bool:
        """
        Determine if a text line is likely a book title using heuristics.

        Args:
            text: Text line to evaluate

        Returns:
            True if likely a book title, False otherwise
        """
        # Filter out too short or too long
        if len(text) < MIN_TITLE_LENGTH or len(text) > MAX_TITLE_LENGTH:
            return False

        # Skip if mostly numbers (ISBNs, prices, etc.)
        # But allow short numeric titles like "1984"
        if len(text) > 0:
            numeric_ratio = sum(c.isdigit() for c in text) / len(text)
            # Allow fully numeric if short (like "1984"), otherwise check ratio
            if len(text) > 10 and numeric_ratio > NUMERIC_RATIO_THRESHOLD:
                return False

        # Skip common publisher/metadata keywords
        noise_keywords = [
            "isbn",
            "copyright",
            "edition",
            "published",
            "publisher",
            "press",
            "books",
            "library",
            "printed",
            "reserved",
            "rights",
            "price",
            "pages",
        ]
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in noise_keywords):
            return False

        return True

    @staticmethod
    async def extract_book_titles(
        ocr_result: dict[str, Any],
        use_llm: bool = True,
        llm_strategy: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Parse OCR text to extract potential book titles with hybrid rule-based + LLM approach.

        Args:
            ocr_result: Result from extract_text method
            use_llm: Enable LLM fallback (default: True)
            llm_strategy: Override OCR_LLM_STRATEGY setting
                - conservative: LLM only when rules extract 0 titles
                - aggressive: LLM refines all low-confidence results
                - disabled: Rules only (no LLM)

        Returns:
            List of potential book titles with confidence scores
        """
        # Determine strategy
        strategy = llm_strategy or getattr(settings, 'OCR_LLM_STRATEGY', 'conservative')

        # Phase 1: Try rule-based extraction
        start_time = time.time()
        rule_based_titles = OCRService._extract_titles_rule_based(ocr_result)
        rule_time_ms = (time.time() - start_time) * 1000

        # Calculate metrics for decision making
        avg_confidence = (
            sum(t["confidence"] for t in rule_based_titles) / len(rule_based_titles)
            if rule_based_titles else 0.0
        )

        # Decision logic based on strategy
        should_use_llm = False
        reason = None

        if not use_llm or not settings.LLM_ENABLED:
            should_use_llm = False
            reason = "LLM disabled"
        elif strategy == "disabled":
            should_use_llm = False
            reason = "Strategy: disabled"
        elif strategy == "conservative":
            if len(rule_based_titles) == 0:
                should_use_llm = True
                reason = "No titles extracted by rules"
        elif strategy == "aggressive":
            llm_threshold = getattr(settings, 'OCR_LLM_CONFIDENCE_THRESHOLD', 0.7)
            if len(rule_based_titles) == 0 or avg_confidence < llm_threshold:
                should_use_llm = True
                reason = f"Low confidence: {avg_confidence:.2f}"

        # Log decision metrics
        logger.info(
            f"Title extraction decision: rule_titles={len(rule_based_titles)}, "
            f"avg_confidence={avg_confidence:.2f}, use_llm={should_use_llm}, "
            f"reason={reason}"
        )

        if should_use_llm:
            try:
                llm_start = time.time()
                llm_titles = await OCRService._extract_titles_llm(
                    ocr_result,
                    fallback_titles=rule_based_titles
                )
                llm_time_ms = (time.time() - llm_start) * 1000

                # Log comparison metrics
                logger.info(
                    f"LLM extraction: input_titles={len(rule_based_titles)}, "
                    f"output_titles={len(llm_titles)}, "
                    f"improvement={len(llm_titles) - len(rule_based_titles)}, "
                    f"time_ms={llm_time_ms:.0f}"
                )

                return llm_titles if llm_titles else rule_based_titles
            except Exception as e:
                logger.warning(f"LLM extraction failed, using rules: {e}")
                return rule_based_titles

        return rule_based_titles

    @staticmethod
    def _extract_titles_rule_based(ocr_result: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract book titles using rule-based heuristics only.

        Args:
            ocr_result: Result from extract_text method

        Returns:
            List of potential book titles with confidence scores
        """
        lines_with_conf = ocr_result.get("lines", [])

        # Fallback to old method if no line-level data
        if not lines_with_conf:
            text = ocr_result.get("text", "")
            confidence = ocr_result.get("confidence", 0.0)

            if not text:
                return []

            lines_with_conf = [
                {"text": line.strip(), "confidence": confidence}
                for line in text.split("\n")
                if line.strip()
            ]

        # Extract titles using heuristics
        potential_titles = []
        for line_data in lines_with_conf:
            text = line_data["text"]
            confidence = line_data["confidence"]

            # Skip low-confidence lines
            if confidence < MIN_LINE_CONFIDENCE:
                continue

            # Apply title heuristics
            if not OCRService._is_likely_title(text):
                continue

            # Clean the title
            cleaned_title = OCRService._clean_title(text)

            if cleaned_title:
                potential_titles.append(
                    {
                        "title": cleaned_title,
                        "confidence": confidence / 100.0,  # Normalize to 0-1
                    }
                )

        # Sort by confidence (highest first)
        potential_titles.sort(key=lambda x: x["confidence"], reverse=True)

        return potential_titles

    @staticmethod
    async def _extract_titles_llm(
        ocr_result: dict[str, Any],
        fallback_titles: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Extract book titles using LLM with strict validation.

        Args:
            ocr_result: OCR output
            fallback_titles: Rule-based titles for context

        Returns:
            List of validated titles
        """
        from app.services.llm.factory import get_llm_provider

        ocr_text = ocr_result.get("text", "")

        # Prepare context for LLM
        context = ""
        if fallback_titles:
            context = f"\nRule-based extraction found {len(fallback_titles)} candidates:\n"
            context += "\n".join([f"- {t['title']}" for t in fallback_titles[:5]])

        prompt = f"""Extract book titles from this OCR text from a bookshelf photo.

OCR Text:
{ocr_text[:2000]}
{context}

Rules:
- Return ONLY actual book titles (not authors, publishers, ISBNs, prices)
- Include confidence 0.0-1.0 for each (based on OCR quality & title likelihood)
- Ignore metadata like "Chapter 1", "Page 50", "ISBN: ..."
- Include short titles like "1984" but skip "Chapter 1984"
- Deduplicate similar titles

Return JSON array ONLY (no explanation):
[{{"title": "Book Title", "confidence": 0.95}}]
"""

        try:
            provider = get_llm_provider()

            # Get raw LLM response
            raw_response = await provider.extract_titles(prompt)

            # Parse and validate
            try:
                parsed = json.loads(raw_response)

                # Validate with Pydantic
                validated = LLMTitleExtractionResponse(
                    titles=[ExtractedTitle(**item) for item in parsed]
                )

                # Convert to internal format
                titles = [
                    {"title": t.title, "confidence": t.confidence}
                    for t in validated.titles
                ]

                return titles

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"LLM returned invalid JSON: {raw_response[:200]}, error: {e}")
                return fallback_titles

        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}", exc_info=True)
            return fallback_titles

    @staticmethod
    def _clean_title(title: str) -> str:
        """
        Clean extracted title by removing special characters and extra whitespace.

        Args:
            title: Raw title string

        Returns:
            Cleaned title string
        """
        # Remove special characters except common punctuation
        title = re.sub(r"[^\w\s\-:',.]", " ", title)

        # Remove extra whitespace
        title = " ".join(title.split())

        return title.strip()
