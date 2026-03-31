import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate


class TestUserSchemas:
    """Test Pydantic schemas validation"""

    def test_user_create_valid(self):
        """Test valid user creation schema"""
        user = UserCreate(
            username="validuser",
            email="valid@example.com",
            password="secret123"
        )
        assert user.username == "validuser"
        assert user.email == "valid@example.com"

    def test_user_create_invalid_email(self):
        """Test user creation with invalid email"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="baduser",
                email="not-an-email",
                password="secret"
            )

    def test_user_create_missing_fields(self):
        """Test user creation with missing required fields"""
        with pytest.raises(ValidationError):
            UserCreate(username="incomplete")
