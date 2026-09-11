from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import DEFAULT_REFERENCE_LEAD_TIME
from app.pipeline.index_engine import (
    compute_index_trend, compute_heatmap, compute_elasticity, compute_airline_comparison
)
from app.schemas import (
    IndexTrendResponse, IndexPoint, HeatmapResponse, HeatmapCell,
    ElasticityResponse, ElasticityPoint, AirlineComparisonPoint,
)

router = APIRouter(prefix="/api/v1/index", tags=["index"])


@router.get("/trend", response_model=IndexTrendResponse)
def get_trend(
    route: Optional[List[str]] = Query(default=None),
    lead_time: int = Query(default=DEFAULT_REFERENCE_LEAD_TIME),
    window_days: int = Query(default=45, ge=7, le=45),
    aggregation: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db),
):
    series = compute_index_trend(
        db,
        route_codes=route,
        reference_lead_time_days=lead_time,
        window_days=window_days,
        aggregation=aggregation,
    )
    return IndexTrendResponse(
        routes=route or [],
        reference_lead_time_days=lead_time,
        aggregation=aggregation,
        points=[IndexPoint(date=p["date"], index_value=p["index_value"]) for p in series],
    )


@router.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap(
    route: Optional[List[str]] = Query(default=None),
    window_days: int = Query(default=45, ge=7, le=45),
    db: Session = Depends(get_db),
):
    cells = compute_heatmap(db, route_codes=route, window_days=window_days)
    return HeatmapResponse(
        window_days=window_days,
        cells=[HeatmapCell(**c) for c in cells],
    )


@router.get("/elasticity", response_model=ElasticityResponse)
def get_elasticity(
    route: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_db),
):
    points = compute_elasticity(db, route_codes=route)
    return ElasticityResponse(
        routes=route or [],
        points=[ElasticityPoint(**p) for p in points],
    )


@router.get("/airlines", response_model=List[AirlineComparisonPoint])
def get_airline_comparison(
    route: Optional[List[str]] = Query(default=None),
    lead_time: int = Query(default=DEFAULT_REFERENCE_LEAD_TIME),
    db: Session = Depends(get_db),
):
    rows = compute_airline_comparison(db, route_codes=route, lead_time_days=lead_time)
    return [AirlineComparisonPoint(**r) for r in rows]
