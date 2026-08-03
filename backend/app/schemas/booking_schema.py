from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    equipment_id: UUID
    start_date: date
    end_date: date


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class BookingUpdate(BookingStatusUpdate):
    pass


class BookingResponse(BaseModel):
    id: UUID
    equipment_id: UUID
    renter_id: UUID

    start_date: date
    end_date: date

    total_price: float

    status: BookingStatus

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )