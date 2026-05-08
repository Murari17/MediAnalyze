from __future__ import annotations

import re
import time
from typing import Dict, List, Tuple

from ..utils.logger import get_logger

_LOGGER = get_logger("medintel.services.validation")

REQUIRED_FIELDS = ["patient_name", "age", "drug_name", "adverse_event"]
LOW_CONF_THRESHOLD = 0.6

FIELD_SYNONYMS = {
    "patient_name": ["name", "patient name"],
    "age": ["age"],
    "drug_name": ["medication", "drug", "current medications"],
    "adverse_event": ["chief complaint", "complaint", "diagnosis", "condition"],
}

ADVERSE_EVENT_KEYWORDS = ["pain", "syndrome", "infarction", "injury", "reaction"]

MEDICATION_SECTIONS = ["current medications", "medications", "treatment"]

KNOWN_DRUGS = {
    "metformin",
    "amlodipine",
    "atorvastatin",
    "aspirin",
    "clopidogrel",
    "heparin",
}

AGE_PATTERNS = [
    re.compile(r"\bage\s*[:\-]\s*(\d{1,3})\b", re.IGNORECASE),
    re.compile(r"\b(\d{1,3})\s*(?:years?|yrs?)\s*old\b", re.IGNORECASE),
    re.compile(r"\b(\d{1,3})-year-old\b", re.IGNORECASE),
]

NAME_PATTERNS = [
    re.compile(r"^\s*(?:patient\s*)?name\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{1,80})$", re.IGNORECASE),
    re.compile(r"^\s*name\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{1,80})$", re.IGNORECASE),
]

PROBABLE_NAME_PATTERN = re.compile(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b")

HEADER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z \-/]{2,50}:\s*$")

DOSAGE_PATTERN = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9 \-/+]{1,40}?)\s+\d+(?:\.\d+)?\s*(mg|mcg|g|ml)\b",
    re.IGNORECASE,
)


def _lower(text: str) -> str:
    return text.lower()


def _find_synonym_hits(text_lower: str, synonyms: List[str]) -> bool:
    return any(syn in text_lower for syn in synonyms)


def _dedupe(values: List[str]) -> List[str]:
    seen = set()
    unique: List[str] = []
    for item in values:
        normalized = re.sub(r"\s+", " ", item).strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(item.strip())
    return unique


def _extract_age_candidates(text: str) -> Tuple[List[str], float, str]:
    label_matches = [m for m in AGE_PATTERNS[0].findall(text)]
    other_matches: List[str] = []
    for pattern in AGE_PATTERNS[1:]:
        other_matches.extend(pattern.findall(text))

    def _clean(values: List[str]) -> List[str]:
        cleaned: List[str] = []
        for value in values:
            value = str(value).strip()
            if value.isdigit():
                age = int(value)
                if 0 < age < 120:
                    cleaned.append(str(age))
        return cleaned

    if label_matches:
        ages = _dedupe(_clean(label_matches + other_matches))
        return ages, 0.9, "matched explicit age label"
    if other_matches:
        ages = _dedupe(_clean(other_matches))
        return ages, 0.55, "matched age phrase in narrative"
    return [], 0.0, ""


def _extract_patient_name(lines: List[str]) -> str:
    for line in lines:
        for pattern in NAME_PATTERNS:
            match = pattern.match(line.strip())
            if match:
                return match.group(1).strip()
    return ""


def _extract_probable_name(lines: List[str]) -> str:
    for line in lines[:6]:
        if "hospital" in line.lower() or "clinic" in line.lower():
            continue
        match = PROBABLE_NAME_PATTERN.search(line)
        if match:
            return match.group(1).strip()
    return ""


def _extract_medication_section(lines: List[str]) -> Tuple[List[str], str]:
    section_lines: List[str] = []
    section_name = ""
    in_section = False
    for line in lines:
        stripped = line.strip()
        lower = stripped.lower().rstrip(":")
        if any(lower == header for header in MEDICATION_SECTIONS):
            in_section = True
            section_name = stripped.rstrip(":")
            continue
        if in_section:
            if not stripped:
                continue
            if HEADER_PATTERN.match(stripped):
                break
            section_lines.append(stripped)
    return section_lines, section_name


