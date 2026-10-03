from uuid import UUID

from pydantic import BaseModel, Field


class EquipmentRecommendation(BaseModel):
    equipment_id: UUID
    name: str
    category: str
    location: str
    score: int = Field(ge=0)
    explanation: str


class RecommendationResponse(BaseModel):
    recommendations: list[EquipmentRecommendation]
    personalized: bool
    fallback_used: bool
    message: str | None = None


class CategoryDemand(BaseModel):
    category: str
    periods: list[str]
    demand_counts: list[int]


class DemandTrendResponse(BaseModel):
    historical_period_count: int
    historical_periods: list[str]
    categories: list[CategoryDemand]
    forecast_available: bool
    status: str
    insufficient_history: bool
    message: str | None = None
    # The model has intentionally not been selected; no forecast field yet.
