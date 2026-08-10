from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=1)


class ReviewResponse(BaseModel):
    id: UUID
    user_id: UUID
    equipment_id: UUID
    rating: int
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
