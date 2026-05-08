from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request

from ..models.schemas import SummarizeRequest, SummarizeResponse
from ..services.summarization import summarize_text
from ..utils.logger import get_logger

router = APIRouter(prefix="/summarize", tags=["summarize"])
logger = get_logger("medintel.routes.summarize")


@router.post("", response_model=SummarizeResponse)
def summarize(payload: SummarizeRequest, request: Request) -> SummarizeResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        "Summarize request received (text_length=%d).",
        len(payload.text),
        extra={"request_id": request_id},
    )
    start = time.perf_counter()
    try:
        summary, confidence = summarize_text(
            payload.text,
            max_length=payload.max_length,
            request_id=request_id,
        )
    except Exception as exc:
        logger.exception("Summarization failed.", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Summarization failed: {exc}") from exc
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Summarize processing time.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
    explanation = (
        f"Summary generated with facebook/bart-large-cnn from {len(payload.text)} "
        f"chars to {len(summary)} chars."
    )
    return SummarizeResponse(
        summary=summary,
        confidence=confidence,
        explanation=explanation,
        model="facebook/bart-large-cnn",
    )
