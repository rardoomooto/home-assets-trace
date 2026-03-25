import pytest


@pytest.mark.asyncio
async def test_create_item_flow(client):
    # Register a user
    reg = await client.post(
        "/api/auth/register",
        json={"username": "testuser_items", "email": "items1@example.com", "password": "secret"},
    )
    assert reg.status_code == 200
    login = await client.post(
        "/api/auth/login",
        json={"username": "testuser_items", "password": "secret"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Create a category
    cat = await client.post(
        "/api/categories",
        json={"name": "TestCategory"},
        headers=headers,
    )
    assert cat.status_code == 200 or cat.status_code == 201
    cat_id = cat.json()["id"]

    # Create a room
    room = await client.post(
        "/api/rooms",
        json={"name": "Living Room"},
        headers=headers,
    )
    assert room.status_code == 200 or room.status_code == 201
    room_id = room.json()["id"]

    # Create an item with valid category/room
    item = await client.post(
        "/api/items",
        json={
            "name": "Test Lamp",
            "quantity": 1,
            "price": 12.5,
            "category_id": cat_id,
            "room_id": room_id
        },
        headers=headers,
    )
    assert item.status_code == 201
    data = item.json()
    assert data.get("name") == "Test Lamp"
    assert data.get("user_id") is not None


@pytest.mark.asyncio
async def test_create_item_invalid_category(client):
    # Register a user
    reg = await client.post(
        "/api/auth/register",
        json={"username": "testuser_items2", "email": "items2@example.com", "password": "secret"},
    )
    assert reg.status_code == 200
    login = await client.post(
        "/api/auth/login",
        json={"username": "testuser_items2", "password": "secret"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to create an item with a non-existent category
    bad = await client.post(
        "/api/items",
        json={
            "name": "Ghost Item",
            "quantity": 1,
            "price": 1.0,
            "category_id": 99999
        },
        headers=headers,
    )
    assert bad.status_code in (400, 422, 500)
