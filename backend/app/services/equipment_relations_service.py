from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment
from app.models.equipment_image import EquipmentImage
from app.models.review import Review
from app.models.user import User
from app.schemas.equipment_image_schema import EquipmentImageCreate
from app.schemas.review_schema import ReviewCreate


def get_equipment_or_404(db: Session, equipment_id):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found.")
    return equipment


def get_images(db: Session, equipment_id):
    get_equipment_or_404(db, equipment_id)
    return (
        db.query(EquipmentImage)
        .filter(EquipmentImage.equipment_id == equipment_id)
        .order_by(EquipmentImage.created_at)
        .all()
    )


def add_image(db: Session, equipment_id, image_data: EquipmentImageCreate, current_user: User):
    equipment = get_equipment_or_404(db, equipment_id)
    if equipment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the equipment owner can add images.")

    image = EquipmentImage(equipment_id=equipment_id, image_url=image_data.image_url)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def get_reviews(db: Session, equipment_id):
    get_equipment_or_404(db, equipment_id)
    return (
        db.query(Review)
        .filter(Review.equipment_id == equipment_id)
        .order_by(Review.created_at.desc())
        .all()
    )


def add_review(db: Session, equipment_id, review_data: ReviewCreate, current_user: User):
    get_equipment_or_404(db, equipment_id)
    completed_booking = (
        db.query(Booking)
        .filter(
            Booking.equipment_id == equipment_id,
            Booking.renter_id == current_user.id,
            Booking.status == BookingStatus.COMPLETED,
        )
        .first()
    )
    if completed_booking is None:
        raise HTTPException(
            status_code=403,
            detail="Only renters with a completed booking can review this equipment.",
        )

    review = Review(
        user_id=current_user.id,
        equipment_id=equipment_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
