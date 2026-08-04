from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment
from app.models.user import User

from app.schemas.booking_schema import (
    BookingCreate,
    BookingStatusUpdate,
)


# ---------------------------------------------------
# CREATE BOOKING
# ---------------------------------------------------
def create_booking(
    db: Session,
    booking: BookingCreate,
    current_user: User,
):
    equipment = (
        db.query(Equipment)
        .filter(Equipment.id == booking.equipment_id)
        .first()
    )

    # Equipment not found
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This equipment no longer exists.",
        )

    # Equipment unavailable
    if not equipment.availability:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This equipment is currently unavailable for booking.",
        )

    # Cannot rent own equipment
    if equipment.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot book your own equipment.",
        )

    # Past date
    if booking.start_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Start date cannot be before today ({date.today()})."
            ),
        )

    # Invalid date range
    if booking.end_date < booking.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="End date must be on or after the start date.",
        )

    # Prevent overlapping bookings
    existing_booking = (
        db.query(Booking)
        .filter(
            Booking.equipment_id == booking.equipment_id,
            Booking.status.in_(
                [
                    BookingStatus.PENDING,
                    BookingStatus.APPROVED,
                ]
            ),
            and_(
                Booking.start_date <= booking.end_date,
                Booking.end_date >= booking.start_date,
            ),
        )
        .first()
    )

    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="These dates overlap with an existing booking.",
        )

    # Calculate total price
    days = (booking.end_date - booking.start_date).days + 1
    total_price = float(equipment.price_per_day) * days

    new_booking = Booking(
        equipment_id=booking.equipment_id,
        renter_id=current_user.id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        total_price=total_price,
        status=BookingStatus.PENDING,
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


# ---------------------------------------------------
# RENTER FUNCTIONS
# ---------------------------------------------------
def get_all_bookings(
    db: Session,
    current_user: User,
):
    return (
        db.query(Booking)
        .filter(Booking.renter_id == current_user.id)
        .all()
    )


def get_booking_by_id(
    db: Session,
    booking_id: UUID,
):
    return (
        db.query(Booking)
        .filter(Booking.id == booking_id)
        .first()
    )


def update_booking_status(
    db: Session,
    booking: Booking,
    status_update: BookingStatusUpdate,
):
    if status_update.status != BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only booking cancellation is allowed from this endpoint.",
        )

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending bookings can be cancelled.",
        )

    booking.status = BookingStatus(status_update.status)
    db.commit()
    db.refresh(booking)
    return booking


def delete_booking(
    db: Session,
    booking: Booking,
):
    db.delete(booking)
    db.commit()


# ---------------------------------------------------
# OWNER FUNCTIONS
# ---------------------------------------------------
def get_owner_bookings(
    db: Session,
    owner: User,
):
    return (
        db.query(Booking)
        .join(Equipment, Booking.equipment_id == Equipment.id)
        .filter(Equipment.owner_id == owner.id)
        .all()
    )


def get_pending_owner_bookings(
    db: Session,
    owner: User,
):
    return (
        db.query(Booking)
        .join(Equipment, Booking.equipment_id == Equipment.id)
        .filter(
            Equipment.owner_id == owner.id,
            Booking.status == BookingStatus.PENDING,
        )
        .all()
    )


# ---------------------------------------------------
# OWNER AUTHORIZATION HELPERS
# ---------------------------------------------------
def is_equipment_owner(
    db: Session,
    booking: Booking,
    current_user: User,
):
    equipment = (
        db.query(Equipment)
        .filter(Equipment.id == booking.equipment_id)
        .first()
    )
    if equipment is None:
        return False
    return equipment.owner_id == current_user.id


def get_equipment_from_booking(
    db: Session,
    booking: Booking,
):
    return (
        db.query(Equipment)
        .filter(Equipment.id == booking.equipment_id)
        .first()
    )


# ---------------------------------------------------
# APPROVE BOOKING
# ---------------------------------------------------
def approve_booking(
    db: Session,
    booking: Booking,
):
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending bookings can be approved.",
        )

    booking.status = BookingStatus.APPROVED

    equipment = (
        db.query(Equipment)
        .filter(Equipment.id == booking.equipment_id)
        .first()
    )
    if equipment:
        equipment.availability = False

    db.commit()
    db.refresh(booking)
    return booking


# ---------------------------------------------------
# REJECT BOOKING
# ---------------------------------------------------
def reject_booking(
    db: Session,
    booking: Booking,
):
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending bookings can be rejected.",
        )

    booking.status = BookingStatus.REJECTED
    db.commit()
    db.refresh(booking)
    return booking


# ---------------------------------------------------
# COMPLETE BOOKING          <-- NEW
# ---------------------------------------------------
def complete_booking(
    db: Session,
    booking: Booking,
):
    # Only approved bookings can be completed
    if booking.status != BookingStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only approved bookings can be completed.",
        )

    booking.status = BookingStatus.COMPLETED

    equipment = (
        db.query(Equipment)
        .filter(Equipment.id == booking.equipment_id)
        .first()
    )
    if equipment:
        equipment.availability = True

    db.commit()
    db.refresh(booking)
    return booking


# ---------------------------------------------------
# CANCEL BOOKING            <-- NEW
# ---------------------------------------------------
def cancel_booking(
    db: Session,
    booking: Booking,
):
    if booking.status != BookingStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only approved bookings can be cancelled by the owner.",
        )

    booking.status = BookingStatus.CANCELLED

    equipment = (
        db.query(Equipment)
        .filter(Equipment.id == booking.equipment_id)
        .first()
    )
    if equipment:
        equipment.availability = True

    db.commit()
    db.refresh(booking)
    return booking
