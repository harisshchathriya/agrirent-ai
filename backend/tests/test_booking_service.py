from datetime import date, timedelta
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment
from app.models.user import User, UserRole
from app.schemas.booking_schema import BookingCreate, BookingStatusUpdate
from app.services import booking_service


def make_user(
    user_id: UUID | None = None,
    name: str = "Test Farmer",
) -> User:
    return User(
        id=user_id or uuid4(),
        name=name,
        email="farmer@example.com",
        hashed_password="hashed-password",
        phone="9876543210",
        role=UserRole.FARMER,
    )


def make_equipment(
    equipment_id: UUID | None = None,
    owner_id: UUID | None = None,
    price_per_day: float = 1000,
    availability: bool = True,
) -> Equipment:
    return Equipment(
        id=equipment_id or uuid4(),
        owner_id=owner_id or uuid4(),
        name="Tractor",
        category="Tractor",
        description="Agricultural tractor",
        location="Trichy",
        price_per_day=price_per_day,
        availability=availability,
    )


def make_booking(
    equipment_id: UUID | None = None,
    renter_id: UUID | None = None,
    status: BookingStatus = BookingStatus.PENDING,
) -> Booking:
    return Booking(
        id=uuid4(),
        equipment_id=equipment_id or uuid4(),
        renter_id=renter_id or uuid4(),
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        total_price=1000,
        status=status,
    )


# ============================================================
# CREATE BOOKING
# ============================================================

def test_create_booking_raises_404_when_equipment_missing():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    user = make_user()

    booking_data = BookingCreate(
        equipment_id=uuid4(),
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=3),
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.create_booking(
            db,
            booking_data,
            user,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Equipment not found."


def test_create_booking_rejects_unavailable_equipment():
    db = MagicMock()

    user = make_user()

    equipment = make_equipment(
        owner_id=uuid4(),
        availability=False,
    )

    db.query.return_value.filter.return_value.first.return_value = equipment

    booking_data = BookingCreate(
        equipment_id=equipment.id,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=3),
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.create_booking(
            db,
            booking_data,
            user,
        )

    assert exc.value.status_code == 409


def test_create_booking_rejects_owner():
    db = MagicMock()

    user = make_user()

    equipment = make_equipment(
        owner_id=user.id,
        availability=True,
    )

    db.query.return_value.filter.return_value.first.return_value = equipment

    booking_data = BookingCreate(
        equipment_id=equipment.id,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=3),
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.create_booking(
            db,
            booking_data,
            user,
        )

    assert exc.value.status_code == 403


def test_create_booking_rejects_past_start_date():
    db = MagicMock()

    user = make_user()

    equipment = make_equipment(
        owner_id=uuid4(),
        availability=True,
    )

    db.query.return_value.filter.return_value.first.return_value = equipment

    booking_data = BookingCreate(
        equipment_id=equipment.id,
        start_date=date.today() - timedelta(days=1),
        end_date=date.today() + timedelta(days=2),
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.create_booking(
            db,
            booking_data,
            user,
        )

    assert exc.value.status_code == 422


def test_create_booking_rejects_invalid_date_range():
    db = MagicMock()

    user = make_user()

    equipment = make_equipment(
        owner_id=uuid4(),
        availability=True,
    )

    db.query.return_value.filter.return_value.first.return_value = equipment

    booking_data = BookingCreate(
        equipment_id=equipment.id,
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=2),
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.create_booking(
            db,
            booking_data,
            user,
        )

    assert exc.value.status_code == 422


def test_create_booking_rejects_overlapping_booking():
    db = MagicMock()

    user = make_user()

    equipment = make_equipment(
        owner_id=uuid4(),
        availability=True,
    )

    existing_booking = make_booking(
        equipment_id=equipment.id,
        status=BookingStatus.APPROVED,
    )

    first_query = db.query.return_value
    first_query.filter.return_value.first.return_value = equipment

    second_query = MagicMock()
    second_query.filter.return_value.first.return_value = existing_booking

    db.query.side_effect = [
        first_query,
        second_query,
    ]

    booking_data = BookingCreate(
        equipment_id=equipment.id,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=3),
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.create_booking(
            db,
            booking_data,
            user,
        )

    assert exc.value.status_code == 409


# ============================================================
# GET BOOKINGS
# ============================================================

def test_get_all_bookings_returns_user_bookings():
    db = MagicMock()
    user = make_user()

    bookings = [
        make_booking(renter_id=user.id),
        make_booking(renter_id=user.id),
    ]

    db.query.return_value.options.return_value.filter.return_value.all.return_value = (
        bookings
    )

    result = booking_service.get_all_bookings(db, user)

    assert result == bookings


def test_get_booking_by_id_returns_booking():
    db = MagicMock()

    booking_id = uuid4()
    booking = make_booking()

    db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        booking
    )

    result = booking_service.get_booking_by_id(
        db,
        booking_id,
    )

    assert result == booking


# ============================================================
# RENTER STATUS
# ============================================================

def test_update_booking_status_cancels_pending_booking():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.PENDING,
    )

    db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        booking
    )

    status = BookingStatusUpdate(
        status=BookingStatus.CANCELLED,
    )

    result = booking_service.update_booking_status(
        db,
        booking,
        status,
    )

    assert booking.status == BookingStatus.CANCELLED
    assert result == booking


