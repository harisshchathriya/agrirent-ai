from collections import Counter, defaultdict
from datetime import date

from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment
from app.schemas.ai_schema import CategoryDemand, DemandTrendResponse

MINIMUM_HISTORICAL_PERIODS = 3
HISTORICAL_STATUSES = (BookingStatus.APPROVED, BookingStatus.COMPLETED)


def build_demand_trends(
    booking_rows: list[tuple[BookingStatus, date, str]],
) -> DemandTrendResponse:
    """Aggregate approved/completed bookings into per-category, per-period demand counts.

    Only approved and completed bookings are treated as historical demand. The
    response never fabricates a forecast: forecasting is marked unavailable until
    at least MINIMUM_HISTORICAL_PERIODS distinct periods are present.
    """
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for status, start_date, category in booking_rows:
        if status not in HISTORICAL_STATUSES:
            continue
        period = f"{start_date.year:04d}-{start_date.month:02d}"
        counts[period][category] += 1

    periods = sorted(counts)
    categories = sorted({category for period in counts for category in counts[period]})
    category_series = [
        CategoryDemand(
            category=category,
            periods=periods,
            demand_counts=[counts[period][category] for period in periods],
        )
        for category in categories
    ]
    sufficient = len(periods) >= MINIMUM_HISTORICAL_PERIODS
    return DemandTrendResponse(
        historical_period_count=len(periods),
        historical_periods=periods,
        categories=category_series,
        forecast_available=False,
        status="forecasting_not_selected" if sufficient else "insufficient_history",
        insufficient_history=not sufficient,
        message=(
            "Forecasting is unavailable because fewer than 3 historical periods exist."
            if not sufficient
            else "Historical depth is sufficient for evaluation, but no forecasting method has been selected."
        ),
    )


def get_demand_trends(db: Session) -> DemandTrendResponse:
    rows = (
        db.query(Booking.status, Booking.start_date, Equipment.category)
        .join(Equipment, Equipment.id == Booking.equipment_id)
        .filter(Booking.status.in_(HISTORICAL_STATUSES))
        .all()
    )
    return build_demand_trends(rows)
