from __future__ import annotations

import os
import re
import time
from typing import Dict, List

from transformers import pipeline

from ..utils.logger import get_logger

LABELS = ["death", "disability", "hospitalization", "other"]

SEVERITY_MAP = {
    "death": "CRITICAL",
    "disability": "HIGH",
    "hospitalization": "HIGH",
    "other": "LOW",
}

_CLASSIFIER = None
_LOGGER = get_logger("medintel.services.classifier")

_KEYWORDS = {
    "death": [
        "death",
        "died",
        "deceased",
        "fatal",
        "mortality",
        "expired",
    ],
    "disability": [
        "disability",
        "disabled",
        "permanent impairment",
        "loss of function",
        "paralysis",
        "amputation",
    ],
    "hospitalization": [
        "hospitalization",
        "hospitalised",
        "hospitalized",
        "admitted",
        "inpatient",
        "icu",
        "emergency room",
        "er visit",
    ],
}


def _get_classifier():
    """Load a transformer classifier lazily to avoid slow startup."""
    global _CLASSIFIER
    if _CLASSIFIER is not None:
        return _CLASSIFIER

    model_name = os.getenv("SEVERITY_MODEL")
    if model_name:
        _CLASSIFIER = pipeline("text-classification", model=model_name)
        return _CLASSIFIER

    # Default to a zero-shot classifier when a fine-tuned model isn't provided.
    _CLASSIFIER = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return _CLASSIFIER


def _keyword_fallback(text: str) -> Dict:
    lowered = text.lower()
    scores: Dict[str, int] = {label: 0 for label in LABELS}
    hits: Dict[str, List[tuple[str, int]]] = {label: [] for label in _KEYWORDS}
    for label, keywords in _KEYWORDS.items():
        for keyword in keywords:
            count = len(re.findall(rf"\b{re.escape(keyword)}\b", lowered))
            if count:
                hits[label].append((keyword, count))
                scores[label] += count

    best_label, best_score = "other", 0
    for label in LABELS:
        if label == "other":
            continue
        if scores[label] > best_score:
            best_label, best_score = label, scores[label]

    if best_score == 0:
        return {"label": "other", "confidence": 0.5, "top_keywords": []}

    # Confidence is a heuristic normalized by total keyword hits.
    total_hits = sum(scores[label] for label in LABELS if label != "other")
    confidence = best_score / max(total_hits, 1)
    top_keywords = [
        keyword
        for keyword, _ in sorted(hits.get(best_label, []), key=lambda item: item[1], reverse=True)
    ][:5]
    return {
        "label": best_label,
        "confidence": round(confidence, 4),
        "top_keywords": top_keywords,
    }


def _top_keywords_for_label(text: str, label: str) -> List[str]:
    if label not in _KEYWORDS:
        return []
    lowered = text.lower()
    hits: List[tuple[str, int]] = []
    for keyword in _KEYWORDS[label]:
        count = len(re.findall(rf"\b{re.escape(keyword)}\b", lowered))
        if count:
            hits.append((keyword, count))
    return [keyword for keyword, _ in sorted(hits, key=lambda item: item[1], reverse=True)][:5]


def classify_text(text: str, request_id: str | None = None) -> Dict:
    """Classify medical case severity with a transformer model or keyword fallback."""
    start = time.perf_counter()
    try:
        if not text or not text.strip():
            return {
                "severity": SEVERITY_MAP["other"],
                "category": "other",
                "confidence": 0.0,
                "explanation": "Empty input text.",
                "top_keywords": [],
            }

        try:
            clf = _get_classifier()
            if clf.task == "zero-shot-classification":
                result = clf(text, candidate_labels=LABELS, multi_label=False)
                label = result["labels"][0]
                score = float(result["scores"][0])
                top_keywords = _top_keywords_for_label(text, label)
                kw_text = ", ".join(top_keywords) if top_keywords else "none"
                explanation = (
                    f"Classified as {label} ({SEVERITY_MAP.get(label, 'LOW')}) "
                    f"based on keywords: {kw_text}."
                )
                return {
                    "severity": SEVERITY_MAP.get(label, "LOW"),
                    "category": label,
                    "confidence": round(score, 4),
                    "explanation": explanation,
                    "top_keywords": top_keywords,
                }

            result = clf(text, truncation=True)
            if result and isinstance(result, list):
                top = result[0]
                label = str(top.get("label", "other")).lower()
                score = float(top.get("score", 0.0))
                mapped_label = label if label in LABELS else "other"
                top_keywords = _top_keywords_for_label(text, mapped_label)
                kw_text = ", ".join(top_keywords) if top_keywords else "none"
                explanation = (
                    f"Classified as {mapped_label} ({SEVERITY_MAP.get(mapped_label, 'LOW')}) "
                    f"based on keywords: {kw_text}."
                )
                return {
                    "severity": SEVERITY_MAP.get(mapped_label, "LOW"),
                    "category": mapped_label,
                    "confidence": round(score, 4),
                    "explanation": explanation,
                    "top_keywords": top_keywords,
                }
        except Exception:
            _LOGGER.warning(
                "Classifier model unavailable; using keyword fallback.",
                extra={"request_id": request_id},
            )
            used_fallback = True
            fallback = _keyword_fallback(text)
            top_keywords = fallback.get("top_keywords", [])
            kw_text = ", ".join(top_keywords) if top_keywords else "none"
            explanation = (
                f"Classified as {fallback['label']} ({SEVERITY_MAP.get(fallback['label'], 'LOW')}) "
                f"using keyword fallback. Keywords: {kw_text}."
            )
            return {
                "severity": SEVERITY_MAP.get(fallback["label"], "LOW"),
                "category": fallback["label"],
                "confidence": fallback["confidence"],
                "explanation": explanation,
                "top_keywords": top_keywords,
            }

        fallback = _keyword_fallback(text)
        top_keywords = fallback.get("top_keywords", [])
        kw_text = ", ".join(top_keywords) if top_keywords else "none"
        explanation = (
            f"Classified as {fallback['label']} ({SEVERITY_MAP.get(fallback['label'], 'LOW')}) "
            f"using keyword fallback. Keywords: {kw_text}."
        )
        return {
            "severity": SEVERITY_MAP.get(fallback["label"], "LOW"),
            "category": fallback["label"],
            "confidence": fallback["confidence"],
            "explanation": explanation,
            "top_keywords": top_keywords,
        }
    except Exception:
        _LOGGER.exception("Classification failed.", extra={"request_id": request_id})
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _LOGGER.info(
            "Classification completed.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
