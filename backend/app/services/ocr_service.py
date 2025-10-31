"""OCR service for extracting text from book spine images using Tesseract."""

import io
import re
from typing import Any

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


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
    def extract_text(image_bytes: bytes) -> dict[str, Any]:
        """
        Extract text from image bytes using Tesseract OCR.

        Args:
            image_bytes: Image file bytes

        Returns:
            Dictionary containing extracted text and confidence scores
        """
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes))

            # Preprocess image
            processed_image = OCRService.preprocess_image(image)

            # Extract text with detailed data
            ocr_data = pytesseract.image_to_data(
                processed_image, output_type=pytesseract.Output.DICT
            )

            # Extract text with confidence
            full_text = pytesseract.image_to_string(processed_image)

            # Calculate average confidence
            confidences = [
                int(conf) for conf in ocr_data["conf"] if conf != "-1" and conf != -1
            ]
            avg_confidence = (
                sum(confidences) / len(confidences) if confidences else 0.0
            )

            return {
                "text": full_text.strip(),
                "confidence": avg_confidence,
                "detailed_data": ocr_data,
            }
        except Exception as e:
            return {"text": "", "confidence": 0.0, "error": str(e)}

    @staticmethod
    def extract_book_titles(ocr_result: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Parse OCR text to extract potential book titles.

        Args:
            ocr_result: Result from extract_text method

        Returns:
            List of potential book titles with confidence scores
        """
        text = ocr_result.get("text", "")
        confidence = ocr_result.get("confidence", 0.0)

        if not text:
            return []

        # Split by newlines and filter out empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Basic heuristics to identify potential book titles
        potential_titles = []
        for line in lines:
            # Skip very short lines (likely noise)
            if len(line) < 3:
                continue

            # Skip lines that are mostly numbers
            if sum(c.isdigit() for c in line) / len(line) > 0.5:
                continue

            # Clean the line
            cleaned_title = OCRService._clean_title(line)

            if cleaned_title:
                potential_titles.append(
                    {"title": cleaned_title, "confidence": confidence / 100.0}
                )

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
