from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# -----------------------------
# Create Equipment
# -----------------------------
class EquipmentCreate(BaseModel):
    name: str
    category: str
    description: str
    price_per_day: float
    location: str


# -----------------------------
# Update Equipment
# -----------------------------
class EquipmentUpdate(BaseModel):
    name: str
    category: str
    description: str
    price_per_day: float
    location: str


# -----------------------------
# Response Schema
# -----------------------------
class EquipmentResponse(BaseModel):
    id: UUID
    owner_id: UUID

    name: str
    category: str
    description: str

    price_per_day: float
    location: str

    availability: bool
    image_url: str | None = None

    created_at: datetime

    model_config = {
        "from_attributes": True
    }