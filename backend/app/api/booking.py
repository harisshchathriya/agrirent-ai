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
    get_owner_bookings,
    get_pending_owner_bookings,
    approve_booking,
    reject_booking,
    complete_booking,      # <-- added
    cancel_booking,        # <-- added
    is_equipment_owner,
)

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


# ---------------------------------------------------
# CREATE BOOKING
# ---------------------------------------------------
@router.post(
    "",
    response_model=BookingResponse,
)
def create_new_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_booking(db, booking, current_user)


# ---------------------------------------------------
# MY BOOKINGS
# ---------------------------------------------------
@router.get(
    "",
    response_model=list[BookingResponse],
)
def read_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_bookings(db, current_user)


# ---------------------------------------------------
# UPDATE STATUS
# ---------------------------------------------------
@router.put(
    "/{booking_id}/status",
    response_model=BookingResponse,
)
def update_status(
    booking_id: UUID,
    status: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = get_booking_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )
    if booking.renter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the renter can cancel this booking.",
        )
    return update_booking_status(db, booking, status)


# ---------------------------------------------------
# DELETE BOOKING
# ---------------------------------------------------
@router.delete(
    "/{booking_id}",
)
def remove_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = get_booking_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )
    if booking.renter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the renter can delete this booking.",
        )
    delete_booking(db, booking)
    return {"message": "Booking deleted successfully."}


# ===================================================
# OWNER APIs
# ===================================================

# ---------------------------------------------------
# OWNER - ALL BOOKINGS
# ---------------------------------------------------
@router.get(
    "/owner/bookings",
    response_model=list[BookingResponse],
)
def owner_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owner_bookings(db, current_user)


# ---------------------------------------------------
# OWNER - PENDING BOOKINGS
# ---------------------------------------------------
@router.get(
    "/owner/bookings/pending",
    response_model=list[BookingResponse],
)
def owner_pending_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_pending_owner_bookings(db, current_user)


# ---------------------------------------------------
# OWNER - APPROVE BOOKING
# ---------------------------------------------------
@router.put(
    "/owner/bookings/{booking_id}/approve",
    response_model=BookingResponse,
)
def owner_approve_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = get_booking_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )
    if not is_equipment_owner(db, booking, current_user):
        raise HTTPException(
            status_code=403,
            detail="Only the equipment owner can approve this booking.",
        )
    return approve_booking(db, booking)


# ---------------------------------------------------
# OWNER - REJECT BOOKING
# ---------------------------------------------------
@router.put(
    "/owner/bookings/{booking_id}/reject",
    response_model=BookingResponse,
)
def owner_reject_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = get_booking_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )
    if not is_equipment_owner(db, booking, current_user):
        raise HTTPException(
            status_code=403,
            detail="Only the equipment owner can reject this booking.",
        )
    return reject_booking(db, booking)


# ---------------------------------------------------
# OWNER - COMPLETE BOOKING        <-- NEW ENDPOINT
# ---------------------------------------------------
@router.put(
    "/owner/bookings/{booking_id}/complete",
    response_model=BookingResponse,
)
def owner_complete_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = get_booking_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )
    if not is_equipment_owner(db, booking, current_user):
        raise HTTPException(
            status_code=403,
            detail="Only the equipment owner can complete this booking.",
        )

    return complete_booking(db, booking)


# ---------------------------------------------------
# OWNER - CANCEL BOOKING          <-- NEW ENDPOINT
# ---------------------------------------------------
@router.put(
    "/owner/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
)
def owner_cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = get_booking_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )
    if not is_equipment_owner(db, booking, current_user):
        raise HTTPException(
            status_code=403,
            detail="Only the equipment owner can cancel this booking.",
        )

    return cancel_booking(db, booking)


# ---------------------------------------------------
# GET BOOKING BY ID
# ---------------------------------------------------
# Keep this parameterized route after the fixed owner routes.
@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def read_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = get_booking_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found.",
        )
    if booking.renter_id != current_user.id and not is_equipment_owner(db, booking, current_user):
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view this booking.",
        )
    return booking
