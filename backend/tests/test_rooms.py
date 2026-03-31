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


class TestRoomCRUD:
    """Test room CRUD operations"""

    def test_get_rooms_list_format(self, client, auth_headers):
        """Test GET /rooms returns rooms in { rooms, total } format"""
        # Create rooms
        client.post("/api/rooms", json={"name": "Living Room"}, headers=auth_headers)
        client.post("/api/rooms", json={"name": "Bedroom"}, headers=auth_headers)

        # Get rooms list
        response = client.get("/api/rooms", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "rooms" in data, "Response must contain 'rooms' key"
        assert "total" in data, "Response must contain 'total' key"
        assert isinstance(data["rooms"], list)
        assert isinstance(data["total"], int)
        assert data["total"] == 2
        
        # Verify room data
        rooms = data["rooms"]
        assert len(rooms) == 2
        for room in rooms:
            assert "id" in room
            assert "name" in room
            assert room["name"] in ["Living Room", "Bedroom"]

    def test_get_rooms_empty_list(self, client, auth_headers):
        """Test GET /rooms returns empty list when user has no rooms"""
        response = client.get("/api/rooms", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "rooms" in data
        assert "total" in data
        assert data["rooms"] == []
        assert data["total"] == 0

    def test_create_room_success(self, client, auth_headers):
        """Test POST /rooms creates a room successfully"""
        response = client.post("/api/rooms", json={"name": "Kitchen"}, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert "id" in data
        assert data["name"] == "Kitchen"
        assert "user_id" in data

    def test_update_room_success(self, client, auth_headers):
        """Test PUT /rooms/{id} updates a room successfully"""
        # Create room
        create = client.post("/api/rooms", json={"name": "Old Name"}, headers=auth_headers)
        assert create.status_code == 201
        room_id = create.json()["id"]

        # Update room
        response = client.put(f"/api/rooms/{room_id}", json={"name": "New Name"}, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == room_id
        assert data["name"] == "New Name"

    def test_delete_room_success(self, client, auth_headers):
        """Test DELETE /rooms/{id} deletes a room successfully"""
        # Create room
        create = client.post("/api/rooms", json={"name": "To Delete"}, headers=auth_headers)
        assert create.status_code == 201
        room_id = create.json()["id"]

        # Delete room
        response = client.delete(f"/api/rooms/{room_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify room is deleted
        list_response = client.get("/api/rooms", headers=auth_headers)
        data = list_response.json()
        assert data["total"] == 0


class TestRoomItems:
    """Test room items endpoints"""

    def test_get_room_items(self, client, test_room, test_items, auth_headers):
        response = client.get(f"/api/rooms/{test_room.id}/items", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_room.id
        assert data["name"] == test_room.name
        assert len(data["items"]) == 2
        assert data["items"][0]["name"] == "Item 1"
        assert data["items"][1]["name"] == "Item 2"

    def test_get_room_items_empty(self, client, test_room, auth_headers):
        response = client.get(f"/api/rooms/{test_room.id}/items", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0

    def test_get_room_items_not_found(self, client, auth_headers):
        response = client.get("/api/rooms/999/items", headers=auth_headers)
        assert response.status_code == 404

    def test_get_room_items_unauthorized(self, client, test_room):
        response = client.get(f"/api/rooms/{test_room.id}/items")
        assert response.status_code == 401

    def test_get_room_items_wrong_user(self, client, test_room, test_items):
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