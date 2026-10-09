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


class CategoryForecast(BaseModel):
    category: str
    period: str
    predicted_bookings: float = Field(ge=0)


class ForecastEvaluation(BaseModel):
    method: str
    baseline: str
    evaluation_start: str
    evaluation_end: str
    observations: int = Field(ge=1)
    mae: float = Field(ge=0)
    baseline_mae: float = Field(ge=0)


class DemandTrendResponse(BaseModel):
    historical_period_count: int
    historical_periods: list[str]
    categories: list[CategoryDemand]
    forecast_available: bool
    status: str
    insufficient_history: bool
    message: str | None = None
    forecast_method: str | None = None
    forecast_horizon_months: int = 1
    forecast_periods: list[str] = Field(default_factory=list)
    forecasts: list[CategoryForecast] = Field(default_factory=list)
    evaluation: ForecastEvaluation | None = None
    limitations: list[str] = Field(default_factory=list)
