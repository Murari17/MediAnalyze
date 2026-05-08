from __future__ import annotations

import contextvars
import json
import logging
from datetime import datetime, timezone
from typing import Optional

_request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
_endpoint_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "endpoint", default=None
)

_CONFIGURED = False


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id") or record.request_id is None:
            record.request_id = _request_id_var.get()
        if not hasattr(record, "endpoint") or record.endpoint is None:
            record.endpoint = _endpoint_var.get()
        if not hasattr(record, "duration_ms"):
            record.duration_ms = None
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        payload = {
            "timestamp": timestamp,
            "level": record.levelname,
            "request_id": record.request_id or "",
            "endpoint": record.endpoint or "",
            "message": record.getMessage(),
            "duration_ms": record.duration_ms,
        }
        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: int = logging.INFO) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    handler.addFilter(RequestContextFilter())
    root.handlers = [handler]
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def set_request_context(request_id: str, endpoint: str) -> None:
    _request_id_var.set(request_id)
    _endpoint_var.set(endpoint)


def clear_request_context() -> None:
    _request_id_var.set(None)
    _endpoint_var.set(None)
