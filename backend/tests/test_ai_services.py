from datetime import date
from types import SimpleNamespace
from uuid import uuid4

from app.models.booking import BookingStatus
from app.services.ai_demand_service import build_demand_trends
from app.services.ai_recommendation_service import (
    HISTORICAL_STATUSES,
    build_recommendations,
    get_recommendations,
)


def item(name, category="Heavy", available=True, item_id=None):
    return SimpleNamespace(id=item_id or uuid4(), name=name, category=category,
                           location="Trichy", availability=available)


def test_personal_category_and_exact_frequency_scores():
    farmer = uuid4()
    used, similar, other = item("Used"), item("Similar"), item("Other", "Soil")
    rows = [(used.id, farmer, "Heavy")] * 2
    result = build_recommendations(farmer, rows, [used, similar, other])
    assert [(x.name, x.score) for x in result.recommendations] == [
        ("Used", 10), ("Similar", 4), ("Other", 0)]
    assert result.personalized and not result.fallback_used
    assert "category 2 time(s)" in result.recommendations[0].explanation
    assert "equipment 2 time(s)" in result.recommendations[0].explanation
    assert "category 2 time(s)" in result.recommendations[1].explanation
    assert "equipment 0 time(s)" in result.recommendations[1].explanation


def test_unavailable_historical_equipment_still_contributes_preference():
    farmer = uuid4()
    unavailable, candidate = item("Used", available=False), item("Candidate")
    result = build_recommendations(
        farmer, [(unavailable.id, farmer, "Heavy")] * 5, [candidate])
    assert [x.name for x in result.recommendations] == ["Candidate"]
    assert result.recommendations[0].score == 10


def test_service_separates_history_query_from_available_candidate_query():
    farmer = uuid4()
    unavailable = item("Previously used", available=False)
    candidate = item("Available alternative")

    class Query:
        def __init__(self, rows):
            self.rows = rows
            self.filters = []

        def join(self, *_args):
            return self

        def filter(self, *criteria):
            self.filters.extend(criteria)
            return self

        def all(self):
            return self.rows

    history_query = Query([(unavailable.id, farmer, "Heavy")] * 5)
    candidate_query = Query([candidate])

    class Database:
        def __init__(self):
            self.queries = iter([history_query, candidate_query])

        def query(self, *_columns):
            return next(self.queries)

    result = get_recommendations(Database(), farmer)

    assert len(history_query.filters) == 1
    assert "bookings.status IN" in str(history_query.filters[0])
    assert tuple(history_query.filters[0].right.value) == HISTORICAL_STATUSES
    assert len(candidate_query.filters) == 1
    assert "equipment.availability IS true" in str(candidate_query.filters[0])
    assert [item.name for item in result.recommendations] == ["Available alternative"]
    assert result.recommendations[0].score == 10


def test_cold_start_uses_labeled_popularity_fallback():
    farmer = uuid4()
    popular, other = item("Popular"), item("Other", "Soil")
    result = build_recommendations(
        farmer, [(popular.id, uuid4(), "Heavy")] * 3, [other, popular])
    assert result.fallback_used and not result.personalized
    assert result.recommendations[0].name == "Popular"
    assert "Popularity fallback" in result.recommendations[0].explanation


def test_personal_history_without_available_candidate_match_is_not_personalized():
    farmer = uuid4()
    old_equipment, candidate = item("Old listing", "Seasonal"), item("Available")
    result = build_recommendations(
        farmer, [(old_equipment.id, farmer, "Seasonal")], [candidate])

    assert result.recommendations[0].score == 0
    assert not result.personalized
    assert not result.fallback_used
    assert "No qualifying historical booking signal" in result.recommendations[0].explanation
    assert result.message == "No qualifying booking signal matches the currently available equipment."


def test_other_users_do_not_change_a_personalized_ranking():
    farmer, another_farmer = uuid4(), uuid4()
    used, candidate, other_category = item("Used"), item("Similar"), item("Other", "Soil")
    personal_row = (used.id, farmer, "Heavy")
    other_rows = [(other_category.id, another_farmer, "Soil")] * 5

    alone = build_recommendations(farmer, [personal_row], [used, candidate, other_category])
    mixed = build_recommendations(
        farmer, [personal_row, *other_rows], [used, candidate, other_category])

    assert [(r.equipment_id, r.score, r.explanation) for r in mixed.recommendations] == [
        (r.equipment_id, r.score, r.explanation) for r in alone.recommendations
    ]
    assert mixed.personalized and not mixed.fallback_used
    assert [r.score for r in mixed.recommendations] == [5, 2, 0]


def test_population_fallback_is_used_when_personal_history_has_no_candidate_signal():
    farmer, another_farmer = uuid4(), uuid4()
    unavailable, candidate = item("Old", "Seasonal"), item("Available")
    popular = item("Popular", item_id=candidate.id)
    rows = [
        (unavailable.id, farmer, "Seasonal"),
        (popular.id, another_farmer, "Heavy"),
        (popular.id, another_farmer, "Heavy"),
    ]

    result = build_recommendations(farmer, rows, [candidate])

    assert not result.personalized and result.fallback_used
    assert result.recommendations[0].score == 10
    assert "Popularity fallback" in result.recommendations[0].explanation
    assert "category has 2" in result.recommendations[0].explanation
    assert "equipment has 2" in result.recommendations[0].explanation


