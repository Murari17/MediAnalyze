from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import analyze, anonymize, classify, compare, decision, summarize, upload, validate
from .utils.logger import clear_request_context, configure_logging, get_logger, set_request_context

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "uploads"


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="MedIntel AI - Autonomous Regulatory Intelligence System",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_request_duration(request: Request, call_next):
        logger = get_logger("medintel.middleware")
        request_id = uuid4().hex
        endpoint = request.url.path
        request.state.request_id = request_id
        set_request_context(request_id, endpoint)
        logger.info("Request received.")
        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled error while processing request.")
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info("Request completed.", extra={"duration_ms": elapsed_ms})
            clear_request_context()

        if response is not None:
            response.headers["X-Request-ID"] = request_id
        return response

    app.include_router(upload.router)
    app.include_router(summarize.router)
    app.include_router(anonymize.router)
    app.include_router(compare.router)
    app.include_router(validate.router)
    app.include_router(classify.router)
    app.include_router(analyze.router)
    app.include_router(decision.router)

    @app.on_event("startup")
    def _ensure_dirs() -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    @app.get("/health")
    def healthcheck() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
