from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request

from ..models.schemas import AnalyzeRequest, AnalyzeResponse
from ..services.anonymization import anonymize_text
from ..services.classifier import classify_text
from ..services.decision import generate_decision
from ..services.semantic_compare import compare_documents
from ..services.summarization import summarize_text
from ..services.validation import validate_document
from ..utils.logger import get_logger

router = APIRouter(prefix="/analyze", tags=["analyze"])
logger = get_logger("medintel.routes.analyze")


@router.post("", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        "Analyze request received (len_a=%d, len_b=%d).",
        len(payload.text_a),
        len(payload.text_b) if payload.text_b else 0,
        extra={"request_id": request_id},
    )
    start = time.perf_counter()
    try:
        summary_text, summary_conf = summarize_text(
            payload.text_a, request_id=request_id
        )
        summary = {
            "summary": summary_text,
            "confidence": summary_conf,
            "explanation": (
                f"Summary generated with facebook/bart-large-cnn from {len(payload.text_a)} "
                f"chars to {len(summary_text)} chars."
            ),
            "model": "facebook/bart-large-cnn",
        }

        anonymized = anonymize_text(payload.text_a, request_id=request_id)

        validation = validate_document(payload.text_a, request_id=request_id)
        classification = classify_text(payload.text_a, request_id=request_id)

        comparison = None
        if payload.text_b and payload.text_b.strip():
            comparison = compare_documents(
                payload.text_a,
                payload.text_b,
                request_id=request_id,
            )

        decision = generate_decision(
            validation=validation,
            classification=classification,
            summary=summary_text,
            request_id=request_id,
        )

        confidences = [
            summary_conf,
            anonymized.get("confidence", 0.0),
            validation.get("confidence", 0.0),
            classification.get("confidence", 0.0),
        ]
        if comparison is not None:
            confidences.append(comparison.get("confidence", 0.0))
        overall_confidence = round(sum(confidences) / max(len(confidences), 1), 4)

        return AnalyzeResponse(
            summary=summary,
            anonymized_text=anonymized,
            validation=validation,
            classification=classification,
            comparison=comparison,
            decision=decision,
            confidence=overall_confidence,
        )
    except Exception as exc:
        logger.exception("Analyze failed.", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Analyze failed: {exc}") from exc
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Analyze processing time.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
