from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.password_reset_token import PasswordResetToken
from app.schemas.user_schema import UserCreate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.core.config import PASSWORD_RESET_TOKEN_EXPIRE_MINUTES


PUBLIC_REGISTRATION_ROLES = {UserRole.FARMER, UserRole.OWNER}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def register_user(db: Session, user: UserCreate) -> User | None:

    if user.role not in PUBLIC_REGISTRATION_ROLES:
        raise ValueError("Only farmer and owner roles can be registered publicly.")

    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        return None

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        phone=user.phone,
        role=user.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_password_reset_token(
    db: Session,
    user: User,
) -> str:
    raw_token = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_reset_token(raw_token),
        expires_at=utc_now() + timedelta(
            minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        ),
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return raw_token


def reset_password(
    db: Session,
    token: str,
    new_password: str,
) -> bool:
    reset_token = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == hash_reset_token(token))
        .first()
    )

    if (
        not reset_token
        or reset_token.used_at is not None
        or reset_token.expires_at <= utc_now()
    ):
        return False

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        return False

    user.hashed_password = hash_password(new_password)
    reset_token.used_at = utc_now()
    db.commit()
    return True


def login_user(db: Session, email: str, password: str) -> str | None:

    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    access_token = create_access_token(
        data={"sub": user.email}
    )

    return access_token
