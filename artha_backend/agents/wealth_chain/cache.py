"""Step 1 cache — in-memory with optional Redis backend."""
import hashlib
import json
import os
from typing import Any, Dict, Optional

_MEMORY_CACHE: Dict[str, Dict[str, Any]] = {}
_redis_client = None


def _snapshot_hash(snapshot: Dict[str, Any]) -> str:
    payload = json.dumps(snapshot, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _cache_key(customer_id: str, snapshot: Dict[str, Any]) -> str:
    return f"step1:{customer_id}:{_snapshot_hash(snapshot)}"


def _get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    url = os.environ.get("REDIS_URL")
    if not url:
        return None
    try:
        import redis
        _redis_client = redis.from_url(url, decode_responses=True)
        return _redis_client
    except Exception:
        return None


def get_step1_cached(customer_id: str, snapshot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    key = _cache_key(customer_id, snapshot)
    r = _get_redis()
    if r:
        try:
            raw = r.get(key)
            if raw:
                return json.loads(raw)
        except Exception:
            pass
    return _MEMORY_CACHE.get(key)


def set_step1_cached(customer_id: str, snapshot: Dict[str, Any], step1_data: Dict[str, Any], ttl: int = 3600) -> None:
    key = _cache_key(customer_id, snapshot)
    r = _get_redis()
    if r:
        try:
            r.setex(key, ttl, json.dumps(step1_data))
            return
        except Exception:
            pass
    _MEMORY_CACHE[key] = step1_data
    if len(_MEMORY_CACHE) > 200:
        oldest = next(iter(_MEMORY_CACHE))
        _MEMORY_CACHE.pop(oldest, None)