def _extract_drug_names_from_lines(lines: List[str]) -> List[str]:
    names: List[str] = []
    for line in lines:
        lower = line.lower()
        for drug in KNOWN_DRUGS:
            if re.search(rf"\b{re.escape(drug)}\b", lower):
                names.append(drug.capitalize())
        match = DOSAGE_PATTERN.match(line)
        if match:
            raw_name = match.group(1).strip()
            parts = re.split(r"\s*[+/,&]\s*", raw_name)
            for part in parts:
                cleaned = part.strip()
                if cleaned:
                    names.append(cleaned)
    return _dedupe(names)


def _extract_adverse_event(lines: List[str], text_lower: str) -> Tuple[str, str]:
    for idx, line in enumerate(lines):
        lower = line.lower()
        if any(syn in lower for syn in FIELD_SYNONYMS["adverse_event"]):
            parts = line.split(":", 1)
            if len(parts) == 2 and parts[1].strip():
                return parts[1].strip(), "section"
            for offset in range(1, 4):
                if idx + offset >= len(lines):
                    break
                next_line = lines[idx + offset].strip()
                if next_line:
                    return next_line, "section"
    for keyword in ADVERSE_EVENT_KEYWORDS:
        if keyword in text_lower:
            sentences = re.split(r"(?<=[.!?])\s+", " ".join(lines))
            for sentence in sentences:
                if keyword in sentence.lower():
                    return sentence.strip(), "keyword"
            return keyword, "keyword"
    return "", ""


def _record_field(
    detected_fields: Dict[str, object],
    low_confidence_fields: Dict[str, object],
    highlights: Dict[str, str],
    field: str,
    value: object,
    section: str,
    reason: str,
    confidence: float,
) -> None:
    entry = {
        "value": value,
        "section": section,
        "reason": reason,
        "confidence": round(confidence, 4),
    }
    target = detected_fields if confidence >= LOW_CONF_THRESHOLD else low_confidence_fields
    target[field] = entry

    if value:
        if isinstance(value, list):
            highlights[field] = "; ".join(value[:3])
        else:
            highlights[field] = str(value)


def _build_explanation(
    detected: Dict[str, object],
    low_confidence: Dict[str, object],
    missing: List[str],
) -> str:
    parts: List[str] = []
    for field, value in detected.items():
        val = value.get("value") if isinstance(value, dict) else value
        section = value.get("section") if isinstance(value, dict) else None
        reason = value.get("reason") if isinstance(value, dict) else None
        if isinstance(val, list) and val:
            text = f"{field} detected: {', '.join(val)}"
        elif isinstance(val, str) and val:
            text = f"{field} detected: {val}"
        else:
            text = f"{field} detected"
        if section:
            text += f" (section: {section})"
        if reason:
            text += f" because {reason}"
        parts.append(text + ".")

    for field, value in low_confidence.items():
        val = value.get("value") if isinstance(value, dict) else value
        if isinstance(val, list) and val:
            text = f"{field} detected with low confidence: {', '.join(val)}"
        elif isinstance(val, str) and val:
            text = f"{field} detected with low confidence: {val}"
        else:
            text = f"{field} detected with low confidence"
        parts.append(text + " (detected from unstructured text).")

    for field in missing:
        parts.append(f"{field} missing.")
    return " ".join(parts)


