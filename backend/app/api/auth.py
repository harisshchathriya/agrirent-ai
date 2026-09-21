import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.user_schema import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserCreate,
    UserResponse,
    Token,
)

from app.services.auth_service import (
    register_user,
    login_user,
    create_password_reset_token,
    get_user_by_email,
    reset_password,
)
from app.core.config import APP_ENV, FRONTEND_URL

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
    try:
        new_user = register_user(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not new_user:
        logger.warning("Registration rejected for duplicate email: %s", user.email)
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    logger.info("User registered: %s", new_user.email)
    return new_user


@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, request.email)
    if user:
        token = create_password_reset_token(db, user)
        if APP_ENV in {"development", "demo"}:
            reset_url = f"{FRONTEND_URL.rstrip('/')}/reset-password?token={token}"
            logger.info("Development password reset URL: %s", reset_url)

    return {
        "message": (
            "If an account exists for this email, a password reset link has "
            "been generated."
        )
    }


@router.post("/reset-password")
def reset_password_request(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    if not reset_password(db, request.token, request.new_password):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset link.",
        )

    return {"message": "Password reset successful. You can now log in."}


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
