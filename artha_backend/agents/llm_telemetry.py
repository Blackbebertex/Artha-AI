"""Telemetry for LLM invocation paths (live API vs keyword fallback)."""
import datetime
from datetime import timezone
from typing import Any, Dict, Optional

_EVENTS: list = []


def record_llm_event(
    path: str,
    *,
    success: bool,
    model: Optional[str] = None,
    error: Optional[str] = None,
    customer_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = {
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "path": path,
        "success": success,
        "model": model,
        "error": error,
        "customer_id": customer_id,
        "extra": extra or {},
    }
    _EVENTS.append(event)
    if len(_EVENTS) > 500:
        del _EVENTS[: len(_EVENTS) - 500]
    tag = "LLM_TELEMETRY"
    status = "ok" if success else "fallback"
    print(f"[{tag}] path={path} status={status} model={model or 'keyword_mock'} error={error or ''}")
    return event


def get_recent_events(limit: int = 50) -> list:
    return list(_EVENTS[-limit:])