def validate_document(text: str, request_id: str | None = None) -> Dict:
    """Validate required fields with confidence-aware detection."""
    start = time.perf_counter()
    try:
        cleaned = text.strip()
        if not cleaned:
            return {
                "missing_fields": REQUIRED_FIELDS,
                "detected_fields": {},
                "low_confidence_fields": {},
                "inconsistencies": [],
                "confidence": 0.0,
                "explanation": "Empty input text.",
                "highlights": {},
            }

        text_lower = _lower(cleaned)
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

        detected_fields: Dict[str, object] = {}
        low_confidence_fields: Dict[str, object] = {}
        highlights: Dict[str, str] = {}

        # patient_name
        if _find_synonym_hits(text_lower, FIELD_SYNONYMS["patient_name"]):
            name_val = _extract_patient_name(lines)
            if name_val:
                _record_field(
                    detected_fields,
                    low_confidence_fields,
                    highlights,
                    "patient_name",
                    name_val,
                    "Demographics",
                    "matched 'name' label in patient header",
                    0.9,
                )
        if "patient_name" not in detected_fields:
            probable = _extract_probable_name(lines)
            if probable:
                _record_field(
                    detected_fields,
                    low_confidence_fields,
                    highlights,
                    "patient_name",
                    probable,
                    "Demographics",
                    "heuristic name pattern",
                    0.55,
                )

        # age
        ages, age_conf, age_reason = _extract_age_candidates(cleaned)
        if ages:
            _record_field(
                detected_fields,
                low_confidence_fields,
                highlights,
                "age",
                ages[0],
                "Demographics",
                age_reason,
                age_conf,
            )

        # drug_name
        meds: List[str] = []
        section_lines, section_name = _extract_medication_section(lines)
        if section_lines:
            meds = _extract_drug_names_from_lines(section_lines)
        if not meds and _find_synonym_hits(text_lower, FIELD_SYNONYMS["drug_name"]):
            meds = _extract_drug_names_from_lines(lines)
        if meds:
            reason = (
                "detected medications under section header"
                if section_lines
                else "heuristic dosage pattern"
            )
            confidence = 0.85 if section_lines else 0.55
            _record_field(
                detected_fields,
                low_confidence_fields,
                highlights,
                "drug_name",
                meds,
                section_name or "Medications",
                reason,
                confidence,
            )

        # adverse_event
        if _find_synonym_hits(text_lower, FIELD_SYNONYMS["adverse_event"]) or any(
            keyword in text_lower for keyword in ADVERSE_EVENT_KEYWORDS
        ):
            adverse_val, source = _extract_adverse_event(lines, text_lower)
            if adverse_val:
                confidence = 0.8 if source == "section" else 0.55
                reason = (
                    "matched complaint/diagnosis terminology"
                    if source == "section"
                    else "keyword match in narrative"
                )
                _record_field(
                    detected_fields,
                    low_confidence_fields,
                    highlights,
                    "adverse_event",
                    adverse_val,
                    "Chief Complaint/Diagnosis",
                    reason,
                    confidence,
                )

        missing_fields = [
            field
            for field in REQUIRED_FIELDS
            if field not in detected_fields and field not in low_confidence_fields
        ]

        inconsistencies: List[str] = []
        if len(set(ages)) > 1:
            inconsistencies.append(f"Multiple ages detected: {', '.join(ages)}")

        field_confidences = [
            value.get("confidence", 0.0) for value in detected_fields.values()
        ] + [
            value.get("confidence", 0.0) for value in low_confidence_fields.values()
        ]
        confidence = sum(field_confidences) / max(len(REQUIRED_FIELDS), 1)
        confidence -= 0.1 * len(inconsistencies)
        confidence = round(max(0.0, min(1.0, confidence)), 4)

        explanation = _build_explanation(detected_fields, low_confidence_fields, missing_fields)
        if meds and section_name:
            explanation += f" Detected medications under '{section_name}' section."

        return {
            "missing_fields": missing_fields,
            "detected_fields": detected_fields,
            "low_confidence_fields": low_confidence_fields,
            "inconsistencies": inconsistencies,
            "confidence": confidence,
            "explanation": explanation,
            "highlights": highlights,
        }
    except Exception:
        _LOGGER.exception("Validation failed.", extra={"request_id": request_id})
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _LOGGER.info(
            "Validation completed.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
