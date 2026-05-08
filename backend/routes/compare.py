from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request

from ..models.schemas import CompareRequest, CompareResponse
from ..services.semantic_compare import compare_documents
from ..utils.logger import get_logger

router = APIRouter(prefix="/compare", tags=["compare"])
logger = get_logger("medintel.routes.compare")


@router.post("", response_model=CompareResponse)
def compare(payload: CompareRequest, request: Request) -> CompareResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        "Compare request received (len_a=%d, len_b=%d).",
        len(payload.text_a),
        len(payload.text_b),
        extra={"request_id": request_id},
    )
    start = time.perf_counter()
    try:
        result = compare_documents(
            payload.text_a,
            payload.text_b,
            threshold=payload.threshold,
            max_sections=payload.max_sections,
            request_id=request_id,
        )
    except Exception as exc:
        logger.exception("Comparison failed.", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Comparison failed: {exc}") from exc
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Compare processing time.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
    return CompareResponse(**result)
