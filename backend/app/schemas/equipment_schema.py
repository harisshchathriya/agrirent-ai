from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field, TypeAdapter, field_validator


_HTTP_URL = TypeAdapter(AnyHttpUrl)


def _clean_image_url(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Image URL must be a valid HTTP or HTTPS URL.")
    value = value.strip()
    if not value:
        return None
    try:
        value = str(_HTTP_URL.validate_python(value))
    except ValueError as exc:
        raise ValueError("Image URL must be a valid HTTP or HTTPS URL.") from exc
    if len(value) > 255:
        raise ValueError("Image URL must be 255 characters or fewer.")
    return value


# -----------------------------
# Create Equipment
# -----------------------------
class EquipmentCreate(BaseModel):
    name: str
    category: str
    description: str
    price_per_day: float
    location: str
    image_url: str | None = Field(default=None, max_length=255)

    @field_validator("image_url", mode="before")
    @classmethod
    def clean_image_url(cls, value):
        return _clean_image_url(value)


# -----------------------------
# Update Equipment
# -----------------------------
class EquipmentUpdate(BaseModel):
    name: str
    category: str
    description: str
    price_per_day: float
    location: str
    image_url: str | None = Field(default=None, max_length=255)

    @field_validator("image_url", mode="before")
    @classmethod
    def clean_image_url(cls, value):
        return _clean_image_url(value)


# -----------------------------
# Response Schema
# -----------------------------
class EquipmentResponse(BaseModel):
    id: UUID
    owner_id: UUID
    owner_name: str | None = None

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
