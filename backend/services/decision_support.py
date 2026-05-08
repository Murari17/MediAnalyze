from __future__ import annotations

from .decision import generate_decision


def make_decision(
    summary: str,
    classification: dict,
    validation: dict,
    request_id: str | None = None,
) -> dict:
    """Backward-compatible wrapper for generate_decision."""
    return generate_decision(
        validation=validation,
        classification=classification,
        summary=summary,
        request_id=request_id,
    )
