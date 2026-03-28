import pytest
from app.models import User, Room, Item
from app.auth import get_password_hash, create_access_token
from conftest import TestingSessionLocal


@pytest.fixture
def test_items(test_user, test_room):
    """Create test items in a room"""
    db = TestingSessionLocal()
    items = [
        Item(
            name="Item 1",
            quantity=2,
            price=10.0,
            user_id=test_user.id,
            room_id=test_room.id
        ),
        Item(
            name="Item 2",
            quantity=1,
            price=20.0,
            user_id=test_user.id,
            room_id=test_room.id
        ),
    ]
    for item in items:
        db.add(item)
    db.commit()
    for item in items:
        db.refresh(item)
    db.close()
    return items


def test_get_room_items(client, test_room, test_items, auth_headers):
    response = client.get(f"/api/rooms/{test_room.id}/items", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_room.id
    assert data["name"] == test_room.name
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Item 1"
    assert data["items"][1]["name"] == "Item 2"


def test_get_room_items_empty(client, test_room, auth_headers):
    response = client.get(f"/api/rooms/{test_room.id}/items", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0


def test_get_room_items_not_found(client, auth_headers):
    response = client.get("/api/rooms/999/items", headers=auth_headers)
    assert response.status_code == 404


def test_get_room_items_unauthorized(client, test_room):
    response = client.get(f"/api/rooms/{test_room.id}/items")
    assert response.status_code == 401


def test_get_room_items_wrong_user(client, test_room, test_items):
    # Create another user
    db = TestingSessionLocal()
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password=get_password_hash("otherpass")
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    db.close()
    
    token = create_access_token(data={"sub": str(other_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"/api/rooms/{test_room.id}/items", headers=headers)
    assert response.status_code == 404