"""Deterministic, explainable equipment recommendation baseline."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Iterable
from uuid import UUID

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment


HISTORICAL_STATUSES = frozenset(
    {BookingStatus.APPROVED, BookingStatus.COMPLETED}
)


def _status_value(status: object) -> str:
    return getattr(status, "value", str(status))


@dataclass(frozen=True)
class Recommendation:
    equipment_id: UUID
    name: str
    category: str
    location: str
    score: int
    explanation: str


def rank_recommendations(
    farmer_id: UUID,
    bookings: Iterable[Booking],
    equipment: Iterable[Equipment],
    top_n: int = 5,
) -> list[Recommendation]:
    """Rank available equipment using booking frequency only.

    The score is deterministic: category frequency is weighted by two and
    exact equipment frequency is weighted by three. Farmers without history
    receive an overall popularity fallback using the same transparent score.
    """
    booking_list = list(bookings)
    equipment_list = [item for item in equipment if item.availability]
    equipment_by_id = {item.id: item for item in equipment_list}

    historical = [
        booking
        for booking in booking_list
        if booking.status in HISTORICAL_STATUSES
    ]
    farmer_history = [
        booking for booking in historical if booking.renter_id == farmer_id
    ]
    has_personal_history = bool(farmer_history)
    relevant_bookings = farmer_history if has_personal_history else historical

    category_counts = Counter()
    equipment_counts = Counter()
    for booking in relevant_bookings:
        equipment_item = equipment_by_id.get(booking.equipment_id)
        if equipment_item is None:
            continue
        category_counts[equipment_item.category] += 1
        equipment_counts[equipment_item.id] += 1

    ranked: list[Recommendation] = []
    for item in equipment_list:
        category_count = category_counts[item.category]
        equipment_count = equipment_counts[item.id]
        score = category_count * 2 + equipment_count * 3
        if has_personal_history and score:
            explanation = (
                f"Category used {category_count} time(s); this equipment used "
                f"{equipment_count} time(s) in your historical bookings."
            )
        elif not has_personal_history and score:
            explanation = (
                f"Fallback popularity: category booked {category_count} time(s); "
                f"this equipment booked {equipment_count} time(s)."
            )
        else:
            explanation = "Available equipment with no matching historical bookings."
        ranked.append(
            Recommendation(
                equipment_id=item.id,
                name=item.name,
                category=item.category,
                location=item.location,
                score=score,
                explanation=explanation,
            )
        )

    ranked.sort(key=lambda item: (-item.score, item.category, item.name, str(item.equipment_id)))
    return ranked[: max(top_n, 0)]


def recommend_for_farmer(db, farmer_id: UUID, top_n: int = 5) -> list[dict[str, object]]:
    """Load POC inputs from SQLAlchemy and return serializable results."""
    bookings = db.query(Booking).all()
    equipment = db.query(Equipment).all()
    return [
        asdict(item)
        for item in rank_recommendations(farmer_id, bookings, equipment, top_n)
    ]


def main() -> None:
    from app.database.session import SessionLocal, engine

    engine.echo = False
    db = SessionLocal()
    try:
        farmer_id = (
            db.query(Booking.renter_id)
            .filter(Booking.status.in_(HISTORICAL_STATUSES))
            .order_by(Booking.renter_id)
            .first()
        )
        if farmer_id is None:
            print("Recommendation baseline: no booking history is available.")
            return
        results = recommend_for_farmer(db, farmer_id[0])
        print("Review-III Week 7 Recommendation Baseline")
        print(f"Farmer history sample: {farmer_id[0]}")
        print(f"Recommendations: {results}")
    finally:
        db.close()


if __name__ == "__main__":
    main()