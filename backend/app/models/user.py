from sqlalchemy import String, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    FARMER = "farmer"
    OWNER = "owner"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    owned_equipment: Mapped[list["Equipment"]] = relationship(
        "Equipment",
        back_populates="owner",
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="renter",
    )
