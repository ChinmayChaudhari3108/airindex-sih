from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FareObservation
from app.schemas import FareObservationOut

router = APIRouter(prefix="/api/v1/fares", tags=["fares"])


@router.get("", response_model=List[FareObservationOut])
def list_fares(
    route: Optional[List[str]] = Query(default=None),
    lead_time: Optional[int] = Query(default=None),
    limit: int = Query(default=50, le=500),
    db: Session = Depends(get_db),
):
    """Most recent normalized fare observations — the raw feed table on the dashboard."""
    q = db.query(FareObservation)
    if route:
        q = q.filter(FareObservation.route_code.in_(route))
    if lead_time is not None:
        q = q.filter(FareObservation.lead_time_days == lead_time)
    q = q.order_by(FareObservation.scraped_at.desc()).limit(limit)
    return q.all()
