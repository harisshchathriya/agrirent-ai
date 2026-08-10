from app.database.session import engine
from app.database.base import Base

# Import all models
from app.models import (
    User,
    Equipment,
    Booking,
    EquipmentImage,
    Review,
)

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
