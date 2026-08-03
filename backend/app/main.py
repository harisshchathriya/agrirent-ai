from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.equipment import router as equipment_router
from app.api.booking import router as booking_router

app = FastAPI(
    title="AgriRent AI",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to AgriRent AI"
    }


# Authentication Routes
app.include_router(auth_router)

# Equipment Routes
app.include_router(equipment_router)

# Booking Routes
app.include_router(booking_router)