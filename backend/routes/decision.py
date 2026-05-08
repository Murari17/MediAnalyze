from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException, Request

from ..models.schemas import DecisionRequest, DecisionResponse
from ..services.decision_support import make_decision
from ..utils.logger import get_logger

router = APIRouter(prefix="/decision", tags=["decision"])
logger = get_logger("medintel.routes.decision")


@router.post("", response_model=DecisionResponse)
def decide(payload: DecisionRequest, request: Request) -> DecisionResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.info("Decision request received.", extra={"request_id": request_id})
    start = time.perf_counter()
    try:
        result = make_decision(
            summary=payload.summary,
            classification=payload.classification,
            validation=payload.validation,
            request_id=request_id,
        )
    except Exception as exc:
        logger.exception("Decision failed.", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Decision failed: {exc}") from exc
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Decision processing time.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )
    return DecisionResponse(**result)
