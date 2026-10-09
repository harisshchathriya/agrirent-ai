from collections import Counter
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment
from app.schemas.ai_schema import (
    EquipmentRecommendation,
    RecommendationResponse,
)

HISTORICAL_STATUSES = (BookingStatus.APPROVED, BookingStatus.COMPLETED)


def build_recommendations(
    farmer_id: UUID,
    historical_rows: list[tuple[UUID, UUID, str]],
    available_equipment: list[Equipment],
    limit: int = 5,
) -> RecommendationResponse:
    """Rank available items from approved/completed booking counts."""
    personal = [row for row in historical_rows if row[1] == farmer_id]

    def counts_for(rows):
        return Counter(row[2] for row in rows), Counter(row[0] for row in rows)

    def has_candidate_signal(category_counts, equipment_counts):
        return any(
            category_counts[item.category] * 2 + equipment_counts[item.id] * 3 > 0
            for item in available_equipment
        )

    personal_categories, personal_equipment = counts_for(personal)
    personalized = bool(personal) and has_candidate_signal(
        personal_categories, personal_equipment
    )

    population_categories, population_equipment = counts_for(historical_rows)
    fallback_used = (
        not personalized
        and has_candidate_signal(population_categories, population_equipment)
    )

    if personalized:
        category_counts, equipment_counts = personal_categories, personal_equipment
    elif fallback_used:
        category_counts, equipment_counts = population_categories, population_equipment
    else:
        category_counts, equipment_counts = Counter(), Counter()

    ranked = []
    for item in available_equipment:
        category_frequency = category_counts[item.category]
        exact_frequency = equipment_counts[item.id]
        score = category_frequency * 2 + exact_frequency * 3
        if personalized:
            explanation = (
                f"Your qualifying booking history includes this category {category_frequency} "
                f"time(s) and this equipment {exact_frequency} time(s)."
            )
        elif fallback_used:
            explanation = (
                f"Popularity fallback: this category has {category_frequency} "
                f"historical booking(s) and this equipment has {exact_frequency}."
            )
        else:
            explanation = "No qualifying historical booking signal matches this available equipment."
        ranked.append((
            -score, item.category, item.name, str(item.id),
            EquipmentRecommendation(
                equipment_id=item.id,
                name=item.name,
                category=item.category,
                location=item.location,
                score=score,
                explanation=explanation,
            ),
        ))

    ranked.sort(key=lambda row: row[:4])
    return RecommendationResponse(
        recommendations=[row[4] for row in ranked[:limit]],
        personalized=personalized,
        fallback_used=fallback_used,
        message=(
            "No equipment is currently available."
            if not available_equipment
            else "No qualifying booking signal matches the currently available equipment."
            if not personalized and not fallback_used and historical_rows
            else "No qualifying historical booking data is available."
            if not personalized and not fallback_used
            else None
        ),
    )


def get_recommendations(
    db: Session, farmer_id: UUID, limit: int = 5
) -> RecommendationResponse:
    # Historical preferences deliberately do not join/filter on availability.
    historical_rows = (
        db.query(Booking.equipment_id, Booking.renter_id, Equipment.category)
        .join(Equipment, Equipment.id == Booking.equipment_id)
        .filter(Booking.status.in_(HISTORICAL_STATUSES))
        .all()
    )
    available = (
        db.query(Equipment)
        .filter(Equipment.availability.is_(True))
        .all()
    )
    return build_recommendations(farmer_id, historical_rows, available, limit)
