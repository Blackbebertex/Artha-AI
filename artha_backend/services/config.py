"""Environment-based application configuration."""
import os
from functools import lru_cache
from typing import List, Optional


@lru_cache
def get_settings():
    return Settings()


class Settings:
  def __init__(self):
    self.gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "").strip()
    self.gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    self.gemini_timeout_seconds: float = float(os.environ.get("GEMINI_TIMEOUT_SECONDS", "60"))
    self.gemini_max_retries: int = int(os.environ.get("GEMINI_MAX_RETRIES", "3"))
    self.port: int = int(os.environ.get("PORT", "8000"))
    self.app_env: str = os.environ.get("NODE_ENV", os.environ.get("APP_ENV", "development"))
    self.is_production: bool = self.app_env == "production"
    self.allowed_origins: List[str] = self._parse_origins(
      os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000",
      )
    )
    self.wealth_chain_enabled: bool = os.environ.get("WEALTH_CHAIN_ENABLED", "true").lower() not in (
      "0", "false", "no",
    )
    self.max_deep_chains_per_day: int = int(os.environ.get("MAX_DEEP_CHAINS_PER_DAY", "3"))
    self.database_url: Optional[str] = os.environ.get("DATABASE_URL")
    self.redis_url: Optional[str] = os.environ.get("REDIS_URL")
    self.admin_token: Optional[str] = os.environ.get("ADMIN_TOKEN")

  @staticmethod
  def _parse_origins(raw: str) -> List[str]:
    origins: List[str] = []
    for part in raw.split(","):
      origin = part.strip()
      if not origin:
        continue
      if not origin.startswith(("http://", "https://")):
        origin = f"https://{origin}"
      origins.append(origin.rstrip("/"))
    return origins

  @property
  def gemini_configured(self) -> bool:
    return bool(self.gemini_api_key)
