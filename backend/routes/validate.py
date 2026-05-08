from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request

from ..models.schemas import ValidateRequest, ValidateResponse
from ..services.validation import validate_document
from ..utils.logger import get_logger

router = APIRouter(prefix="/validate", tags=["validate"])
logger = get_logger("medintel.routes.validate")


@router.post("", response_model=ValidateResponse)
def validate(payload: ValidateRequest, request: Request) -> ValidateResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        "Validate request received (text_length=%d).",
        len(payload.text),
        extra={"request_id": request_id},
    )
    start = time.perf_counter()
    try:
        result = validate_document(payload.text, request_id=request_id)
    except Exception as exc:
        logger.exception("Validation failed.", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Validation failed: {exc}") from exc
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Validate processing time.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
    return ValidateResponse(**result)
