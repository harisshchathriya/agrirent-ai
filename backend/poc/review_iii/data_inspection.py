"""Inspect aggregate booking and equipment data for the Review-III POC."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment
from app.models.user import User


HISTORICAL_STATUSES = frozenset(
    {BookingStatus.APPROVED, BookingStatus.COMPLETED}
)


def _status_value(status: object) -> str:
    return getattr(status, "value", str(status))


def _month_value(value: date | datetime | None) -> str:
    if value is None:
        return "unknown"
    return f"{value.year:04d}-{value.month:02d}"


def collect_aggregate_data(db: Session) -> dict[str, object]:
    """Return aggregate counts without exposing row-level or sensitive data."""
    users = db.query(User.id).count()
    equipment = db.query(Equipment.id, Equipment.category).all()
    bookings = db.query(
        Booking.equipment_id,
        Booking.start_date,
        Booking.status,
    ).all()

    equipment_by_id = {equipment_id: category for equipment_id, category in equipment}
    status_counts = Counter(_status_value(status) for _, _, status in bookings)
    category_counts = Counter(category for _, category in equipment)
    booking_counts_by_equipment = Counter(
        str(equipment_id) for equipment_id, _, _ in bookings
    )
    booking_counts_by_category = Counter(
        equipment_by_id.get(equipment_id, "unknown")
        for equipment_id, _, _ in bookings
    )
    booking_counts_by_month = Counter(
        _month_value(start_date) for _, start_date, _ in bookings
    )

    historical_bookings = [
        booking
        for booking in bookings
        if booking[2] in HISTORICAL_STATUSES
    ]

    return {
        "user_count": users,
        "equipment_count": len(equipment),
        "booking_count": len(bookings),
        "status_counts": dict(sorted(status_counts.items())),
        "equipment_category_counts": dict(sorted(category_counts.items())),
        "booking_counts_by_equipment": dict(
            sorted(booking_counts_by_equipment.items())
        ),
        "booking_counts_by_category": dict(
            sorted(booking_counts_by_category.items())
        ),
        "booking_counts_by_month": dict(sorted(booking_counts_by_month.items())),
        "historical_booking_count": len(historical_bookings),
        "historical_period_count": len(
            {_month_value(start_date) for _, start_date, _ in historical_bookings}
        ),
    }


def print_aggregate_data(data: dict[str, object]) -> None:
    """Print the aggregate POC report."""
    print("Review-III Week 7 Data Inspection")
    print(f"Users: {data['user_count']}")
    print(f"Equipment: {data['equipment_count']}")
    print(f"Bookings: {data['booking_count']}")
    print(f"Historical bookings (approved/completed): {data['historical_booking_count']}")
    print(f"Historical booking periods: {data['historical_period_count']}")
    print(f"Booking status distribution: {data['status_counts']}")
    print(f"Equipment category distribution: {data['equipment_category_counts']}")
    print(f"Booking counts by equipment: {data['booking_counts_by_equipment']}")
    print(f"Booking counts by category: {data['booking_counts_by_category']}")
    print(f"Booking counts by month: {data['booking_counts_by_month']}")


def main() -> None:
    from app.database.session import SessionLocal, engine

    engine.echo = False
    db = SessionLocal()
    try:
        print_aggregate_data(collect_aggregate_data(db))
    finally:
        db.close()


if __name__ == "__main__":
    main()