def test_no_qualifying_history_returns_neutral_unpersonalized_recommendations():
    farmer = uuid4()
    result = build_recommendations(farmer, [], [item("Available")])

    assert result.recommendations[0].score == 0
    assert not result.personalized and not result.fallback_used
    assert "No qualifying historical booking signal" in result.recommendations[0].explanation
    assert result.message == "No qualifying historical booking data is available."


def test_empty_history_candidates_and_limit_are_safe():
    farmer = uuid4()
    result = build_recommendations(farmer, [], [item("Available")], limit=1)
    assert result.recommendations[0].score == 0
    assert not result.fallback_used
    assert build_recommendations(farmer, [], [], 5).recommendations == []
    assert build_recommendations(farmer, [], [item("A")], 0).recommendations == []


def test_recommendation_order_is_deterministic():
    farmer = uuid4()
    lower_id, higher_id = sorted([uuid4(), uuid4()], key=str)
    candidates = [item("Same", "Z", item_id=higher_id),
                  item("Beta", "A"), item("Alpha", "A"),
                  item("Same", "Z", item_id=lower_id)]
    result = build_recommendations(farmer, [], candidates, 3)
    assert [(x.category, x.name) for x in result.recommendations] == [
        ("A", "Alpha"), ("A", "Beta"), ("Z", "Same")]
    assert result.recommendations[-1].equipment_id == lower_id


def test_demand_category_aggregation_and_insufficient_history():
    result = build_demand_trends([
        (BookingStatus.APPROVED, date(2026, 1, 2), "Heavy"),
        (BookingStatus.COMPLETED, date(2026, 1, 9), "Heavy"),
        (BookingStatus.APPROVED, date(2026, 2, 1), "Soil")])
    assert result.historical_periods == ["2026-01", "2026-02"]
    assert result.categories[0].demand_counts == [2, 0]
    assert result.insufficient_history and not result.forecast_available


def test_three_periods_do_not_fabricate_forecast_and_empty_history_safe():
    enough = build_demand_trends([
        (BookingStatus.COMPLETED, date(2026, month, 1), "Heavy")
        for month in (1, 2, 3)])
    empty = build_demand_trends([])
    assert enough.insufficient_history
    assert not enough.forecast_available
    assert enough.status == "insufficient_history"
    assert empty.insufficient_history and empty.categories == []
    assert not empty.forecast_available


def test_demand_history_inserts_zero_months_between_observations():
    result = build_demand_trends([
        (BookingStatus.COMPLETED, date(2026, 1, 5), "Heavy"),
        (BookingStatus.APPROVED, date(2026, 3, 5), "Heavy"),
    ])
    assert result.historical_periods == ["2026-01", "2026-02", "2026-03"]
    assert result.categories[0].demand_counts == [1, 0, 1]
    assert result.status == "insufficient_history"
    assert result.forecasts == []


def test_moving_average_forecast_and_chronological_naive_evaluation():
    rows = [
        (BookingStatus.COMPLETED, date(2026, month, 5), "Heavy")
        for month, count in enumerate((2, 4, 6, 8, 10, 12), start=1)
        for _ in range(count)
    ]
    result = build_demand_trends(rows)
    assert result.forecast_available
    assert result.status == "forecast_available"
    assert result.forecast_method == "three_month_moving_average"
    assert result.forecast_horizon_months == 1
    assert result.forecast_periods == ["2026-07"]
    assert result.forecasts[0].predicted_bookings == 10
    assert result.evaluation.evaluation_start == "2026-04"
    assert result.evaluation.evaluation_end == "2026-06"
    assert result.evaluation.observations == 3
    assert result.evaluation.mae == 4
    assert result.evaluation.baseline == "last_month_naive"
    assert result.evaluation.baseline_mae == 2
    assert any("higher MAE" in limitation for limitation in result.limitations)


def test_demand_skips_invalid_missing_dates_and_non_demand_statuses():
    result = build_demand_trends([
        (BookingStatus.COMPLETED, None, "Heavy"),
        (BookingStatus.APPROVED, date(2026, 1, 1), " "),
        (BookingStatus.PENDING, date(2026, 1, 1), "Heavy"),
    ])
    assert result.historical_periods == []
    assert result.categories == []
    assert result.forecasts == []
    assert result.insufficient_history


def test_only_approved_and_completed_are_historical_statuses():
    from app.services.ai_demand_service import HISTORICAL_STATUSES as demand
    from app.services.ai_recommendation_service import HISTORICAL_STATUSES as rec
    assert set(demand) == {BookingStatus.APPROVED, BookingStatus.COMPLETED}
    assert set(rec) == {BookingStatus.APPROVED, BookingStatus.COMPLETED}


def test_demand_includes_approved_completed_and_excludes_other_statuses():
    rows = [
        (BookingStatus.APPROVED, date(2026, 1, 1), "Heavy"),
        (BookingStatus.COMPLETED, date(2026, 1, 2), "Heavy"),
        (BookingStatus.PENDING, date(2026, 1, 3), "Heavy"),
        (BookingStatus.REJECTED, date(2026, 1, 4), "Heavy"),
        (BookingStatus.CANCELLED, date(2026, 1, 5), "Heavy"),
    ]
    result = build_demand_trends(rows)
    assert result.historical_periods == ["2026-01"]
    assert result.categories[0].demand_counts == [2]
