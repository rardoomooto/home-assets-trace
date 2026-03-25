import pytest


@pytest.mark.asyncio
async def test_get_rooms_list_format(client):
    """Test that GET /rooms returns rooms in { rooms, total } format.
    
    This test prevents regression where the API response format changes
    and breaks the frontend room list display.
    """
    # Register and login a user
    reg = await client.post(
        "/api/auth/register",
        json={"username": "testuser_rooms", "email": "rooms@example.com", "password": "secret"},
    )
    assert reg.status_code == 200
    login = await client.post(
        "/api/auth/login",
        json={"username": "testuser_rooms", "password": "secret"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create rooms
    room1 = await client.post("/api/rooms", json={"name": "Living Room"}, headers=headers)
    assert room1.status_code == 201
    room2 = await client.post("/api/rooms", json={"name": "Bedroom"}, headers=headers)
    assert room2.status_code == 201

    # Get rooms list - critical test for format consistency
    response = await client.get("/api/rooms", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    # 关键断言：确保返回格式是 { rooms: [...], total: number }
    assert "rooms" in data, "Response must contain 'rooms' key"
    assert "total" in data, "Response must contain 'total' key"
    assert isinstance(data["rooms"], list), "rooms must be a list"
    assert isinstance(data["total"], int), "total must be an integer"
    
    # 验证房间数据完整性
    rooms = data["rooms"]
    assert len(rooms) == 2
    assert data["total"] == 2
    
    # 验证每个房间都有 name 字段
    for room in rooms:
        assert "id" in room
        assert "name" in room
        assert room["name"] in ["Living Room", "Bedroom"]


@pytest.mark.asyncio
async def test_get_rooms_empty_list(client):
    """Test GET /rooms returns empty list when user has no rooms."""
    # Register and login a user
    reg = await client.post(
        "/api/auth/register",
        json={"username": "testuser_empty", "email": "empty@example.com", "password": "secret"},
    )
    assert reg.status_code == 200
    login = await client.post(
        "/api/auth/login",
        json={"username": "testuser_empty", "password": "secret"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get rooms without creating any
    response = await client.get("/api/rooms", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "rooms" in data
    assert "total" in data
    assert data["rooms"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_room_success(client):
    """Test POST /rooms creates a room successfully."""
    reg = await client.post(
        "/api/auth/register",
        json={"username": "testuser_create", "email": "create@example.com", "password": "secret"},
    )
    assert reg.status_code == 200
    login = await client.post(
        "/api/auth/login",
        json={"username": "testuser_create", "password": "secret"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/api/rooms", json={"name": "Kitchen"}, headers=headers)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["name"] == "Kitchen"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_update_room_success(client):
    """Test PUT /rooms/{id} updates a room successfully."""
    reg = await client.post(
        "/api/auth/register",
        json={"username": "testuser_update", "email": "update@example.com", "password": "secret"},
    )
    assert reg.status_code == 200
    login = await client.post(
        "/api/auth/login",
        json={"username": "testuser_update", "password": "secret"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create room
    create = await client.post("/api/rooms", json={"name": "Old Name"}, headers=headers)
    assert create.status_code == 201
    room_id = create.json()["id"]

    # Update room
    response = await client.put(f"/api/rooms/{room_id}", json={"name": "New Name"}, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == room_id
    assert data["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_room_success(client):
    """Test DELETE /rooms/{id} deletes a room successfully."""
    reg = await client.post(
        "/api/auth/register",
        json={"username": "testuser_delete", "email": "delete@example.com", "password": "secret"},
    )
    assert reg.status_code == 200
    login = await client.post(
        "/api/auth/login",
        json={"username": "testuser_delete", "password": "secret"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create room
    create = await client.post("/api/rooms", json={"name": "To Delete"}, headers=headers)
    assert create.status_code == 201
    room_id = create.json()["id"]

    # Delete room
    response = await client.delete(f"/api/rooms/{room_id}", headers=headers)
    assert response.status_code == 204

    # Verify room is deleted
    list_response = await client.get("/api/rooms", headers=headers)
    data = list_response.json()
    assert data["total"] == 0