from uuid import UUID

from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment
from app.models.user import User

from app.schemas.booking_schema import (
    BookingCreate,
    BookingStatusUpdate,
)


def create_booking(
    db: Session,
    booking: BookingCreate,
    current_user: User,
):
    equipment = (
        db.query(Equipment)
        .filter(
            Equipment.id == booking.equipment_id
        )
        .first()
    )

    if equipment is None:
        return None

    # User cannot rent their own equipment
    if equipment.owner_id == current_user.id:
        return None

    # Invalid date range
    if booking.end_date < booking.start_date:
        return None

    days = (
        booking.end_date - booking.start_date
    ).days + 1

    total_price = (
        float(equipment.price_per_day) * days
    )

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


def get_all_bookings(
    db: Session,
    current_user: User,
):
    return (
        db.query(Booking)
        .filter(
            Booking.renter_id == current_user.id
        )
        .all()
    )


def get_booking_by_id(
    db: Session,
    booking_id: UUID,
):
    return (
        db.query(Booking)
        .filter(
            Booking.id == booking_id
        )
        .first()
    )


def update_booking_status(
    db: Session,
    booking: Booking,
    status: BookingStatusUpdate,
):
    booking.status = BookingStatus(status.status)

    db.commit()
    db.refresh(booking)

    return booking


def delete_booking(
    db: Session,
    booking: Booking,
):
    db.delete(booking)
    db.commit()