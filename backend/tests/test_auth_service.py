from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.models.user import User, UserRole
from app.schemas.user_schema import UserCreate
from app.services import auth_service


def test_get_user_by_email_returns_user():
    db = MagicMock()
    expected_user = User(
        name="Test Farmer",
        email="farmer@example.com",
        hashed_password="hashed-password",
        phone="9876543210",
        role=UserRole.FARMER,
    )

    db.query.return_value.filter.return_value.first.return_value = expected_user

    result = auth_service.get_user_by_email(db, "farmer@example.com")

    assert result is expected_user
    db.query.assert_called_once_with(auth_service.User)


@pytest.mark.parametrize("role", [UserRole.FARMER, UserRole.OWNER])
def test_register_user_creates_requested_public_role(role):
    db = MagicMock()

    # No existing user
    db.query.return_value.filter.return_value.first.return_value = None

    user_data = UserCreate(
        name="Test Farmer",
        email="farmer@example.com",
        password="password123",
        phone="9876543210",
        role=role,
    )

    with patch(
        "app.services.auth_service.hash_password",
        return_value="hashed-password",
    ):
        result = auth_service.register_user(db, user_data)

    assert result is not None
    assert result.name == "Test Farmer"
    assert result.email == "farmer@example.com"
    assert result.phone == "9876543210"
    assert result.role == role
    assert result.hashed_password == "hashed-password"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_register_user_returns_none_for_existing_email():
    db = MagicMock()

    existing_user = User(
        name="Existing Farmer",
        email="farmer@example.com",
        hashed_password="hashed-password",
        phone="9876543210",
        role=UserRole.FARMER,
    )

    db.query.return_value.filter.return_value.first.return_value = existing_user

    user_data = UserCreate(
        name="Test Farmer",
        email="farmer@example.com",
        password="password123",
        phone="9876543210",
        role=UserRole.FARMER,
    )

    result = auth_service.register_user(db, user_data)

    assert result is None
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_register_user_rejects_admin_role():
    db = MagicMock()
    user_data = UserCreate(
        name="Admin Attempt",
        email="admin@example.com",
        password="password123",
        phone="9876543210",
        role=UserRole.ADMIN,
    )

    with pytest.raises(ValueError, match="Only farmer and owner"):
        auth_service.register_user(db, user_data)

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_login_user_returns_none_when_user_does_not_exist():
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    result = auth_service.login_user(
        db,
        "missing@example.com",
        "password123",
    )

    assert result is None


def test_login_user_returns_none_for_invalid_password():
    db = MagicMock()

    user = User(
        name="Test Farmer",
        email="farmer@example.com",
        hashed_password="hashed-password",
        phone="9876543210",
        role=UserRole.FARMER,
    )

    db.query.return_value.filter.return_value.first.return_value = user

    with patch(
        "app.services.auth_service.verify_password",
        return_value=False,
    ):
        result = auth_service.login_user(
            db,
            "farmer@example.com",
            "wrong-password",
        )

    assert result is None


def test_login_user_returns_access_token_for_valid_credentials():
    db = MagicMock()

    user = User(
        name="Test Farmer",
        email="farmer@example.com",
        hashed_password="hashed-password",
        phone="9876543210",
        role=UserRole.FARMER,
    )

    db.query.return_value.filter.return_value.first.return_value = user

    with patch(
        "app.services.auth_service.verify_password",
        return_value=True,
    ), patch(
        "app.services.auth_service.create_access_token",
        return_value="test-access-token",
    ) as create_token:

        result = auth_service.login_user(
            db,
            "farmer@example.com",
            "password123",
        )

    assert result == "test-access-token"
    create_token.assert_called_once_with(
        data={"sub": "farmer@example.com"}
    )


def test_create_password_reset_token_stores_only_hash():
    db = MagicMock()
    user = SimpleNamespace(id="user-id")

    with patch(
        "app.services.auth_service.secrets.token_urlsafe",
        return_value="secure-reset-token",
    ):
        token = auth_service.create_password_reset_token(db, user)

    stored_token = db.add.call_args.args[0]
    assert token == "secure-reset-token"
    assert stored_token.token_hash == auth_service.hash_reset_token(token)
    assert stored_token.token_hash != token
    assert stored_token.expires_at > auth_service.utc_now()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(stored_token)


def test_reset_password_updates_bcrypt_hash_and_invalidates_token():
    db = MagicMock()
    user = SimpleNamespace(id="user-id", hashed_password=auth_service.hash_password("old-password"))
    reset_token = SimpleNamespace(
        user_id="user-id",
        used_at=None,
        expires_at=auth_service.utc_now() + timedelta(minutes=5),
    )
    db.query.side_effect = [
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=reset_token)))),
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=user)))),
    ]

    assert auth_service.reset_password(db, "valid-token", "new-password") is True
    assert reset_token.used_at is not None
    assert auth_service.verify_password("new-password", user.hashed_password)
    assert not auth_service.verify_password("old-password", user.hashed_password)
    db.commit.assert_called_once()


@pytest.mark.parametrize(
    "used_at, expires_at",
    [
        (None, auth_service.utc_now() - timedelta(minutes=1)),
        (auth_service.utc_now(), auth_service.utc_now() + timedelta(minutes=5)),
    ],
)
def test_reset_password_rejects_expired_or_reused_token(used_at, expires_at):
    db = MagicMock()
    reset_token = SimpleNamespace(used_at=used_at, expires_at=expires_at)
    db.query.return_value.filter.return_value.first.return_value = reset_token

    assert auth_service.reset_password(db, "invalid-token", "new-password") is False
    db.commit.assert_not_called()


def test_reset_password_rejects_unknown_token():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    assert auth_service.reset_password(db, "invalid-token", "new-password") is False
    db.commit.assert_not_called()
