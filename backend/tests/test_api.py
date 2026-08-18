from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api import auth as auth_api
from app.api import booking as booking_api
from app.api import equipment as equipment_api
from app.api import equipment_relations as relations_api
from app.core.security import get_current_user
from app.database.session import get_db
from app.main import app


def make_user(user_id=None):
    return SimpleNamespace(
        id=user_id or uuid4(),
        name="Test User",
        email="user@example.com",
        phone="9876543210",
        role="farmer",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
    )


def make_equipment(owner_id=None):
    return SimpleNamespace(
        id=uuid4(), owner_id=owner_id or uuid4(), owner_name="Equipment Owner",
        name="Tractor", category="Tractor", description="Reliable tractor",
        price_per_day=2500.0, location="Trichy", availability=True, image_url=None,
        created_at=datetime(2026, 1, 1, 12, 0, 0),
    )


def make_booking(renter_id=None, equipment_id=None, status="pending"):
    renter_id = renter_id or uuid4()
    return SimpleNamespace(
        id=uuid4(), equipment_id=equipment_id or uuid4(), farmer_id=renter_id,
        renter_id=renter_id, renter_name="Test Renter", owner_name="Equipment Owner",
        owner_email="owner@example.com", equipment_name="Tractor", category="Tractor",
        location="Trichy", price_per_day=2500.0, start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 3), total_price=7500.0, status=status,
    )


@pytest.fixture
def client():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client, db
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client):
    test_client, db = client
    user = make_user()
    app.dependency_overrides[get_current_user] = lambda: user
    return test_client, db, user


def test_register_success_returns_public_user_response(client, monkeypatch):
    test_client, db = client
    service = MagicMock(return_value=make_user())
    monkeypatch.setattr(auth_api, "register_user", service)

    response = test_client.post("/auth/register", json={
        "name": "Test User", "email": "user@example.com", "password": "safe-password",
        "phone": "9876543210", "role": "farmer",
    })

    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
    assert "hashed_password" not in response.json()
    assert service.call_args.args[0] is db


def test_register_rejects_invalid_body_before_service(client, monkeypatch):
    test_client, _ = client
    service = MagicMock()
    monkeypatch.setattr(auth_api, "register_user", service)

    assert test_client.post("/auth/register", json={"name": "Test User"}).status_code == 422
    service.assert_not_called()


