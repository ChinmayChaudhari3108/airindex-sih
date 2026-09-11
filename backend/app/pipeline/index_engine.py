"""
Stage 5 — Index Engine (Technical Approach slide's Data Flow).

Applies representative route weights to fare observations stored in
Postgres to compute:
  - the weighted Base-100 Airfare Price Index over time
  - a route x lead-time heatmap
  - lead-time elasticity (avg fare by days-before-departure)
  - airline comparison at a given lead time
"""
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import ROUTE_BASKET, LEAD_TIMES_DAYS
from app.models import FareObservation


def _basket_weights(route_codes: List[str]) -> dict:
    weights = {r["code"]: r["weight"] for r in ROUTE_BASKET if r["code"] in route_codes}
    total = sum(weights.values()) or 1.0
    return {k: v / total for k, v in weights.items()}


def _latest_available_date(db: Session, route_codes: List[str]) -> date:
    """
    Most recent observed_date actually present for this route basket.
    Using this instead of date.today() means the heatmap/elasticity/airline
    panels keep showing the last real data instead of going blank on any
    day the scraper hasn't run yet (e.g. before the scheduler's next tick).
    """
    latest = (
        db.query(func.max(FareObservation.observed_date))
        .filter(FareObservation.route_code.in_(route_codes))
        .scalar()
    )
    return latest or date.today()


def _aggregate_points(points: List[dict], aggregation: str) -> List[dict]:
    """
    Resamples a daily [{date, index_value}, ...] series to weekly/monthly by
    keeping the last point observed in each ISO week / calendar month.
    """
    if aggregation == "daily" or not points:
        return points

    buckets: "dict" = {}
    for p in points:
        d = p["date"]
        if aggregation == "weekly":
            key = d.isocalendar()[:2]  # (iso_year, iso_week)
        elif aggregation == "monthly":
            key = (d.year, d.month)
        else:
            return points
        buckets[key] = p  # last point seen per bucket wins

    return list(buckets.values())


def compute_index_trend(
    db: Session,
    route_codes: Optional[List[str]] = None,
    reference_lead_time_days: int = 14,
    window_days: int = 45,
    aggregation: str = "daily",
) -> List[dict]:
    """
    Returns [{date, index_value}, ...] — weighted avg fare per day,
    normalized to 100 on the first day in the window. If aggregation is
    "weekly" or "monthly", the daily series is resampled accordingly.
    """
    route_codes = route_codes or [r["code"] for r in ROUTE_BASKET]
    weights = _basket_weights(route_codes)

    start_date = date.today() - timedelta(days=window_days - 1)

    rows = (
        db.query(
            FareObservation.observed_date,
            FareObservation.route_code,
            func.avg(FareObservation.total_fare).label("avg_fare"),
        )
        .filter(
            FareObservation.route_code.in_(route_codes),
            FareObservation.lead_time_days == reference_lead_time_days,
            FareObservation.observed_date >= start_date,
        )
        .group_by(FareObservation.observed_date, FareObservation.route_code)
        .order_by(FareObservation.observed_date)
        .all()
    )

    by_date: dict = {}
    for observed_date, route_code, avg_fare in rows:
        by_date.setdefault(observed_date, {})[route_code] = float(avg_fare)

    series = []
    for d in sorted(by_date.keys()):
        route_fares = by_date[d]
        weighted = sum(
            route_fares.get(code, 0) * w for code, w in weights.items() if code in route_fares
        )
        series.append({"date": d, "weighted_fare": weighted})

    if not series:
        return []

    anchor = series[0]["weighted_fare"] or 1.0
    daily_points = [
        {"date": p["date"], "index_value": round((p["weighted_fare"] / anchor) * 100, 2)}
        for p in series
    ]
    return _aggregate_points(daily_points, aggregation)


def compute_heatmap(
    db: Session,
    route_codes: Optional[List[str]] = None,
    window_days: int = 45,
) -> List[dict]:
    """Latest-day avg fare per route x lead-time, with % change vs window start."""
    route_codes = route_codes or [r["code"] for r in ROUTE_BASKET]
    latest_date = _latest_available_date(db, route_codes)
    start_date = latest_date - timedelta(days=window_days - 1)

    def avg_fare(observed_date, route_code, lead_time):
        result = (
            db.query(func.avg(FareObservation.total_fare))
            .filter(
                FareObservation.observed_date == observed_date,
                FareObservation.route_code == route_code,
                FareObservation.lead_time_days == lead_time,
            )
            .scalar()
        )
        return float(result) if result is not None else None

    cells = []
    for route_code in route_codes:
        for lead_time in LEAD_TIMES_DAYS:
            latest = avg_fare(latest_date, route_code, lead_time)
            start = avg_fare(start_date, route_code, lead_time)
            if latest is None:
                continue
            pct_change = ((latest - start) / start * 100) if start else 0.0
            cells.append({
                "route_code": route_code,
                "lead_time_days": lead_time,
                "avg_fare": round(latest, 2),
                "pct_change_vs_window_start": round(pct_change, 2),
            })
    return cells


def compute_elasticity(db: Session, route_codes: Optional[List[str]] = None) -> List[dict]:
    """Avg fare by lead time, latest day, across the selected basket."""
    route_codes = route_codes or [r["code"] for r in ROUTE_BASKET]
    latest_date = _latest_available_date(db, route_codes)

    rows = (
        db.query(
            FareObservation.lead_time_days,
            func.avg(FareObservation.total_fare).label("avg_fare"),
        )
        .filter(
            FareObservation.route_code.in_(route_codes),
            FareObservation.observed_date == latest_date,
        )
        .group_by(FareObservation.lead_time_days)
        .order_by(FareObservation.lead_time_days)
        .all()
    )
    return [{"lead_time_days": lt, "avg_fare": round(float(f), 2)} for lt, f in rows]


def compute_airline_comparison(
    db: Session,
    route_codes: Optional[List[str]] = None,
    lead_time_days: int = 14,
) -> List[dict]:
    route_codes = route_codes or [r["code"] for r in ROUTE_BASKET]
    latest_date = _latest_available_date(db, route_codes)

    rows = (
        db.query(
            FareObservation.airline,
            func.avg(FareObservation.total_fare).label("avg_fare"),
        )
        .filter(
            FareObservation.route_code.in_(route_codes),
            FareObservation.lead_time_days == lead_time_days,
            FareObservation.observed_date == latest_date,
        )
        .group_by(FareObservation.airline)
        .order_by(FareObservation.airline)
        .all()
    )
    return [{"airline": a, "avg_fare": round(float(f), 2)} for a, f in rows]
