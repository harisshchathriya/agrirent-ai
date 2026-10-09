from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import get_current_user
from app.database.session import get_db
from app.main import app
from app.models.user import UserRole
from app.schemas.ai_schema import (
    DemandTrendResponse,
    EquipmentRecommendation,
    RecommendationResponse,
)


def user(role=UserRole.FARMER):
    return type("AuthenticatedUser", (), {"id": uuid4(), "role": role})()


def setup_client(current_user=None):
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    if current_user is not None:
        app.dependency_overrides[get_current_user] = lambda: current_user
    return TestClient(app), db


def clear_overrides():
    app.dependency_overrides.clear()


def test_ai_routes_require_authentication():
    client, _ = setup_client()
    try:
        assert client.get("/ai/recommendations").status_code == 401
        assert client.get("/ai/demand-trends").status_code == 401
    finally:
        clear_overrides()


def test_recommendations_use_jwt_identity_and_response(monkeypatch):
    from app.api import ai
    authenticated = user()
    client, db = setup_client(authenticated)
    recommendation = EquipmentRecommendation(
        equipment_id=uuid4(), name="Tractor", category="Heavy",
        location="Trichy", score=5, explanation="Historical relevance.")
    response_data = RecommendationResponse(
        recommendations=[recommendation], personalized=True, fallback_used=False)
    service = MagicMock(return_value=response_data)
    monkeypatch.setattr(ai, "get_recommendations", service)
    arbitrary_farmer = uuid4()
    try:
        response = client.get(
            f"/ai/recommendations?limit=2&farmer_id={arbitrary_farmer}")
        assert response.status_code == 200
        assert response.json()["recommendations"][0]["equipment_id"] == str(
            recommendation.equipment_id)
        service.assert_called_once_with(db, authenticated.id, 2)
    finally:
        clear_overrides()


def test_recommendation_limit_and_farmer_role_are_validated(monkeypatch):
    from app.api import ai
    service = MagicMock()
    monkeypatch.setattr(ai, "get_recommendations", service)
    client, _ = setup_client(user())
    try:
        assert client.get("/ai/recommendations?limit=0").status_code == 422
        assert client.get("/ai/recommendations?limit=21").status_code == 422
        service.assert_not_called()
    finally:
        clear_overrides()

    client, _ = setup_client(user(UserRole.OWNER))
    try:
        assert client.get("/ai/recommendations").status_code == 403
        service.assert_not_called()
    finally:
        clear_overrides()


def test_recommendations_accept_string_role_value(monkeypatch):
    """Farmer identity must be accepted even when role is a plain string, not an enum."""
    from app.api import ai
    service = MagicMock(return_value=RecommendationResponse(
        recommendations=[], personalized=False, fallback_used=False))
    monkeypatch.setattr(ai, "get_recommendations", service)
    # Role stored as a plain string (no .value attribute) — must not crash
    client, _ = setup_client(user("farmer"))
    try:
        response = client.get("/ai/recommendations")
        assert response.status_code == 200
        service.assert_called_once()
    finally:
        clear_overrides()


def test_demand_response_and_insufficient_history(monkeypatch):
    from app.api import ai
    data = DemandTrendResponse(
        historical_period_count=1, historical_periods=["2026-08"],
        categories=[], forecast_available=False, status="insufficient_history",
        insufficient_history=True, message="Insufficient history.")
    service = MagicMock(return_value=data)
    monkeypatch.setattr(ai, "get_demand_trends", service)
    client, db = setup_client(user(UserRole.OWNER))
    try:
        response = client.get("/ai/demand-trends")
        assert response.status_code == 200
        assert response.json()["insufficient_history"] is True
        assert response.json()["forecast_available"] is False
        assert response.json()["forecasts"] == []
        assert response.json()["forecast_method"] is None
        service.assert_called_once_with(db)
    finally:
        clear_overrides()


def test_database_errors_return_safe_service_message(monkeypatch):
    from app.api import ai
    monkeypatch.setattr(
        ai, "get_demand_trends",
        MagicMock(side_effect=SQLAlchemyError("private connection details")))
    client, _ = setup_client(user())
    try:
        response = client.get("/ai/demand-trends")
        assert response.status_code == 503
        assert response.json()["detail"] == "Demand trends are temporarily unavailable."
        assert "private connection details" not in response.text
    finally:
        clear_overrides()