def test_register_returns_bad_request_for_duplicate_email(client, monkeypatch):
    test_client, _ = client
    monkeypatch.setattr(auth_api, "register_user", MagicMock(return_value=None))

    response = test_client.post("/auth/register", json={
        "name": "Test User", "email": "user@example.com", "password": "safe-password",
        "phone": "9876543210", "role": "farmer",
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_success_returns_bearer_token(client, monkeypatch):
    test_client, db = client
    service = MagicMock(return_value="test-access-token")
    monkeypatch.setattr(auth_api, "login_user", service)

    response = test_client.post("/auth/login", data={
        "username": "user@example.com", "password": "safe-password",
    })

    assert response.status_code == 200
    assert response.json() == {"access_token": "test-access-token", "token_type": "bearer"}
    service.assert_called_once_with(db, "user@example.com", "safe-password")


def test_login_rejects_invalid_credentials(client, monkeypatch):
    test_client, _ = client
    monkeypatch.setattr(auth_api, "login_user", MagicMock(return_value=None))

    response = test_client.post("/auth/login", data={"username": "user@example.com", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_current_user_requires_authentication(client):
    test_client, _ = client
    response = test_client.get("/auth/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_current_user_returns_authenticated_user(authenticated_client):
    test_client, _, user = authenticated_client
    response = test_client.get("/auth/users/me")

    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)


def test_create_equipment_success_calls_service(authenticated_client, monkeypatch):
    test_client, db, user = authenticated_client
    service = MagicMock(return_value=make_equipment(user.id))
    monkeypatch.setattr(equipment_api, "create_equipment", service)
    payload = {"name": "Tractor", "category": "Tractor", "description": "Reliable tractor", "price_per_day": 2500, "location": "Trichy"}

    response = test_client.post("/equipment", json=payload)

    assert response.status_code == 200
    assert response.json()["owner_id"] == str(user.id)
    assert service.call_args.args[0] is db
    assert service.call_args.args[2] is user


def test_create_equipment_requires_authentication(client):
    test_client, _ = client
    assert test_client.post("/equipment", json={}).status_code == 401


def test_create_equipment_rejects_missing_fields_before_service(authenticated_client, monkeypatch):
    test_client, _, _ = authenticated_client
    service = MagicMock()
    monkeypatch.setattr(equipment_api, "create_equipment", service)

    assert test_client.post("/equipment", json={"name": "Tractor"}).status_code == 422
    service.assert_not_called()


def test_list_equipment_returns_service_response(client, monkeypatch):
    test_client, db = client
    equipment = make_equipment()
    service = MagicMock(return_value=[equipment])
    monkeypatch.setattr(equipment_api, "get_all_equipment", service)

    response = test_client.get("/equipment")

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(equipment.id)
    service.assert_called_once_with(db)


def test_read_equipment_not_found_and_invalid_id(client, monkeypatch):
    test_client, _ = client
    monkeypatch.setattr(equipment_api, "get_equipment_by_id", MagicMock(return_value=None))

    missing = test_client.get(f"/equipment/{uuid4()}")
    invalid = test_client.get("/equipment/not-a-uuid")

    assert missing.status_code == 404
    assert missing.json()["detail"] == "Equipment not found"
    assert invalid.status_code == 422


def test_update_equipment_rejects_non_owner(authenticated_client, monkeypatch):
    test_client, _, _ = authenticated_client
    equipment = make_equipment()
    monkeypatch.setattr(equipment_api, "get_equipment_by_id", MagicMock(return_value=equipment))
    service = MagicMock()
    monkeypatch.setattr(equipment_api, "update_equipment", service)
    payload = {"name": "Tractor", "category": "Tractor", "description": "Reliable tractor", "price_per_day": 2500, "location": "Trichy"}

    assert test_client.put(f"/equipment/{equipment.id}", json=payload).status_code == 403
    service.assert_not_called()


def test_delete_equipment_owner_deletes_resource(authenticated_client, monkeypatch):
    test_client, db, user = authenticated_client
    equipment = make_equipment(user.id)
    monkeypatch.setattr(equipment_api, "get_equipment_by_id", MagicMock(return_value=equipment))
    service = MagicMock()
    monkeypatch.setattr(equipment_api, "delete_equipment", service)

    response = test_client.delete(f"/equipment/{equipment.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Equipment deleted successfully"
    service.assert_called_once_with(db, equipment)


def test_create_booking_success_calls_service(authenticated_client, monkeypatch):
    test_client, db, user = authenticated_client
    booking = make_booking(renter_id=user.id)
    service = MagicMock(return_value=booking)
    monkeypatch.setattr(booking_api, "create_booking", service)
    payload = {"equipment_id": str(booking.equipment_id), "start_date": "2026-02-01", "end_date": "2026-02-03"}

    response = test_client.post("/bookings", json=payload)

    assert response.status_code == 200
    assert response.json()["renter_id"] == str(user.id)
    assert service.call_args.args[0] is db
    assert service.call_args.args[2] is user


def test_create_booking_requires_authentication(client):
    test_client, _ = client
    assert test_client.post("/bookings", json={}).status_code == 401


def test_create_booking_rejects_invalid_body_before_service(authenticated_client, monkeypatch):
    test_client, _, _ = authenticated_client
    service = MagicMock()
    monkeypatch.setattr(booking_api, "create_booking", service)

    response = test_client.post("/bookings", json={"equipment_id": "not-a-uuid", "start_date": "bad-date"})

    assert response.status_code == 422
    service.assert_not_called()


def test_create_booking_maps_service_conflict(authenticated_client, monkeypatch):
    test_client, _, _ = authenticated_client
    monkeypatch.setattr(booking_api, "create_booking", MagicMock(side_effect=HTTPException(409, "Booking conflict")))

    response = test_client.post("/bookings", json={
        "equipment_id": str(uuid4()), "start_date": "2026-02-01", "end_date": "2026-02-03",
    })

    assert response.status_code == 409
    assert response.json()["detail"] == "Booking conflict"


def test_read_booking_handles_not_found_and_unauthorized(authenticated_client, monkeypatch):
    test_client, _, _ = authenticated_client
    lookup = MagicMock(return_value=None)
    monkeypatch.setattr(booking_api, "get_booking_by_id", lookup)
    assert test_client.get(f"/bookings/{uuid4()}").status_code == 404

    booking = make_booking()
    lookup.return_value = booking
    monkeypatch.setattr(booking_api, "is_equipment_owner", MagicMock(return_value=False))
    response = test_client.get(f"/bookings/{booking.id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "You are not allowed to view this booking."


def test_owner_approval_authorizes_owner_and_rejects_non_owner(authenticated_client, monkeypatch):
    test_client, db, _ = authenticated_client
    booking = make_booking()
    approved = make_booking(booking.renter_id, booking.equipment_id, "approved")
    approved.id = booking.id
    monkeypatch.setattr(booking_api, "get_booking_by_id", MagicMock(return_value=booking))
    ownership = MagicMock(return_value=True)
    monkeypatch.setattr(booking_api, "is_equipment_owner", ownership)
    service = MagicMock(return_value=approved)
    monkeypatch.setattr(booking_api, "approve_booking", service)

    allowed = test_client.put(f"/bookings/owner/bookings/{booking.id}/approve")
    ownership.return_value = False
    denied = test_client.put(f"/bookings/owner/bookings/{booking.id}/approve")

    assert allowed.status_code == 200
    assert allowed.json()["status"] == "approved"
    service.assert_called_once_with(db, booking)
    assert denied.status_code == 403


def test_read_images_returns_service_response(client, monkeypatch):
    test_client, db = client
    equipment_id = uuid4()
    image = SimpleNamespace(id=uuid4(), equipment_id=equipment_id, image_url="https://example.com/tractor.jpg", created_at=datetime(2026, 1, 1, 12, 0, 0))
    service = MagicMock(return_value=[image])
    monkeypatch.setattr(relations_api, "get_images", service)

    response = test_client.get(f"/equipment/{equipment_id}/images")

    assert response.status_code == 200
    assert response.json()[0]["image_url"] == image.image_url
    service.assert_called_once_with(db, equipment_id)


def test_create_image_requires_authentication(client):
    test_client, _ = client
    response = test_client.post(f"/equipment/{uuid4()}/images", json={"image_url": "https://example.com/tractor.jpg"})

    assert response.status_code == 401


def test_create_image_rejects_blank_url_before_service(authenticated_client, monkeypatch):
    test_client, _, _ = authenticated_client
    service = MagicMock()
    monkeypatch.setattr(relations_api, "add_image", service)

    assert test_client.post(f"/equipment/{uuid4()}/images", json={"image_url": ""}).status_code == 422
    service.assert_not_called()


def test_create_review_maps_service_authorization_error(authenticated_client, monkeypatch):
    test_client, _, _ = authenticated_client
    monkeypatch.setattr(relations_api, "add_review", MagicMock(side_effect=HTTPException(
        403, "Only renters with a completed booking can review this equipment."
    )))

    response = test_client.post(f"/equipment/{uuid4()}/reviews", json={"rating": 5, "comment": "Excellent tractor."})

    assert response.status_code == 403
    assert response.json()["detail"] == "Only renters with a completed booking can review this equipment."


def test_create_review_rejects_out_of_range_rating(authenticated_client, monkeypatch):
    test_client, _, _ = authenticated_client
    service = MagicMock()
    monkeypatch.setattr(relations_api, "add_review", service)

    assert test_client.post(f"/equipment/{uuid4()}/reviews", json={"rating": 6, "comment": "Excellent tractor."}).status_code == 422
    service.assert_not_called()
