from unittest.mock import MagicMock, patch

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


def test_register_user_creates_new_user():
    db = MagicMock()

    # No existing user
    db.query.return_value.filter.return_value.first.return_value = None

    user_data = UserCreate(
        name="Test Farmer",
        email="farmer@example.com",
        password="password123",
        phone="9876543210",
        role="farmer",
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
    assert result.role == UserRole.FARMER
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
        role="farmer",
    )

    result = auth_service.register_user(db, user_data)

    assert result is None
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
