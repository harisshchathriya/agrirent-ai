from app.database.session import engine
from app.database.base import Base

# Import all models
from app.models import (
    User,
    Equipment,
    Booking,
)

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")