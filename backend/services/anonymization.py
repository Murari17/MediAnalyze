from __future__ import annotations

import re
import time
from collections import defaultdict
from typing import Dict, List, Tuple

import spacy

from ..utils.logger import get_logger

_LOGGER = get_logger("medintel.services.anonymization")

_NLP = None

ALLOWED_LABELS = {"PERSON", "GPE", "ORG"}
MEDICAL_TERMS = {
    "bp",
    "hr",
    "rr",
    "spo2",
    "ecg",
    "troponin",
    "glucose",
    "sob",
    "dm",
    "htn",
    "statin",
    "aspirin",
    "metformin",
    "losartan",
    "amlodipine",
    "atorvastatin",
    "clopidogrel",
    "heparin",
}
MEDICAL_WHITELIST = MEDICAL_TERMS

UNIT_REGEX = re.compile(
    r"\b\d+(?:\.\d+)?\s*(mg|mcg|g|ml|bpm|mmhg|%|/min|min|kg|cm|mm)\b",
    re.IGNORECASE,
)
MEASUREMENT_REGEX = re.compile(
    r"\b(?:bp|hr|rr|spo2|temp|temperature|pulse|respiratory rate)\s*[:=]?\s*\d{1,3}(?:/\d{1,3})?\s*(?:mmhg|bpm|%|/min)?\b",
    re.IGNORECASE,
)
ABBREVIATION_REGEX = re.compile(
    r"\b(?:bp|hr|rr|spo2|ecg|ekg|sob|dm|htn)\b", re.IGNORECASE
)
SECTION_KEYWORDS = {
    "meds",
    "medications",
    "current medications",
    "history",
    "hx",
    "plan",
    "assessment",
    "diagnosis",
    "chief complaint",
    "complaint",
    "treatment",
    "impression",
    "investigations",
    "exam",
    "vitals",
}
SECTION_LABEL_REGEX = re.compile(
    r"(?m)^\s*(?:meds|medications|current medications|history|hx|plan|assessment|diagnosis|chief complaint|complaint|treatment|impression|investigations|exam|vitals)\s*:?",
    re.IGNORECASE,
)
MEDICAL_WHITELIST_REGEX = re.compile(
    r"\b(?:bp|hr|rr|spo2|ecg|ekg|troponin|glucose|sob|dm|htn|statin|aspirin|metformin|losartan|amlodipine|atorvastatin|clopidogrel|heparin)\b",
    re.IGNORECASE,
)


def _is_all_caps(text: str) -> bool:
    return text.isupper() and len(text) >= 2


def _is_short_token(text: str) -> bool:
    return len(re.sub(r"\W+", "", text)) < 4


def _is_high_confidence(ent) -> bool:
    """Heuristic confidence check for entity replacement."""
    try:
        if ent.has_extension("confidence"):
            conf = float(ent._.confidence)  # type: ignore[attr-defined]
            return conf >= 0.6
    except Exception:
        pass

    text = ent.text.strip()
    words = [w for w in text.split() if w]
    if not words:
        return False
    if ent.label_ == "PERSON":
        if len(words) >= 2:
            return True
        return words[0][0].isupper() and len(words[0]) >= 4
    if ent.label_ in {"ORG", "GPE"}:
        return len(words) >= 2 or (words[0][0].isupper() and len(words[0]) >= 4)
    return True


def _is_section_label(text: str) -> bool:
    cleaned = text.strip().lower().rstrip(":")
    return cleaned in SECTION_KEYWORDS


def _build_protected_spans(text: str) -> List[Tuple[int, int]]:
    spans: List[Tuple[int, int]] = []
    for regex in (UNIT_REGEX, MEASUREMENT_REGEX, ABBREVIATION_REGEX, SECTION_LABEL_REGEX):
        for match in regex.finditer(text):
            spans.append(match.span())
    return spans


def _overlaps(span: Tuple[int, int], protected: List[Tuple[int, int]]) -> bool:
    start, end = span
    for p_start, p_end in protected:
        if start < p_end and end > p_start:
            return True
    return False


def _get_nlp():
    """Load spaCy model once."""
    global _NLP
    if _NLP is None:
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _replace_spans(text: str, spans: List[Tuple[int, int, str]]) -> str:
    if not spans:
        return text
    spans_sorted = sorted(spans, key=lambda x: x[0], reverse=True)
    output = text
    for start, end, token in spans_sorted:
        output = output[:start] + token + output[end:]
    return output


def _near_unit(text: str, start: int, end: int, window: int = 6) -> bool:
    """Return True if entity is within a small window of a unit expression."""
    for match in UNIT_REGEX.finditer(text):
        u_start, u_end = match.span()
        if start <= u_end + window and end >= u_start - window:
            return True
    return False


