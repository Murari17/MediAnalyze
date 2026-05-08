from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request

from ..models.schemas import ClassifyRequest, ClassifyResponse
from ..services.classifier import classify_text
from ..utils.logger import get_logger

router = APIRouter(prefix="/classify", tags=["classify"])
logger = get_logger("medintel.routes.classify")


@router.post("", response_model=ClassifyResponse)
def classify(payload: ClassifyRequest, request: Request) -> ClassifyResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        "Classify request received (text_length=%d).",
        len(payload.text),
        extra={"request_id": request_id},
    )
    start = time.perf_counter()
    try:
        result = classify_text(payload.text, request_id=request_id)
    except Exception as exc:
        logger.exception("Classification failed.", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Classification failed: {exc}") from exc
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Classify processing time.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
    return ClassifyResponse(**result)
