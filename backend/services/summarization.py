from __future__ import annotations

import time
from typing import List, Tuple

import torch
from transformers import pipeline

from ..utils.logger import get_logger

_SUMMARIZER = None
_LOGGER = get_logger("medintel.services.summarization")


def _get_summarizer():
    global _SUMMARIZER
    if _SUMMARIZER is None:
        device = 0 if torch.cuda.is_available() else -1
        _SUMMARIZER = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=device,
        )
    return _SUMMARIZER


def _chunk_text(text: str, max_chars: int = 3000) -> List[str]:
    """Split long text into chunks that fit the summarizer input limits."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for para in paragraphs:
        if current_len + len(para) + 1 > max_chars and current:
            chunks.append(" ".join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para) + 1
    if current:
        chunks.append(" ".join(current))
    if not chunks:
        chunks = [text.strip()]
    return chunks


def _estimate_confidence(text_len: int, summary_len: int, chunk_count: int) -> float:
    if text_len < 50 or summary_len < 20:
        return 0.4
    ratio = summary_len / max(text_len, 1)
    if 0.05 <= ratio <= 0.3:
        base = 0.85
    elif ratio < 0.05:
        base = 0.65
    else:
        base = 0.75
    if chunk_count > 1:
        base -= 0.05 * min(chunk_count - 1, 3)
    return round(max(0.3, min(0.95, base)), 4)


def summarize_text(text: str, max_length: int = 180, request_id: str | None = None) -> Tuple[str, float]:
    """Summarize input text using a pretrained transformer model."""
    start = time.perf_counter()
    try:
        if not text or not text.strip():
            return "", 0.0
        summarizer = _get_summarizer()
        chunks = _chunk_text(text)
        summaries: list[str] = []
        for chunk in chunks:
            result = summarizer(
                chunk,
                max_length=max_length,
                min_length=40,
                do_sample=False,
            )
            if result and "summary_text" in result[0]:
                summaries.append(result[0]["summary_text"])
        if not summaries:
            return "", 0.0
        if len(summaries) == 1:
            summary = summaries[0]
        else:
            # If multiple chunks, summarize the summaries
            combined = " ".join(summaries)
            final = summarizer(
                combined,
                max_length=max_length,
                min_length=40,
                do_sample=False,
            )
            summary = final[0]["summary_text"] if final else ""
        confidence = _estimate_confidence(len(text), len(summary), len(chunks))
        return summary, confidence
    except Exception:
        _LOGGER.exception("Summarization failed.", extra={"request_id": request_id})
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _LOGGER.info(
            "Summarization completed.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
