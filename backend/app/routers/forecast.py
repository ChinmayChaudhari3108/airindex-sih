from fastapi import APIRouter, Query
from app.services import forecast_service

router = APIRouter(prefix="/api/v1/index", tags=["forecast"])

@router.get("/forecast")
def get_forecast(
    route: str = Query("DEL-BOM", description="Origin-destination route pair, e.g. DEL-BOM"),
    horizon_days: int = Query(14, ge=1, le=30, description="Forecast horizon in days"),
    lead_time: int = Query(14, ge=1, le=60, description="Lead time baseline in days")
):
    """
    Get AI Price Index forecast for a specific route with confidence bounds and recommendations.
    """
    return forecast_service.generate_forecast(
        route=route,
        horizon_days=horizon_days,
        lead_time=lead_time
    )
