from __future__ import annotations

import re
import time
from typing import Dict, List

from ..utils.logger import get_logger

_LOGGER = get_logger("medintel.services.decision")

CARDIAC_SIGNAL_PATTERNS = [
    (re.compile(r"\bchest pain\b", re.IGNORECASE), "chest pain"),
    (
        re.compile(r"\belevated\s+troponin\b|\btroponin\b.*\b(elevated|high|positive)\b", re.IGNORECASE),
        "elevated troponin",
    ),
    (
        re.compile(r"\bnstemi\b|non[- ]st elevation myocardial infarction", re.IGNORECASE),
        "NSTEMI diagnosis",
    ),
    (
        re.compile(r"\bst segment depression\b", re.IGNORECASE),
        "ST segment depression",
    ),
    (
        re.compile(r"\bacute coronary syndrome\b|\bacs\b", re.IGNORECASE),
        "acute coronary syndrome",
    ),
    (
        re.compile(r"\bmyocardial infarction\b|\bmi\b", re.IGNORECASE),
        "myocardial infarction",
    ),
]

GENERAL_SIGNAL_PATTERNS = [
    (re.compile(r"\bstroke\b|cerebrovascular", re.IGNORECASE), "stroke"),
    (re.compile(r"\bsepsis\b", re.IGNORECASE), "sepsis"),
    (re.compile(r"\bhemorrhage\b|bleeding", re.IGNORECASE), "hemorrhage"),
    (re.compile(r"\brespiratory failure\b", re.IGNORECASE), "respiratory failure"),
    (re.compile(r"\bshock\b", re.IGNORECASE), "shock"),
]


def _extract_signals(summary: str) -> List[str]:
    """Extract high-risk signals from the summary text."""
    if not summary:
        return []
    signals: List[str] = []
    for pattern, label in CARDIAC_SIGNAL_PATTERNS + GENERAL_SIGNAL_PATTERNS:
        if pattern.search(summary):
            signals.append(label)
    # de-duplicate while preserving order
    seen = set()
    ordered: List[str] = []
    for item in signals:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _build_reason(
    decision: str,
    missing_fields: List[str],
    severity: str,
    summary: str | None,
) -> str:
    """Build a human-readable reason based on decision state and signals."""
    if decision == "INCOMPLETE SUBMISSION":
        return f"Missing required fields: {', '.join(missing_fields)}."
    signals = _extract_signals(summary or "")
    has_cardiac = any(
        signal
        in {
            "chest pain",
            "elevated troponin",
            "NSTEMI diagnosis",
            "ST segment depression",
            "acute coronary syndrome",
            "myocardial infarction",
        }
        for signal in signals
    )
    if decision == "URGENT ATTENTION":
        if signals:
            prefix = "Critical medical indicators detected"
            return f"{prefix}: {', '.join(signals)}."
        return "Critical medical condition detected."
    if decision == "REQUIRES REVIEW":
        if signals:
            prefix = "High-risk cardiac indicators detected" if has_cardiac else "High-risk indicators detected"
            return f"{prefix}: {', '.join(signals)}."
        return "High-risk indicators detected."
    return "No major issues detected."


def generate_decision(
    validation: dict,
    classification: dict,
    summary: str | None = None,
    request_id: str | None = None,
) -> dict:
    """Generate final decision from validation completeness and classification severity."""
    start = time.perf_counter()
    try:
        missing_fields = validation.get("missing_fields", [])
        severity = str(classification.get("severity", "")).upper()

        if missing_fields:
            decision = "INCOMPLETE SUBMISSION"
        elif severity == "CRITICAL":
            decision = "URGENT ATTENTION"
        elif severity == "HIGH":
            decision = "REQUIRES REVIEW"
        else:
            decision = "SAFE"

        reason = _build_reason(decision, missing_fields, severity, summary)
        confidence = float(classification.get("confidence", 0.5))

        return {"decision": decision, "reason": reason, "confidence": round(confidence, 4)}
    except Exception:
        _LOGGER.exception("Decision generation failed.", extra={"request_id": request_id})
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _LOGGER.info(
            "Decision generation completed.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
