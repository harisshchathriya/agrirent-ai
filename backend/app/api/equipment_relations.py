from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.equipment_image_schema import EquipmentImageCreate, EquipmentImageResponse
from app.schemas.review_schema import ReviewCreate, ReviewResponse
from app.services.equipment_relations_service import add_image, add_review, get_images, get_reviews


router = APIRouter(prefix="/equipment", tags=["Equipment relationships"])


@router.get("/{equipment_id}/images", response_model=list[EquipmentImageResponse])
def read_images(equipment_id: UUID, db: Session = Depends(get_db)):
    return get_images(db, equipment_id)


@router.post("/{equipment_id}/images", response_model=EquipmentImageResponse)
def create_image(
    equipment_id: UUID,
    image_data: EquipmentImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_image(db, equipment_id, image_data, current_user)


@router.get("/{equipment_id}/reviews", response_model=list[ReviewResponse])
def read_reviews(equipment_id: UUID, db: Session = Depends(get_db)):
    return get_reviews(db, equipment_id)


@router.post("/{equipment_id}/reviews", response_model=ReviewResponse)
def create_review(
    equipment_id: UUID,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_review(db, equipment_id, review_data, current_user)
