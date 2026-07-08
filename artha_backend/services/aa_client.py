"""Account Aggregator sandbox client (mock with swappable interface)."""
import os
from typing import Any, Dict, Optional

from services.customer_snapshot import get_snapshot


class AAClient:
    """Financial Information User client — sandbox/mock implementation."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.environ.get("AA_SANDBOX_URL", "https://sandbox.aa.mock/v1")
        self.use_live = os.environ.get("AA_LIVE", "").lower() in ("1", "true", "yes")

    def fetch_customer_data(self, customer_id: str, consent_id: str) -> Dict[str, Any]:
        if self.use_live:
            # Production: HTTP call to licensed NBFC-AA
            raise NotImplementedError("Live AA integration requires bank credentials")
        return get_snapshot(customer_id)

    def validate_consent(self, consent: Dict[str, Any]) -> bool:
        if not consent:
            return False
        from datetime import datetime
        expires = consent.get("expiresAt", "")
        try:
            return datetime.strptime(expires, "%Y-%m-%d") >= datetime.now()
        except ValueError:
            return False


_default_client: Optional[AAClient] = None


def get_aa_client() -> AAClient:
    global _default_client
    if _default_client is None:
        _default_client = AAClient()
    return _default_client
