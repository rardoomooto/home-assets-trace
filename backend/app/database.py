from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.pool import StaticPool

from app.config import settings

# Only create directory for file-based SQLite databases (not in-memory)
if not settings.DATABASE_URL.startswith("sqlite:///:memory:"):
    db_path = settings.DATABASE_URL.replace("sqlite:///./", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

# For in-memory SQLite used in tests, ensure a single persistent connection
# so that the in-memory database persists across sessions.
engine_kwargs = {
    "connect_args": {"check_same_thread": False}
}
if settings.DATABASE_URL.startswith("sqlite:///:memory:") or settings.DATABASE_URL == "sqlite:///:memory:":
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
