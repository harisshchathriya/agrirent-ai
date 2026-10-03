import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User, UserRole
from app.schemas.ai_schema import DemandTrendResponse, RecommendationResponse
from app.services.ai_demand_service import get_demand_trends
from app.services.ai_recommendation_service import get_recommendations

logger = logging.getLogger("agrirent.ai")
router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/recommendations", response_model=RecommendationResponse)
def recommendations(
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if getattr(current_user.role, "value", current_user.role) != UserRole.FARMER.value:
        raise HTTPException(status_code=403, detail="Only farmers can access recommendations.")
    try:
        return get_recommendations(db, current_user.id, limit)
    except SQLAlchemyError as exc:
        logger.exception("Unable to load equipment recommendations")
        raise HTTPException(status_code=503, detail="Recommendations are temporarily unavailable.") from exc


@router.get("/demand-trends", response_model=DemandTrendResponse)
def demand_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_demand_trends(db)
    except SQLAlchemyError as exc:
        logger.exception("Unable to load historical demand trends")
        raise HTTPException(status_code=503, detail="Demand trends are temporarily unavailable.") from exc
