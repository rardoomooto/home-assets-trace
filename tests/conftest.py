import os
import sys
import pathlib
import pytest_asyncio

# Ensure the backend package (which uses absolute imports like `from app...`) is on sys.path
# so tests can import `backend.app.*` modules as `app.*` from the inside.
ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from httpx import AsyncClient, ASGITransport  # imported here to avoid top-level import side-effects


@pytest.fixture(autouse=True)
def _reset_db():
    # Lazy import to avoid circular imports during test collection
    from app.database import engine, Base
    # Re-create tables for each test to ensure isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture
async def client():
    # Import app lazily to ensure environment is prepared (DATABASE_URL set)
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
