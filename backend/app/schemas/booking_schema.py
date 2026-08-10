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
    farmer_id: UUID
    renter_id: UUID
    renter_name: str | None = None
    owner_name: str | None = None
    owner_email: str | None = None

    equipment_name: str
    category: str
    location: str
    price_per_day: float

    start_date: date
    end_date: date
    total_price: float
    status: str

    model_config = ConfigDict(from_attributes=True)
