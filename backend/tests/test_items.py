import pytest
from app.models import User, Room, Item
from app.auth import get_password_hash, create_access_token
from conftest import TestingSessionLocal


@pytest.fixture
def test_items(test_user, test_rooms):
    """Create test items in different rooms"""
    db = TestingSessionLocal()
    items = [
        Item(
            name="Sofa",
            quantity=1,
            price=100.0,
            user_id=test_user.id,
            room_id=test_rooms["living_room"].id
        ),
        Item(
            name="TV",
            quantity=1,
            price=200.0,
            user_id=test_user.id,
            room_id=test_rooms["living_room"].id
        ),
        Item(
            name="Bed",
            quantity=1,
            price=300.0,
            user_id=test_user.id,
            room_id=test_rooms["bedroom"].id
        ),
        Item(
            name="Desk",
            quantity=1,
            price=150.0,
            user_id=test_user.id,
            room_id=None  # Item without a room
        ),
    ]
    for item in items:
        db.add(item)
    db.commit()
    for item in items:
        db.refresh(item)
    db.close()
    return items


class TestItemRoomFilter:
    """Tests for room_id filter on items endpoint"""

    def test_filter_items_by_room_id(self, client, test_items, test_rooms, auth_headers):
        """Test filtering items by room_id returns only items in that room"""
        living_room_id = test_rooms["living_room"].id
        response = client.get(f"/api/items?room_id={living_room_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        item_names = [item["name"] for item in data["items"]]
        assert "Sofa" in item_names
        assert "TV" in item_names
        assert "Bed" not in item_names
        assert "Desk" not in item_names

    def test_filter_items_by_room_id_bedroom(self, client, test_items, test_rooms, auth_headers):
        """Test filtering items by bedroom room_id"""
        bedroom_id = test_rooms["bedroom"].id
        response = client.get(f"/api/items?room_id={bedroom_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Bed"

    def test_filter_items_by_room_id_empty(self, client, test_user, auth_headers):
        """Test filtering by room_id that has no items returns empty list"""
        db = TestingSessionLocal()
        empty_room = Room(name="Empty Room", user_id=test_user.id)
        db.add(empty_room)
        db.commit()
        db.refresh(empty_room)
        empty_room_id = empty_room.id
        db.close()
        
        response = client.get(f"/api/items?room_id={empty_room_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_filter_items_without_room(self, client, test_items, auth_headers):
        """Test getting all items without room filter includes items with no room"""
        response = client.get("/api/items", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4  # All 4 items
        item_names = [item["name"] for item in data["items"]]
        assert "Desk" in item_names  # Item with no room should be included

    def test_filter_items_by_room_id_unauthorized(self, client, test_rooms):
        """Test filtering without authentication returns 401"""
        living_room_id = test_rooms["living_room"].id
        response = client.get(f"/api/items?room_id={living_room_id}")
        
        assert response.status_code == 401

    def test_filter_items_by_room_id_wrong_user(self, client, test_items, test_rooms, test_user):
        """Test that user cannot see another user's items even with correct room_id"""
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
        other_user_id = other_user.id
        db.close()
        
        # Use other_user's token
        token = create_access_token(data={"sub": str(other_user_id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        living_room_id = test_rooms["living_room"].id
        response = client.get(f"/api/items?room_id={living_room_id}", headers=headers)
        
        # Should return empty because other_user has no items in that room
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0


class TestItemPaginationWithRoomFilter:
    """Tests for pagination combined with room_id filter"""

    def test_pagination_with_room_filter(self, client, test_items, test_rooms, auth_headers):
        """Test that pagination works correctly with room_id filter"""
        living_room_id = test_rooms["living_room"].id
        
        # Get first page with limit 1
        response = client.get(
            f"/api/items?room_id={living_room_id}&skip=0&limit=1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # Total items in room
        assert len(data["items"]) == 1  # Only 1 item returned due to limit

    def test_skip_with_room_filter(self, client, test_items, test_rooms, auth_headers):
        """Test that skip works correctly with room_id filter"""
        living_room_id = test_rooms["living_room"].id
        
        # Skip first item
        response = client.get(
            f"/api/items?room_id={living_room_id}&skip=1&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 1  # Only second item after skip
