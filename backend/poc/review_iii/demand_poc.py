"""Baseline demand aggregation and conditional moving-average forecast."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Iterable

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment


HISTORICAL_STATUSES = frozenset(
    {BookingStatus.APPROVED, BookingStatus.COMPLETED}
)


def _month_value(value: date | datetime) -> str:
    return f"{value.year:04d}-{value.month:02d}"


def build_demand_series(
    bookings: Iterable[Booking],
    equipment: Iterable[Equipment],
) -> dict[str, dict[str, int]]:
    """Aggregate approved/completed bookings by month and category."""
    category_by_equipment = {item.id: item.category for item in equipment}
    series: dict[str, Counter[str]] = defaultdict(Counter)
    for booking in bookings:
        if booking.status not in HISTORICAL_STATUSES:
            continue
        category = category_by_equipment.get(booking.equipment_id)
        if category is None:
            continue
        series[_month_value(booking.start_date)][category] += 1
    return {
        period: dict(sorted(counts.items()))
        for period, counts in sorted(series.items())
    }


def evaluate_baseline(
    series: dict[str, dict[str, int]],
    minimum_periods: int = 3,
    window: int = 3,
) -> dict[str, object]:
    """Return a moving-average forecast only when enough periods exist."""
    periods = sorted(series)
    if len(periods) < minimum_periods:
        return {
            "supported": False,
            "reason": (
                f"Only {len(periods)} historical period(s) are available; "
                f"at least {minimum_periods} are required for this baseline."
            ),
            "forecast": {},
        }

    categories = sorted({category for values in series.values() for category in values})
    recent_periods = periods[-window:]
    forecast = {
        category: round(
            sum(series[period].get(category, 0) for period in recent_periods)
            / len(recent_periods),
            2,
        )
        for category in categories
    }
    return {
        "supported": True,
        "reason": f"Moving average over the latest {len(recent_periods)} period(s).",
        "forecast": forecast,
    }


def run_demand_poc(db) -> dict[str, object]:
    bookings = db.query(Booking).all()
    equipment = db.query(Equipment).all()
    series = build_demand_series(bookings, equipment)
    baseline = evaluate_baseline(series)
    return {
        "series": series,
        "total_bookings": sum(sum(values.values()) for values in series.values()),
        "period_count": len(series),
        "baseline": baseline,
    }


def main() -> None:
    from app.database.session import SessionLocal, engine

    engine.echo = False
    db = SessionLocal()
    try:
        result = run_demand_poc(db)
        print("Review-III Week 7 Demand Baseline")
        print(f"Historical demand series: {result['series']}")
        print(f"Historical booking total: {result['total_bookings']}")
        print(f"Historical period count: {result['period_count']}")
        print(f"Baseline evaluation: {result['baseline']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()