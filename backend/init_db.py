"""
Creates tables and backfills `window_days` of history using the mock
source, so the API/dashboard has data to show immediately after setup.

Usage:
    python init_db.py
"""
import asyncio
from datetime import date, timedelta

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import Base, engine, SessionLocal
from app.config import ROUTE_BASKET, LEAD_TIMES_DAYS
from app.models import FareObservation
from app.scraper.mock_source import MockFareSource
from app.pipeline.validate import validate_quotes
from app.pipeline.normalize import normalize_quote

BACKFILL_DAYS = 45


async def backfill():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    source = MockFareSource()
    route_codes = [r["code"] for r in ROUTE_BASKET]

    try:
        for i in range(BACKFILL_DAYS):
            observed_date = date.today() - timedelta(days=BACKFILL_DAYS - 1 - i)
            raw = []
            for route_code in route_codes:
                for lead_time in LEAD_TIMES_DAYS:
                    quotes = await source.fetch_quotes(route_code, lead_time)
                    for q in quotes:
                        q.observed_date = observed_date
                    raw.extend(quotes)

            clean = validate_quotes(raw)
            normalized = [normalize_quote(q) for q in clean]

            for n in normalized:
                stmt = pg_insert(FareObservation).values(
                    observed_date=n.observed_date,
                    route_code=n.route_code,
                    airline=n.airline,
                    lead_time_days=n.lead_time_days,
                    base_fare=n.base_fare,
                    tax=n.tax,
                    total_fare=n.base_fare + n.tax,
                    available=n.available,
                    source=n.source,
                ).on_conflict_do_nothing(
                    index_elements=["observed_date", "route_code", "airline", "lead_time_days", "source"],
                )
                db.execute(stmt)
            db.commit()
            print(f"Seeded {observed_date} ({len(normalized)} records)")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(backfill())
