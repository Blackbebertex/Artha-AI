"""SIP / insurance execution gateway — pilot stub (log only, no trades)."""
from datetime import datetime, timezone
from typing import Any, Dict

from services.audit_logger import log_event


def submit_execution_intent(
    customer_id: str,
    product_id: str,
    action: str,
    amount: float,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    payload = {
        "event_type": "execution_intent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "customer_id": customer_id,
        "product_id": product_id,
        "action": action,
        "amount": amount,
        "status": "logged_stub",
        "metadata": metadata or {},
    }
    log_event(payload)
    return {
        "status": "accepted_stub",
        "message": "Intent logged for pilot — no trade executed",
        "intent_id": f"intent_{customer_id}_{product_id}",
    }
