import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    Token,
)

from app.services.auth_service import (
    register_user,
    login_user,
)

from app.core.security import get_current_user
from app.models.user import User

logger = logging.getLogger("agrirent.auth")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# -----------------------------
# Register
# -----------------------------
@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    new_user = register_user(db, user)

    if not new_user:
        logger.warning("Registration rejected for duplicate email: %s", user.email)
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    logger.info("User registered: %s", new_user.email)
    return new_user


# -----------------------------
# Login (OAuth2)
# -----------------------------
@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    token = login_user(
        db,
        form_data.username,   # Email goes here
        form_data.password,
    )

    if not token:
        logger.warning("Failed login attempt for email: %s", form_data.username)
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    logger.info("Successful login for email: %s", form_data.username)
    return {
        "access_token": token,
        "token_type": "bearer",
    }


# -----------------------------
# Current Logged-in User
# -----------------------------
@router.get(
    "/users/me",
    response_model=UserResponse,
)
def read_users_me(
    current_user: User = Depends(get_current_user),
):
    return current_user