"""
Orchestrates a full scrape run: for each route in the basket and each
lead time, pull quotes from the active source(s), validate, normalize,
and upsert into fare_observations.

This is "Stage 2 — Data Extraction" through "Stage 4 — Normalization"
on the Technical Approach slide's Data Flow column.
"""
from typing import List, Optional

from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.dialects import sqlite as sqlite_dialect
from sqlalchemy.dialects import postgresql as pg_dialect

from app.config import ROUTE_BASKET, LEAD_TIMES_DAYS, USE_MOCK_SOURCE, DATABASE_URL
from app.models import FareObservation
from app.scraper.base import BaseFareSource, RawFareQuote
from app.scraper.mock_source import MockFareSource
from app.pipeline.validate import validate_quotes
from app.pipeline.normalize import normalize_quote


def _active_sources() -> List[BaseFareSource]:
    if USE_MOCK_SOURCE:
        return [MockFareSource()]
    # TODO: once real connectors are ready, add them here, e.g.:
    # from app.scraper.playwright_source import PlaywrightFareSource
    # return [IndiGoDirectSource(), SomeOtaSource()]
    return [MockFareSource()]


def _is_postgres() -> bool:
    return DATABASE_URL.startswith("postgresql")


async def run_scrape(
    db: Session,
    routes: Optional[List[str]] = None,
    lead_times: Optional[List[int]] = None,
) -> int:
    """Runs one full scrape + ETL pass. Returns number of records ingested."""
    route_codes = routes or [r["code"] for r in ROUTE_BASKET]
    leads = lead_times or LEAD_TIMES_DAYS
    sources = _active_sources()

    raw_quotes: List[RawFareQuote] = []
    for source in sources:
        for route_code in route_codes:
            for lead_time in leads:
                quotes = await source.fetch_quotes(route_code, lead_time)
                raw_quotes.extend(quotes)

    clean_quotes = validate_quotes(raw_quotes)
    normalized = [normalize_quote(q) for q in clean_quotes]

    ingested = 0
    for n in normalized:
        values = dict(
            observed_date=n.observed_date,
            route_code=n.route_code,
            airline=n.airline,
            lead_time_days=n.lead_time_days,
            base_fare=n.base_fare,
            tax=n.tax,
            total_fare=n.base_fare + n.tax,
            available=n.available,
            source=n.source,
        )

        if _is_postgres():
            # PostgreSQL-specific ON CONFLICT DO UPDATE (most efficient)
            from sqlalchemy.dialects.postgresql import insert as pg_insert
            stmt = pg_insert(FareObservation).values(**values).on_conflict_do_update(
                index_elements=["observed_date", "route_code", "airline", "lead_time_days", "source"],
                set_={
                    "base_fare": n.base_fare,
                    "tax": n.tax,
                    "total_fare": n.base_fare + n.tax,
                    "available": n.available,
                },
            )
        else:
            # SQLite / generic fallback: delete existing matching row then insert
            db.query(FareObservation).filter(
                FareObservation.observed_date == n.observed_date,
                FareObservation.route_code == n.route_code,
                FareObservation.airline == n.airline,
                FareObservation.lead_time_days == n.lead_time_days,
                FareObservation.source == n.source,
            ).delete(synchronize_session=False)

            stmt = FareObservation.__table__.insert().values(**values)

        db.execute(stmt)
        ingested += 1

    db.commit()
    return ingested
