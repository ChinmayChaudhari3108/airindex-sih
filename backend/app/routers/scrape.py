from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import USE_MOCK_SOURCE
from app.schemas import ScrapeRunRequest, ScrapeRunResult
from app.scraper.runner import run_scrape

router = APIRouter(prefix="/api/v1/scrape", tags=["scrape"])


@router.post("/run", response_model=ScrapeRunResult)
async def trigger_scrape(payload: ScrapeRunRequest, db: Session = Depends(get_db)):
    """
    Runs one scrape + ETL pass across the configured (or requested)
    route basket and lead times, and upserts results into Postgres.
    In production this also runs on a schedule — see app/scheduler.py.
    """
    count = await run_scrape(db, routes=payload.routes, lead_times=payload.lead_times)
    return ScrapeRunResult(
        records_ingested=count,
        source_mode="mock" if USE_MOCK_SOURCE else "live",
        observed_date=date.today(),
    )
