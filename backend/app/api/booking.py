from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.core.security import get_current_user
from app.models.user import User

from app.schemas.booking_schema import (
    BookingCreate,
    BookingResponse,
    BookingStatusUpdate,
)

from app.services.booking_service import (
    create_booking,
    get_all_bookings,
    get_booking_by_id,
    update_booking_status,
    delete_booking,
)

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


# -----------------------------
# Create Booking
# -----------------------------
@router.post(
    "",
    response_model=BookingResponse,
)
def create_new_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_booking = create_booking(
        db,
        booking,
        current_user,
    )

    if not new_booking:
        raise HTTPException(
            status_code=400,
            detail="Booking could not be created.",
        )

    return new_booking


# -----------------------------
# Get My Bookings
# -----------------------------
@router.get(
    "",
    response_model=list[BookingResponse],
)
def read_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_bookings(
        db,
        current_user,
    )


# -----------------------------
# Get Booking by ID
# -----------------------------
@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def read_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
):
    booking = get_booking_by_id(
        db,
        booking_id,
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )

    return booking


# -----------------------------
# Update Booking Status
# -----------------------------
@router.put(
    "/{booking_id}/status",
    response_model=BookingResponse,
)
def update_status(
    booking_id: UUID,
    status: BookingStatusUpdate,
    db: Session = Depends(get_db),
):
    booking = get_booking_by_id(
        db,
        booking_id,
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )

    return update_booking_status(
        db,
        booking,
        status,
    )


# -----------------------------
# Delete Booking
# -----------------------------
@router.delete(
    "/{booking_id}",
)
def remove_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
):
    booking = get_booking_by_id(
        db,
        booking_id,
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )

    delete_booking(
        db,
        booking,
    )

    return {
        "message": "Booking deleted successfully."
    }