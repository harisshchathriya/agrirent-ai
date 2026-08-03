from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def register_user(db: Session, user: UserCreate):

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


def login_user(db: Session, email: str, password: str):

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