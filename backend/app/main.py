from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.equipment import router as equipment_router
from app.api.booking import router as booking_router
from app.api.equipment_relations import router as equipment_relations_router
from app.core.config import FRONTEND_URL

app = FastAPI(
    title="AgriRent AI",
    version="1.0.0",
)

# ----------------------------
# CORS Configuration
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Root Endpoint
# ----------------------------
@app.get("/")
def root():
    return {
        "message": "Welcome to AgriRent AI"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}

# ----------------------------
# API Routes
# ----------------------------
app.include_router(auth_router)
app.include_router(equipment_router)
app.include_router(booking_router)
app.include_router(equipment_relations_router)
