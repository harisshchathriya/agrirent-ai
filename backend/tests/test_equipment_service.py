from unittest.mock import MagicMock
from uuid import uuid4

from app.models.equipment import Equipment
from app.models.user import User, UserRole
from app.schemas.equipment_schema import (
    EquipmentCreate,
    EquipmentUpdate,
)
from app.services import equipment_service


def test_create_equipment():
    db = MagicMock()

    owner = User(
        id=uuid4(),
        name="Equipment Owner",
        email="owner@example.com",
        hashed_password="hashed-password",
        phone="9876543210",
        role=UserRole.OWNER,
    )

    equipment_data = EquipmentCreate(
        name="John Deere Tractor",
        category="Tractor",
        description="Agricultural tractor",
        price_per_day=2500,
        location="Trichy",
    )

    result = equipment_service.create_equipment(
        db,
        equipment_data,
        owner,
    )

    assert result.owner_id == owner.id
    assert result.name == "John Deere Tractor"
    assert result.category == "Tractor"
    assert result.description == "Agricultural tractor"
    assert result.price_per_day == 2500
    assert result.location == "Trichy"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_get_all_equipment():
    db = MagicMock()

    equipment_list = [
        Equipment(
            owner_id=uuid4(),
            name="Tractor",
            category="Tractor",
            description="Agricultural tractor",
            price_per_day=2500,
            location="Trichy",
        ),
        Equipment(
            owner_id=uuid4(),
            name="Harvester",
            category="Harvester",
            description="Agricultural harvester",
            price_per_day=3500,
            location="Chennai",
        ),
    ]

    db.query.return_value.all.return_value = equipment_list

    result = equipment_service.get_all_equipment(db)

    assert result == equipment_list
    assert len(result) == 2
    db.query.assert_called_once_with(equipment_service.Equipment)


def test_get_equipment_by_id_returns_equipment():
    db = MagicMock()

    equipment_id = uuid4()

    equipment = Equipment(
        id=equipment_id,
        owner_id=uuid4(),
        name="Tractor",
        category="Tractor",
        description="Agricultural tractor",
        price_per_day=2500,
        location="Trichy",
    )

    db.query.return_value.filter.return_value.first.return_value = equipment

    result = equipment_service.get_equipment_by_id(
        db,
        equipment_id,
    )

    assert result is not None
    assert result is equipment
    assert result.id == equipment_id
    assert result.name == "Tractor"


def test_get_equipment_by_id_returns_none_when_missing():
    db = MagicMock()

    equipment_id = uuid4()

    db.query.return_value.filter.return_value.first.return_value = None

    result = equipment_service.get_equipment_by_id(
        db,
        equipment_id,
    )

    assert result is None


def test_update_equipment():
    db = MagicMock()

    equipment = Equipment(
        owner_id=uuid4(),
        name="Old Tractor",
        category="Tractor",
        description="Old description",
        price_per_day=2000,
        location="Trichy",
    )

    updated_data = EquipmentUpdate(
        name="New Tractor",
        category="Heavy Tractor",
        description="Updated description",
        price_per_day=3000,
        location="Chennai",
    )

    result = equipment_service.update_equipment(
        db,
        equipment,
        updated_data,
    )

    assert result is equipment
    assert equipment.name == "New Tractor"
    assert equipment.category == "Heavy Tractor"
    assert equipment.description == "Updated description"
    assert equipment.price_per_day == 3000
    assert equipment.location == "Chennai"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(equipment)


def test_delete_equipment():
    db = MagicMock()

    equipment = Equipment(
        id=uuid4(),
        owner_id=uuid4(),
        name="Tractor",
        category="Tractor",
        description="Agricultural tractor",
        price_per_day=2500,
        location="Trichy",
    )

    result = equipment_service.delete_equipment(
        db,
        equipment,
    )

    assert result is None
    db.delete.assert_called_once_with(equipment)
    db.commit.assert_called_once()
