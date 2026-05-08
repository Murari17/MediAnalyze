from __future__ import annotations

import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from ..services.text_extraction import extract_text_from_file
from ..utils.logger import get_logger

router = APIRouter(prefix="/upload", tags=["upload"])
logger = get_logger("medintel.routes.upload")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = ROOT_DIR / "data" / "uploads"

ALLOWED_EXTS = {".pdf", ".txt"}


def _build_safe_path(filename: str) -> Path:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")
    safe_name = f"{uuid4().hex}{ext}"
    return UPLOAD_DIR / safe_name


@router.post("")
async def upload_file(request: Request, file: UploadFile = File(...)) -> dict:
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        "Upload request received (filename=%s).",
        file.filename,
        extra={"request_id": request_id},
    )
    start = time.perf_counter()
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename.")
    target_path = _build_safe_path(file.filename)
    try:
        contents = await file.read()
        target_path.write_bytes(contents)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {exc}") from exc

    try:
        extracted_text = extract_text_from_file(target_path, request_id=request_id)
    except Exception as exc:
        logger.exception("Text extraction failed.", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {exc}") from exc
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Upload processing time.",
            extra={"request_id": request_id, "duration_ms": elapsed_ms},
        )

    preview = extracted_text[:500]
    return {
        "file_name": file.filename,
        "stored_path": str(target_path),
        "text_length": len(extracted_text),
        "text_preview": preview,
    }
