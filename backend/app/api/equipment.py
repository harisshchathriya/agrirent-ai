from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.equipment import Equipment

from app.schemas.equipment_schema import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
)

from app.services.equipment_service import (
    create_equipment,
    get_all_equipment,
    get_equipment_by_id,
    update_equipment,
    delete_equipment,
)

from app.core.security import get_current_user


router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"],
)


# ---------------------------------
# Create Equipment
# ---------------------------------
@router.post(
    "",
    response_model=EquipmentResponse,
)
def add_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_equipment(
        db,
        equipment,
        current_user,
    )


# ---------------------------------
# Get All Equipment
# ---------------------------------
@router.get(
    "",
    response_model=list[EquipmentResponse],
)
def read_all_equipment(
    db: Session = Depends(get_db),
):
    return get_all_equipment(db)


# ---------------------------------
# Get Equipment By ID
# ---------------------------------
@router.get(
    "/{equipment_id}",
    response_model=EquipmentResponse,
)
def read_equipment(
    equipment_id: UUID,
    db: Session = Depends(get_db),
):
    equipment = get_equipment_by_id(
        db,
        equipment_id,
    )

    if not equipment:
        raise HTTPException(
            status_code=404,
            detail="Equipment not found",
        )

    return equipment


# ---------------------------------
# Update Equipment
# ---------------------------------
@router.put(
    "/{equipment_id}",
    response_model=EquipmentResponse,
)
def edit_equipment(
    equipment_id: UUID,
    updated_data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    equipment = get_equipment_by_id(
        db,
        equipment_id,
    )

    if not equipment:
        raise HTTPException(
            status_code=404,
            detail="Equipment not found",
        )

    if equipment.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this equipment",
        )

    return update_equipment(
        db,
        equipment,
        updated_data,
    )


# ---------------------------------
# Delete Equipment
# ---------------------------------
@router.delete(
    "/{equipment_id}",
)
def remove_equipment(
    equipment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    equipment = get_equipment_by_id(
        db,
        equipment_id,
    )

    if not equipment:
        raise HTTPException(
            status_code=404,
            detail="Equipment not found",
        )

    if equipment.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this equipment",
        )

    delete_equipment(
        db,
        equipment,
    )

    return {
        "message": "Equipment deleted successfully"
    }