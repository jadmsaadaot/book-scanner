# OCR Service Improvements

## Overview

Upgraded the OCR service with intelligent title extraction heuristics, line-level confidence filtering, and modular architecture.

## What Changed

### 1. Line-Level Confidence Tracking

**Before:**
```python
# Used global average confidence for all text
avg_confidence = sum(confidences) / len(confidences)
```

**After:**
```python
# Extract each line with its own confidence score
lines_with_confidence = OCRService._extract_lines_with_confidence(ocr_data)
# Returns: [{"text": "Book Title", "confidence": 94.2}, ...]
```

**Benefits:**
- Filter out low-confidence lines individually (< 50% confidence)
- Keep high-confidence titles even if overall image quality is poor
- More granular quality signal for downstream processing

---

### 2. Smart Title Heuristics

Added `_is_likely_title()` method with multiple filters:

#### ✅ Filters Noise
```python
# Skip publisher/metadata keywords
noise_keywords = ["isbn", "copyright", "edition", "published",
                  "publisher", "press", "books", "price", "pages"]

# Skip numeric content (ISBNs, prices)
numeric_ratio = sum(c.isdigit() for c in text) / len(text)
if numeric_ratio > 0.5:  # More than 50% numbers
    return False

# Skip all-caps multi-word text (e.g., "PENGUIN RANDOM HOUSE")
if len(words) > 1 and text.isupper():
    return False
```

#### ✅ Prefers Title Case
```python
# Count capitalized words
capitalized_words = sum(1 for word in words if word[0].isupper())
title_case_ratio = capitalized_words / len(words)

# Require at least 50% capitalization for multi-word titles
if len(words) > 1 and title_case_ratio < 0.5:
    return False
```

**Filtered Examples:**
- ❌ `"ISBN 978-0-14-311822-4"` → Contains "isbn" keyword
- ❌ `"PENGUIN RANDOM HOUSE"` → All-caps multi-word
- ❌ `"Copyright 2024"` → Contains "copyright"
- ❌ `"$34.99"` → > 50% numeric
- ❌ `"456 pages"` → Contains "pages"
- ❌ `"the catcher in the rye"` → Poor Title Case (< 50% capitalized)

**Accepted Examples:**
- ✅ `"The Lord of the Rings"` → Good Title Case
- ✅ `"Foundation"` → Single word
- ✅ `"DUNE"` → Single-word all-caps (valid book title)

---

### 3. Modular Architecture

**Refactored into focused functions:**

```python
# Separate concerns
_load_and_preprocess_image(bytes) -> Image
_extract_lines_with_confidence(ocr_data) -> list[dict]
_is_likely_title(text) -> bool
_clean_title(text) -> str

# Main pipeline
extract_text(bytes) -> dict
extract_book_titles(ocr_result) -> list[dict]
```

**Benefits:**
- Easier to test individual components
- Can swap OCR engines without changing title logic
- Clear separation of byte handling, OCR, and heuristics

---

### 4. Configurable Constants

```python
MIN_TITLE_LENGTH = 3          # Minimum characters
MAX_TITLE_LENGTH = 200        # Maximum characters
MIN_LINE_CONFIDENCE = 50      # Minimum confidence threshold
NUMERIC_RATIO_THRESHOLD = 0.5 # Max ratio of digits
```

Easy to adjust filtering based on real-world data.

---

## Performance Comparison

### Input: 15 OCR lines from book spine image

**Before (naive filtering):**
- Extracted: ~12 lines
- Included: Publisher names, ISBNs, prices, editions
- Result: Google Books API gets confused by noise

**After (smart heuristics):**
- Extracted: 5 high-quality titles
- Filtered out: 10 noise lines (67% reduction)
- Result: Clean titles → better Google Books matches

---

## Example Output

### OCR Input Lines
```
1. "The Lord of the Rings" (94.2% conf)
2. "Harry Potter and the Chamber of Secrets" (91.8% conf)
3. "Foundation" (89.5% conf)
4. "DUNE" (88.0% conf)
5. "The Great Gatsby" (87.3% conf)
6. "PENGUIN RANDOM HOUSE" (85.0% conf)
7. "ISBN 978-0-14-311822-4" (82.5% conf)
8. "Copyright 2024" (78.0% conf)
9. "Published in New York" (75.2% conf)
10. "$34.99" (70.0% conf)
11. "456 pages" (68.5% conf)
12. "Reprint Edition" (65.0% conf)
13. "A Possible Title" (45.0% conf)
14. "Another Book" (38.5% conf)
15. "the catcher in the rye" (82.0% conf)
```

### Extracted Titles
```json
[
  {"title": "The Lord of the Rings", "confidence": 0.942},
  {"title": "Harry Potter and the Chamber of Secrets", "confidence": 0.918},
  {"title": "Foundation", "confidence": 0.895},
  {"title": "DUNE", "confidence": 0.880},
  {"title": "The Great Gatsby", "confidence": 0.873}
]
```

**Filtered out:** Lines 6-15 (noise, low confidence, poor formatting)

---

## API Changes

### Backward Compatible

The `extract_text()` method now returns an additional field:

```python
{
  "text": "...",           # Full text (unchanged)
  "confidence": 78.5,    # Average confidence (unchanged)
  "lines": [...],        # NEW: Line-level confidence data
  "detailed_data": {...} # Raw OCR data (unchanged)
}
```

The `extract_book_titles()` method automatically uses line-level data if available, falls back to old method if not.

---

## Configuration

Adjust thresholds in [ocr_service.py](app/services/ocr_service.py#L10-L14):

```python
MIN_LINE_CONFIDENCE = 50  # Lower = more permissive (more false positives)
                          # Higher = stricter (may miss valid titles)
```

---

## Future Improvements (Not Implemented)

### Not Needed Yet
- ❌ **Spell correction** - Google Books API already handles OCR errors via fuzzy matching
- ❌ **De-duplication** - Not a problem in current data
- ❌ **Orientation correction** - Wait for real-world rotation issues

### Only If Tesseract Fails
- ❌ **Alternative OCR engines** (EasyOCR, PaddleOCR) - Only if non-English or stylized fonts
- ❌ **Object detection** (YOLO spine cropping) - Overkill for current use case
- ❌ **NLP models** (BERT title classification) - Already have LLM integration

**Approach:** Monitor production OCR failures, implement solutions based on real data.

---

## Testing

Run the test suite:

```bash
python -c "from app.services.ocr_service import OCRService; ..."
```

Or use the comprehensive test in the implementation.

---

## Files Changed

- [app/services/ocr_service.py](app/services/ocr_service.py) - Complete refactor with new heuristics

---

## Credits

Implemented based on analysis of common OCR challenges in book spine detection.
