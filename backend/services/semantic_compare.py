from __future__ import annotations

import difflib
import re
import time
from typing import Dict, List

import torch
from sentence_transformers import SentenceTransformer, util

from ..utils.logger import get_logger

_MODEL = None
_LOGGER = get_logger("medintel.services.semantic_compare")


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _MODEL


def _split_sections(text: str) -> List[str]:
    cleaned = text.strip()
    if not cleaned:
        return []
    # Prefer paragraph-level splits, fallback to sentence-level splits
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    if len(paragraphs) >= 2:
        return paragraphs
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
    return sentences if sentences else [cleaned]


def _diff_summary(text_a: str, text_b: str, max_lines: int = 200) -> str:
    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()
    diff_lines = list(
        difflib.unified_diff(lines_a, lines_b, fromfile="doc_a", tofile="doc_b", lineterm="")
    )
    if len(diff_lines) > max_lines:
        diff_lines = diff_lines[:max_lines] + ["...diff truncated..."]
    return "\n".join(diff_lines)


def _build_changed_sections(
    sections_a: List[str],
    sections_b: List[str],
    sims: torch.Tensor,
    threshold: float,
    max_sections: int,
) -> List[Dict]:
    changed: List[Dict] = []
    if sections_a and sections_b:
        for idx, section in enumerate(sections_a):
            best_idx = int(torch.argmax(sims[idx]).item())
            best_sim = float(sims[idx][best_idx].item())
            if best_sim < threshold:
                changed.append(
                    {
                        "side": "a",
                        "text": section,
                        "best_match": sections_b[best_idx],
                        "similarity": round(best_sim, 4),
                    }
                )
        for idx, section in enumerate(sections_b):
            best_idx = int(torch.argmax(sims[:, idx]).item())
            best_sim = float(sims[best_idx][idx].item())
            if best_sim < threshold:
                changed.append(
                    {
                        "side": "b",
                        "text": section,
                        "best_match": sections_a[best_idx],
                        "similarity": round(best_sim, 4),
                    }
                )
    else:
        for section in sections_a:
            changed.append(
                {"side": "a", "text": section, "best_match": "", "similarity": 0.0}
            )
        for section in sections_b:
            changed.append(
                {"side": "b", "text": section, "best_match": "", "similarity": 0.0}
            )

    changed.sort(key=lambda item: item["similarity"])
    return changed[:max_sections]


def _estimate_confidence(similarity: float, len_a: int, len_b: int) -> float:
    min_len = min(len_a, len_b)
    if min_len < 50:
        return 0.4
    return round(min(1.0, 0.5 + 0.5 * similarity), 4)


def compare_documents(
    text_a: str,
    text_b: str,
    threshold: float = 0.75,
    max_sections: int = 6,
    request_id: str | None = None,
) -> Dict:
    """Compare two documents using sentence embeddings and a basic diff."""
    start = time.perf_counter()
    try:
        if not text_a.strip() or not text_b.strip():
            return {
                "similarity_score": 0.0,
                "diff_summary": _diff_summary(text_a, text_b),
                "changed_sections": [],
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "confidence": 0.0,
                "explanation": "One or both documents were empty; no semantic comparison performed.",
            }

        model = _get_model()

        doc_embeddings = model.encode(
            [text_a, text_b], convert_to_tensor=True, normalize_embeddings=True
        )
        similarity_score = float(util.cos_sim(doc_embeddings[0], doc_embeddings[1]).item())

        sections_a = _split_sections(text_a)
        sections_b = _split_sections(text_b)

        if sections_a and sections_b:
            emb_a = model.encode(sections_a, convert_to_tensor=True, normalize_embeddings=True)
            emb_b = model.encode(sections_b, convert_to_tensor=True, normalize_embeddings=True)
            sims = util.cos_sim(emb_a, emb_b)
            changed_sections = _build_changed_sections(
                sections_a, sections_b, sims, threshold, max_sections
            )
        else:
            changed_sections = _build_changed_sections(
                sections_a, sections_b, torch.empty(0), threshold, max_sections
            )

        confidence = _estimate_confidence(similarity_score, len(text_a), len(text_b))
        if changed_sections:
            parts: List[str] = []
            for section in changed_sections[:3]:
                snippet = section["text"].replace("\n", " ").strip()
                if len(snippet) > 140:
                    snippet = snippet[:137] + "..."
                parts.append(
                    f"[{section['side']}] \"{snippet}\" (sim {section['similarity']})"
                )
            explanation = "Low-similarity sections: " + "; ".join(parts)
        else:
            explanation = "No low-similarity sections detected."

        return {
            "similarity_score": round(similarity_score, 4),
            "diff_summary": _diff_summary(text_a, text_b),
            "changed_sections": changed_sections,
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "confidence": confidence,
            "explanation": explanation,
        }
    except Exception:
        _LOGGER.exception("Semantic comparison failed.", extra={"request_id": request_id})
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _LOGGER.info(
            "Semantic comparison completed.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
