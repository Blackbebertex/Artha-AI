"""PostgreSQL models and session — optional when DATABASE_URL is set."""
import os
from typing import Optional

_engine = None
_SessionLocal = None


def get_database_url() -> Optional[str]:
    return os.environ.get("DATABASE_URL")


def init_db():
    global _engine, _SessionLocal
    url = get_database_url()
    if not url:
        return False
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        _engine = create_engine(url)
        _SessionLocal = sessionmaker(bind=_engine)
        from services.db_models import Base
        Base.metadata.create_all(_engine)
        return True
    except Exception as e:
        print(f"[DB] init failed: {e}")
        return False


def get_db_session():
    if _SessionLocal is None:
        init_db()
    if _SessionLocal is None:
        return None
    return _SessionLocal()
