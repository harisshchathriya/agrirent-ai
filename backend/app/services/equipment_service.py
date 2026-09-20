from uuid import UUID

from sqlalchemy.orm import Session

from app.models.equipment import Equipment
from app.models.user import User
from app.schemas.equipment_schema import (
    EquipmentCreate,
    EquipmentUpdate,
)


# --------------------------------
# Create Equipment
# --------------------------------
def create_equipment(
    db: Session,
    equipment: EquipmentCreate,
    owner: User,
) -> Equipment:
    new_equipment = Equipment(
        owner_id=owner.id,
        name=equipment.name,
        category=equipment.category,
        description=equipment.description,
        price_per_day=equipment.price_per_day,
        location=equipment.location,
    )

    db.add(new_equipment)
    db.commit()
    db.refresh(new_equipment)

    return new_equipment


# --------------------------------
# Get All Equipment
# --------------------------------
def get_all_equipment(db: Session) -> list[Equipment]:
    return db.query(Equipment).all()


# --------------------------------
# Get Equipment by ID
# --------------------------------
def get_equipment_by_id(
    db: Session,
    equipment_id: UUID,
) -> Equipment | None:
    return (
        db.query(Equipment)
        .filter(Equipment.id == equipment_id)
        .first()
    )


# --------------------------------
# Update Equipment
# --------------------------------
def update_equipment(
    db: Session,
    equipment: Equipment,
    updated_data: EquipmentUpdate,
) -> Equipment:
    equipment.name = updated_data.name
    equipment.category = updated_data.category
    equipment.description = updated_data.description
    equipment.price_per_day = updated_data.price_per_day
    equipment.location = updated_data.location

    db.commit()
    db.refresh(equipment)

    return equipment


# --------------------------------
# Delete Equipment
# --------------------------------
def delete_equipment(
    db: Session,
    equipment: Equipment,
) -> None:
    db.delete(equipment)
    db.commit()
