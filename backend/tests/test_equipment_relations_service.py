from datetime import date, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment
from app.models.equipment_image import EquipmentImage
from app.models.review import Review
from app.models.user import User, UserRole
from app.schemas.equipment_image_schema import EquipmentImageCreate
from app.schemas.review_schema import ReviewCreate
from app.services import equipment_relations_service


def create_owner():
    return User(
        id=uuid4(),
        name="Equipment Owner",
        email="owner@example.com",
        hashed_password="hashed-password",
        phone="9876543210",
        role=UserRole.OWNER,
    )


def create_farmer():
    return User(
        id=uuid4(),
        name="Test Farmer",
        email="farmer@example.com",
        hashed_password="hashed-password",
        phone="9876543211",
        role=UserRole.FARMER,
    )


def create_equipment(owner_id):
    return Equipment(
        id=uuid4(),
        owner_id=owner_id,
        name="Tractor",
        category="Tractor",
        description="Agricultural tractor",
        price_per_day=2500,
        location="Trichy",
    )


def test_get_equipment_or_404_returns_equipment():
    db = MagicMock()

    equipment = create_equipment(uuid4())

    db.query.return_value.filter.return_value.first.return_value = equipment

    result = equipment_relations_service.get_equipment_or_404(
        db,
        equipment.id,
    )

    assert result is equipment


def test_get_equipment_or_404_raises_404_when_missing():
    db = MagicMock()

    equipment_id = uuid4()

    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        equipment_relations_service.get_equipment_or_404(
            db,
            equipment_id,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Equipment not found."


def test_get_images_returns_equipment_images():
    db = MagicMock()

    equipment = create_equipment(uuid4())

    image_1 = EquipmentImage(
        id=uuid4(),
        equipment_id=equipment.id,
        image_url="https://example.com/tractor-1.jpg",
    )

    image_2 = EquipmentImage(
        id=uuid4(),
        equipment_id=equipment.id,
        image_url="https://example.com/tractor-2.jpg",
    )

    db.query.return_value.filter.return_value.first.return_value = equipment
    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .all.return_value
    ) = [image_1, image_2]

    result = equipment_relations_service.get_images(
        db,
        equipment.id,
    )

    assert result == [image_1, image_2]


def test_add_image_allows_equipment_owner():
    db = MagicMock()

    owner = create_owner()
    equipment = create_equipment(owner.id)

    db.query.return_value.filter.return_value.first.return_value = equipment

    image_data = EquipmentImageCreate(
        image_url="https://example.com/tractor.jpg"
    )

    result = equipment_relations_service.add_image(
        db,
        equipment.id,
        image_data,
        owner,
    )

    assert result.equipment_id == equipment.id
    assert result.image_url == "https://example.com/tractor.jpg"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_add_image_rejects_non_owner():
    db = MagicMock()

    owner = create_owner()
    farmer = create_farmer()

    equipment = create_equipment(owner.id)

    db.query.return_value.filter.return_value.first.return_value = equipment

    image_data = EquipmentImageCreate(
        image_url="https://example.com/tractor.jpg"
    )

    with pytest.raises(HTTPException) as exc_info:
        equipment_relations_service.add_image(
            db,
            equipment.id,
            image_data,
            farmer,
        )

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == "Only the equipment owner can add images."
    )

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_get_reviews_returns_equipment_reviews():
    db = MagicMock()

    equipment = create_equipment(uuid4())

    review_1 = Review(
        id=uuid4(),
        user_id=uuid4(),
        equipment_id=equipment.id,
        rating=5,
        comment="Excellent equipment.",
    )

    review_2 = Review(
        id=uuid4(),
        user_id=uuid4(),
        equipment_id=equipment.id,
        rating=4,
        comment="Worked well.",
    )

    db.query.return_value.filter.return_value.first.return_value = equipment
    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .all.return_value
    ) = [review_1, review_2]

    result = equipment_relations_service.get_reviews(
        db,
        equipment.id,
    )

    assert result == [review_1, review_2]


def test_add_review_allows_renter_with_completed_booking():
    db = MagicMock()

    farmer = create_farmer()
    equipment = create_equipment(uuid4())

    completed_booking = Booking(
        id=uuid4(),
        equipment_id=equipment.id,
        renter_id=farmer.id,
        start_date=date.today() - timedelta(days=3),
        end_date=date.today() - timedelta(days=1),
        total_price=5000,
        status=BookingStatus.COMPLETED,
    )

    query = db.query.return_value

    query.filter.return_value.first.side_effect = [
        equipment,
        completed_booking,
    ]

    review_data = ReviewCreate(
        rating=5,
        comment="Excellent tractor.",
    )

    result = equipment_relations_service.add_review(
        db,
        equipment.id,
        review_data,
        farmer,
    )

    assert result.user_id == farmer.id
    assert result.equipment_id == equipment.id
    assert result.rating == 5
    assert result.comment == "Excellent tractor."

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_add_review_rejects_renter_without_completed_booking():
    db = MagicMock()

    farmer = create_farmer()
    equipment = create_equipment(uuid4())

    query = db.query.return_value

    query.filter.return_value.first.side_effect = [
        equipment,
        None,
    ]

    review_data = ReviewCreate(
        rating=5,
        comment="Excellent tractor.",
    )

    with pytest.raises(HTTPException) as exc_info:
        equipment_relations_service.add_review(
            db,
            equipment.id,
            review_data,
            farmer,
        )

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == "Only renters with a completed booking can review this equipment."
    )

    db.add.assert_not_called()
    db.commit.assert_not_called()