def test_update_booking_status_rejects_non_cancel_status():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.PENDING,
    )

    status = BookingStatusUpdate(
        status=BookingStatus.APPROVED,
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.update_booking_status(
            db,
            booking,
            status,
        )

    assert exc.value.status_code == 422


# ============================================================
# OWNER HELPERS
# ============================================================

def test_is_equipment_owner_returns_true_for_owner():
    db = MagicMock()

    owner = make_user()

    booking = make_booking()

    equipment = make_equipment(
        equipment_id=booking.equipment_id,
        owner_id=owner.id,
    )

    db.query.return_value.filter.return_value.first.return_value = equipment

    result = booking_service.is_equipment_owner(
        db,
        booking,
        owner,
    )

    assert result is True


def test_is_equipment_owner_returns_false_for_non_owner():
    db = MagicMock()

    owner = make_user()
    other_user = make_user()

    booking = make_booking()

    equipment = make_equipment(
        equipment_id=booking.equipment_id,
        owner_id=owner.id,
    )

    db.query.return_value.filter.return_value.first.return_value = equipment

    result = booking_service.is_equipment_owner(
        db,
        booking,
        other_user,
    )

    assert result is False


def test_is_equipment_owner_returns_false_when_equipment_missing():
    db = MagicMock()

    booking = make_booking()
    user = make_user()

    db.query.return_value.filter.return_value.first.return_value = None

    result = booking_service.is_equipment_owner(
        db,
        booking,
        user,
    )

    assert result is False


def test_get_equipment_from_booking_returns_equipment():
    db = MagicMock()

    booking = make_booking()
    equipment = make_equipment(
        equipment_id=booking.equipment_id,
    )

    db.query.return_value.filter.return_value.first.return_value = equipment

    result = booking_service.get_equipment_from_booking(
        db,
        booking,
    )

    assert result == equipment


# ============================================================
# APPROVE BOOKING
# ============================================================

def test_approve_booking_changes_status_and_unavailable_equipment():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.PENDING,
    )

    equipment = make_equipment(
        equipment_id=booking.equipment_id,
        availability=True,
    )

    query = db.query.return_value

    first_call = MagicMock()
    first_call.filter.return_value.first.return_value = equipment

    second_call = MagicMock()
    second_call.options.return_value.filter.return_value.first.return_value = booking

    db.query.side_effect = [
        first_call,
        second_call,
    ]

    result = booking_service.approve_booking(
        db,
        booking,
    )

    assert booking.status == BookingStatus.APPROVED
    assert equipment.availability is False
    assert result == booking


def test_approve_booking_rejects_non_pending_booking():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.APPROVED,
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.approve_booking(
            db,
            booking,
        )

    assert exc.value.status_code == 409


# ============================================================
# REJECT BOOKING
# ============================================================

def test_reject_booking_changes_status():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.PENDING,
    )

    db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        booking
    )

    result = booking_service.reject_booking(
        db,
        booking,
    )

    assert booking.status == BookingStatus.REJECTED
    assert result == booking


def test_reject_booking_rejects_non_pending_booking():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.APPROVED,
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.reject_booking(
            db,
            booking,
        )

    assert exc.value.status_code == 409


# ============================================================
# COMPLETE BOOKING
# ============================================================

def test_complete_booking_changes_status_and_releases_equipment():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.APPROVED,
    )

    equipment = make_equipment(
        equipment_id=booking.equipment_id,
        availability=False,
    )

    first_query = MagicMock()
    first_query.filter.return_value.first.return_value = equipment

    second_query = MagicMock()
    second_query.options.return_value.filter.return_value.first.return_value = booking

    db.query.side_effect = [
        first_query,
        second_query,
    ]

    result = booking_service.complete_booking(
        db,
        booking,
    )

    assert booking.status == BookingStatus.COMPLETED
    assert equipment.availability is True
    assert result == booking


def test_complete_booking_rejects_non_approved_booking():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.PENDING,
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.complete_booking(
            db,
            booking,
        )

    assert exc.value.status_code == 409


# ============================================================
# CANCEL BOOKING
# ============================================================

def test_cancel_booking_changes_status_and_releases_equipment():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.APPROVED,
    )

    equipment = make_equipment(
        equipment_id=booking.equipment_id,
        availability=False,
    )

    first_query = MagicMock()
    first_query.filter.return_value.first.return_value = equipment

    second_query = MagicMock()
    second_query.options.return_value.filter.return_value.first.return_value = booking

    db.query.side_effect = [
        first_query,
        second_query,
    ]

    result = booking_service.cancel_booking(
        db,
        booking,
    )

    assert booking.status == BookingStatus.CANCELLED
    assert equipment.availability is True
    assert result == booking


def test_cancel_booking_rejects_completed_booking():
    db = MagicMock()

    booking = make_booking(
        status=BookingStatus.COMPLETED,
    )

    with pytest.raises(HTTPException) as exc:
        booking_service.cancel_booking(
            db,
            booking,
        )

    assert exc.value.status_code == 409
