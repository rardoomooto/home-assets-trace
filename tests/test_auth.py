import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    # Register a new user
    reg_resp = await client.post(
        "/api/auth/register",
        json={"username": "testuser_auth_1", "email": "auth1@example.com", "password": "secret"},
    )
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data.get("id") is not None
    assert reg_data.get("username") == "testuser_auth_1"
    assert reg_data.get("email") == "auth1@example.com"

    # Login with the new user
    login_resp = await client.post(
        "/api/auth/login",
        json={"username": "testuser_auth_1", "password": "secret"},
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Access current user info
    me_resp = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data.get("username") == "testuser_auth_1"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    # Attempt login with non-existent user
    resp = await client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "nope"},
    )
    assert resp.status_code in (401, 422)  # depending on validation vs auth
