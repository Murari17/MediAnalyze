from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request

from ..models.schemas import AnonymizeRequest, AnonymizeResponse
from ..services.anonymization import anonymize_text
from ..utils.logger import get_logger

router = APIRouter(prefix="/anonymize", tags=["anonymize"])
logger = get_logger("medintel.routes.anonymize")


@router.post("", response_model=AnonymizeResponse)
def anonymize(payload: AnonymizeRequest, request: Request) -> AnonymizeResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        "Anonymize request received (text_length=%d).",
        len(payload.text),
        extra={"request_id": request_id},
    )
    start = time.perf_counter()
    try:
        result = anonymize_text(payload.text, request_id=request_id)
    except Exception as exc:
        logger.exception("Anonymization failed.", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {exc}") from exc
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Anonymize processing time.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
    return AnonymizeResponse(**result)