def _estimate_confidence(replacements: int, skipped: int) -> float:
    if replacements == 0:
        return 0.3
    base = 0.6 + 0.05 * min(replacements, 6)
    penalty = 0.02 * min(skipped, 6)
    return round(max(0.3, min(0.9, base - penalty)), 4)


def anonymize_text(text: str, request_id: str | None = None) -> Dict:
    """Redact PII/PHI with controlled entity labels and medical-term protections."""
    start = time.perf_counter()
    try:
        if not text or not text.strip():
            return {
                "anonymized_text": "",
                "redactions": [],
                "entities_replaced": {},
                "spans": [],
                "confidence": 0.0,
                "explanation": "Empty input text.",
            }

        nlp = _get_nlp()
        doc = nlp(text)

        label_counts: Dict[str, int] = defaultdict(int)
        replacements: Dict[Tuple[str, str], str] = {}
        redactions: List[Dict[str, str]] = []
        spans: List[Tuple[int, int, str]] = []
        ignored_terms: List[str] = []
        skipped_units: int = 0
        skipped_structured: int = 0
        skipped_low_conf: int = 0

        protected_spans = _build_protected_spans(text)
        ignored_terms.extend(match.group(0) for match in MEDICAL_WHITELIST_REGEX.finditer(text))

        for ent in doc.ents:
            if ent.label_ not in ALLOWED_LABELS:
                continue

            ent_text = ent.text.strip()
            ent_lower = ent_text.lower()
            if ent_lower in MEDICAL_TERMS:
                ignored_terms.append(ent_text)
                continue

            if _is_short_token(ent_text) or _is_all_caps(ent_text):
                ignored_terms.append(ent_text)
                continue

            if _is_section_label(ent_text):
                ignored_terms.append(ent_text)
                continue

            if ent_text.endswith(":") and len(ent_text) <= 10:
                ignored_terms.append(ent_text)
                continue

            if UNIT_REGEX.search(ent_text) or MEASUREMENT_REGEX.search(ent_text):
                ignored_terms.append(ent_text)
                skipped_structured += 1
                continue

            if _overlaps((ent.start_char, ent.end_char), protected_spans):
                ignored_terms.append(ent_text)
                skipped_structured += 1
                continue

            if _near_unit(text, ent.start_char, ent.end_char):
                skipped_units += 1
                ignored_terms.append(ent_text)
                continue

            if not _is_high_confidence(ent):
                skipped_low_conf += 1
                ignored_terms.append(ent_text)
                continue

            key = (ent_text, ent.label_)
            if key not in replacements:
                label_counts[ent.label_] += 1
                token = f"{ent.label_}_{label_counts[ent.label_]}"
                replacements[key] = token
                redactions.append(
                    {
                        "label": ent.label_,
                        "text": ent_text,
                        "token": token,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                )
            spans.append((ent.start_char, ent.end_char, replacements[key]))

        redacted_text = _replace_spans(text, spans)

        entities_replaced = {text: token for (text, _), token in replacements.items()}
        confidence = _estimate_confidence(
            len(entities_replaced),
            skipped_units + skipped_structured + skipped_low_conf + len(ignored_terms),
        )

        explanation_parts = [
            f"Replaced {len(entities_replaced)} entities (labels: {', '.join(sorted(ALLOWED_LABELS))})."
        ]
        if ignored_terms:
            explanation_parts.append(
                f"Ignored terms: {', '.join(sorted(set(ignored_terms)))}."
            )
        if skipped_units:
            explanation_parts.append(
                f"Skipped {skipped_units} entities near dosage/measurement units."
            )
        if skipped_structured:
            explanation_parts.append(
                f"Skipped {skipped_structured} entities inside structured clinical patterns."
            )
        if skipped_low_conf:
            explanation_parts.append(
                f"Skipped {skipped_low_conf} low-confidence entities."
            )
        explanation = " ".join(explanation_parts)

        return {
            "anonymized_text": redacted_text,
            "redactions": redactions,
            "entities_replaced": entities_replaced,
            "spans": [
                {"start": item["start"], "end": item["end"], "label": item["label"], "token": item["token"]}
                for item in redactions
            ],
            "confidence": confidence,
            "explanation": explanation,
            "ignored_terms": sorted(set(ignored_terms)),
            "reason": "Medical terms preserved to maintain clinical meaning.",
        }
    except Exception:
        _LOGGER.exception("Anonymization failed.", extra={"request_id": request_id})
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _LOGGER.info(
            "Anonymization completed.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
