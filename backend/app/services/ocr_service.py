"""OCR service for extracting text from book spine images using Tesseract."""

import io
import re
from typing import Any

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

# Configuration constants
MIN_TITLE_LENGTH = 3  # Minimum characters for a valid title
MAX_TITLE_LENGTH = 200  # Maximum characters for a valid title
MIN_LINE_CONFIDENCE = 50  # Minimum confidence score (0-100) for a line to be considered
NUMERIC_RATIO_THRESHOLD = 0.5  # Maximum ratio of digits in a title


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
        Extract text from image bytes using Tesseract OCR.

        Args:
            image_bytes: Image file bytes

        Returns:
            Dictionary containing extracted text and confidence scores
        """
        try:
            # Load and preprocess image
            processed_image = OCRService._load_and_preprocess_image(image_bytes)

            # Extract text with detailed data (line-level confidence)
            ocr_data = pytesseract.image_to_data(
                processed_image, output_type=pytesseract.Output.DICT
            )

            # Extract full text for backward compatibility
            full_text = pytesseract.image_to_string(processed_image)

            # Extract lines with their individual confidence scores
            lines_with_confidence = OCRService._extract_lines_with_confidence(
                ocr_data
            )

            # Calculate average confidence from all valid words
            confidences = [
                int(conf) for conf in ocr_data["conf"] if conf != -1 and conf != "-1"
            ]
            avg_confidence = (
                sum(confidences) / len(confidences) if confidences else 0.0
            )

            return {
                "text": full_text.strip(),
                "confidence": avg_confidence,
                "lines": lines_with_confidence,  # New: line-level data
                "detailed_data": ocr_data,
            }
        except Exception as e:
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
    def extract_book_titles(ocr_result: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Parse OCR text to extract potential book titles with improved heuristics.

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
