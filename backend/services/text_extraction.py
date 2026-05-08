from __future__ import annotations

from pathlib import Path
import time

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from ..utils.logger import get_logger

_LOGGER = get_logger("medintel.services.text_extraction")

def _extract_text_from_pdf(path: Path) -> str:
    """Extract text from a PDF, falling back to OCR when needed."""
    text_chunks: list[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text_chunks.append(page_text)

    combined_text = "\n".join(text_chunks).strip()
    if len(combined_text) >= 100:
        return combined_text

    # Fallback to OCR for scanned PDFs
    ocr_chunks: list[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_chunks.append(pytesseract.image_to_string(img))
    return "\n".join(ocr_chunks).strip()


def _extract_text_from_txt(path: Path) -> str:
    """Read text from a UTF-8 text file."""
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def extract_text_from_file(path: Path, request_id: str | None = None) -> str:
    """Extract text from supported files (PDF, TXT)."""
    start = time.perf_counter()
    try:
        ext = path.suffix.lower()
        if ext == ".pdf":
            return _extract_text_from_pdf(path)
        if ext == ".txt":
            return _extract_text_from_txt(path)
        raise ValueError(f"Unsupported file type: {ext}")
    except Exception:
        _LOGGER.exception("Text extraction failed.", extra={"request_id": request_id})
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _LOGGER.info(
            "Text extraction completed.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
