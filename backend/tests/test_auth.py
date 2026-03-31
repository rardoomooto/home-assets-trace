import pytest
from app.models import User
from app.auth import get_password_hash


class TestAuthAPI:
    """Test authentication endpoints"""

    def test_register_success(self, client):
        """Test user registration"""
        response = client.post(
            "/api/auth/register",
            json={"username": "newuser", "email": "new@example.com", "password": "secret123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username"""
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "email": "another@example.com", "password": "secret"}
        )
        assert response.status_code == 400

    def test_login_success(self, client, test_user):
        """Test login with valid credentials"""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpass"}
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/auth/login",
            json={"username": "ghost", "password": "nope"}
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info"""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_get_current_user_unauthorized(self, client):
        """Test getting user info without token"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
