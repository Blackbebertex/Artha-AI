"""Optional JWT auth stub for pilot staging."""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt

SECRET = os.environ.get("JWT_SECRET", "artha-pilot-dev-secret-change-in-prod")
ALGORITHM = "HS256"


def create_demo_jwt(customer_id: str, name: str, hours: int = 24) -> str:
    payload = {
        "sub": customer_id,
        "name": name,
        "exp": datetime.now(timezone.utc) + timedelta(hours=hours),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def decode_jwt(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except Exception:
        return None
