import pytest
from pydantic import ValidationError


def test_user_create_valid_schema():
    from app.schemas.user import UserCreate

    user = UserCreate(username="schema_user", email="schema@example.com", password="secret")
    assert user.username == "schema_user"
    assert user.email == "schema@example.com"


def test_user_create_invalid_email_raises():
    from app.schemas.user import UserCreate

    with pytest.raises(ValidationError):
        UserCreate(username="bad", email="not-an-email", password="secret")
