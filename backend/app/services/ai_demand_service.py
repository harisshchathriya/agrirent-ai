from collections import Counter, defaultdict
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.equipment import Equipment
from app.schemas.ai_schema import (
    CategoryDemand,
    CategoryForecast,
    DemandTrendResponse,
    ForecastEvaluation,
)

MINIMUM_HISTORICAL_PERIODS = 6
MOVING_AVERAGE_WINDOW = 3
EVALUATION_HORIZON = 3
HISTORICAL_STATUSES = (BookingStatus.APPROVED, BookingStatus.COMPLETED)


def _month_index(value: date | datetime) -> int:
    return value.year * 12 + value.month - 1


def _period_label(month_index: int) -> str:
    year, zero_based_month = divmod(month_index, 12)
    return f"{year:04d}-{zero_based_month + 1:02d}"


def _monthly_series(
    booking_rows: list[tuple[BookingStatus, date | None, str | None]],
) -> tuple[list[str], dict[str, list[int]]]:
    counts: dict[int, Counter[str]] = defaultdict(Counter)
    for status, start_date, category in booking_rows:
        if status not in HISTORICAL_STATUSES or not isinstance(start_date, date):
            continue
        if not isinstance(category, str) or not category.strip():
            continue
        counts[_month_index(start_date)][category.strip()] += 1

    if not counts:
        return [], {}

    first = min(counts)
    last = max(counts)
    month_indices = list(range(first, last + 1))
    periods = [_period_label(index) for index in month_indices]
    categories = sorted({category for monthly in counts.values() for category in monthly})
    series = {
        category: [counts[index][category] for index in month_indices]
        for category in categories
    }
    return periods, series


def _moving_average(values: list[int | float]) -> float:
    prediction = sum(values[-MOVING_AVERAGE_WINDOW:]) / MOVING_AVERAGE_WINDOW
    return round(max(0.0, prediction), 2)


def _evaluate_baseline(
    periods: list[str], series: dict[str, list[int]]
) -> ForecastEvaluation | None:
    """Evaluate three one-step origins; each prediction sees prior months only."""
    if len(periods) < MINIMUM_HISTORICAL_PERIODS:
        return None

    start_index = len(periods) - EVALUATION_HORIZON
    actual_totals = [sum(series[category][i] for category in series) for i in range(len(periods))]
    moving_errors = []
    naive_errors = []
    for target in range(start_index, len(periods)):
        history = actual_totals[:target]
        moving_errors.append(abs(actual_totals[target] - _moving_average(history)))
        naive_errors.append(abs(actual_totals[target] - history[-1]))

    return ForecastEvaluation(
        method="three_month_moving_average",
        baseline="last_month_naive",
        evaluation_start=periods[start_index],
        evaluation_end=periods[-1],
        observations=len(moving_errors),
        mae=round(sum(moving_errors) / len(moving_errors), 2),
        baseline_mae=round(sum(naive_errors) / len(naive_errors), 2),
    )


def build_demand_trends(
    booking_rows: list[tuple[BookingStatus, date | None, str | None]],
) -> DemandTrendResponse:
    """Return continuous observed history and a guarded one-month baseline forecast.

    Gaps between the first and last qualifying booking month represent zero
    approved/completed bookings. Months outside that observed range are unknown
    and are not added. A forecast is exposed only with six consecutive monthly
    observations; its evaluation is a three-origin chronological holdout.
    """
    periods, series = _monthly_series(booking_rows)
    sufficient = len(periods) >= MINIMUM_HISTORICAL_PERIODS
    evaluation = _evaluate_baseline(periods, series) if sufficient else None
    next_period = _period_label(_month_index(datetime.strptime(periods[-1], "%Y-%m").date()) + 1) if periods else None

    forecasts = []
    if sufficient and next_period:
        for category in sorted(series):
            forecasts.append(
                CategoryForecast(
                    category=category,
                    period=next_period,
                    predicted_bookings=_moving_average(series[category]),
                )
            )

    limitations = (
        [
            "This simple baseline uses booking start month and does not account for rental duration, seasonality, weather, or market changes.",
            "The chronological evaluation uses only the latest three one-month holdout observations; metrics are not evidence of long-term accuracy.",
        ]
        if sufficient
        else [
            "Observed history is too short to forecast defensibly. Missing months between the first and last qualifying booking month are filled with zero qualifying bookings; months outside that range are unknown."
        ]
    )
    if evaluation and evaluation.mae > evaluation.baseline_mae:
        limitations.append(
            "The moving-average baseline had higher MAE than the last-month naive baseline in this holdout; treat its forecasts cautiously."
        )

    return DemandTrendResponse(
        historical_period_count=len(periods),
        historical_periods=periods,
        categories=[
            CategoryDemand(
                category=category,
                periods=periods,
                demand_counts=series[category],
            )
            for category in sorted(series)
        ],
        forecast_available=sufficient,
        status="forecast_available" if sufficient else "insufficient_history",
        insufficient_history=not sufficient,
        message=(
            None
            if sufficient
            else f"At least {MINIMUM_HISTORICAL_PERIODS} consecutive observed months are required; no forecast was generated."
        ),
        forecast_method="three_month_moving_average" if sufficient else None,
        forecast_horizon_months=1,
        forecast_periods=[next_period] if sufficient and next_period else [],
        forecasts=forecasts,
        evaluation=evaluation,
        limitations=limitations,
    )


def get_demand_trends(db: Session) -> DemandTrendResponse:
    rows = (
        db.query(Booking.status, Booking.start_date, Equipment.category)
        .join(Equipment, Equipment.id == Booking.equipment_id)
        .filter(Booking.status.in_(HISTORICAL_STATUSES))
        .all()
    )
    return build_demand_trends(rows)
