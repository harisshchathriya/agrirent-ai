from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

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

    if equipment is None:
        raise HTTPException(
            status_code=404,
            detail="Equipment not found.",
        )

    if not equipment.availability:
        raise HTTPException(
            status_code=409,
            detail="This equipment is currently unavailable for booking.",
        )

    if equipment.owner_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot book your own equipment.",
        )

    if booking.start_date < date.today():
        raise HTTPException(
            status_code=422,
            detail="Start date cannot be in the past.",
        )

    if booking.end_date <= booking.start_date:
        raise HTTPException(
            status_code=422,
            detail="End date must be after the start date.",
        )

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
            status_code=409,
            detail="Selected dates overlap with an existing booking for this equipment.",
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

    return get_booking_by_id(db, new_booking.id)


# ---------------------------------------------------
# RENTER FUNCTIONS
# ---------------------------------------------------
def get_all_bookings(
    db: Session,
    current_user: User,
):
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.renter).load_only(User.id, User.name),
            joinedload(Booking.equipment).joinedload(Equipment.owner).load_only(
                User.id,
                User.name,
                User.email,
            ),
        )
        .filter(Booking.renter_id == current_user.id)
        .all()
    )


def get_booking_by_id(
    db: Session,
    booking_id: UUID,
):
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.renter).load_only(User.id, User.name),
            joinedload(Booking.equipment).joinedload(Equipment.owner).load_only(
                User.id,
                User.name,
                User.email,
            ),
        )
        .filter(Booking.id == booking_id)
        .first()
    )


def update_booking_status(
    db: Session,
    booking: Booking,
    status: BookingStatusUpdate,
):
    if status.status != BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=422,
            detail="Renters can only cancel their own bookings.",
        )

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=409,
            detail="Only pending bookings can be cancelled by the renter.",
        )

    booking.status = BookingStatus.CANCELLED
    db.commit()
    return get_booking_by_id(db, booking.id)


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
        .options(
            joinedload(Booking.renter).load_only(User.id, User.name),
            joinedload(Booking.equipment).joinedload(Equipment.owner).load_only(
                User.id,
                User.name,
                User.email,
            ),
        )
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
        .options(
            joinedload(Booking.renter).load_only(User.id, User.name),
            joinedload(Booking.equipment).joinedload(Equipment.owner).load_only(
                User.id,
                User.name,
                User.email,
            ),
        )
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
            status_code=409,
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
    return get_booking_by_id(db, booking.id)


# ---------------------------------------------------
# REJECT BOOKING
# ---------------------------------------------------
def reject_booking(
    db: Session,
    booking: Booking,
):
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=409,
            detail="Only pending bookings can be rejected.",
        )

    booking.status = BookingStatus.REJECTED
    db.commit()
    return get_booking_by_id(db, booking.id)


# ---------------------------------------------------
# COMPLETE BOOKING          <-- NEW
# ---------------------------------------------------
def complete_booking(
    db: Session,
    booking: Booking,
):
    if booking.status != BookingStatus.APPROVED:
        raise HTTPException(
            status_code=409,
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
    return get_booking_by_id(db, booking.id)


# ---------------------------------------------------
# CANCEL BOOKING            <-- NEW
# ---------------------------------------------------
def cancel_booking(
    db: Session,
    booking: Booking,
):
    if booking.status not in {
        BookingStatus.PENDING,
        BookingStatus.APPROVED,
    }:
        raise HTTPException(
            status_code=409,
            detail="Only pending or approved bookings can be cancelled.",
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
    return get_booking_by_id(db, booking.id)
