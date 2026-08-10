from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EquipmentImageCreate(BaseModel):
    image_url: str = Field(min_length=1, max_length=255)


class EquipmentImageResponse(BaseModel):
    id: UUID
    equipment_id: UUID
    image_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
