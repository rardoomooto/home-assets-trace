import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import User, Room, Item, Family, FamilyMember
from app.auth import get_password_hash, create_access_token


# Create in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Provide a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


@pytest.fixture
def auth_headers(test_user):
    """Provide authentication headers for test user"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_room(test_user):
    """Create a test room"""
    db = TestingSessionLocal()
    room = Room(name="Test Room", user_id=test_user.id)
    db.add(room)
    db.commit()
    db.refresh(room)
    db.close()
    return room


@pytest.fixture
def test_rooms(test_user):
    """Create multiple test rooms"""
    db = TestingSessionLocal()
    room1 = Room(name="Living Room", user_id=test_user.id)
    room2 = Room(name="Bedroom", user_id=test_user.id)
    db.add(room1)
    db.add(room2)
    db.commit()
    db.refresh(room1)
    db.refresh(room2)
    db.close()
    return {"living_room": room1, "bedroom": room2}
