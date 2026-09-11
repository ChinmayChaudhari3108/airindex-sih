"""
Scheduled scraping — "Fast and efficient scheduled data processing"
(Non-functionality: Performance) and daily/weekly/monthly signal
production (Innovation & Uniqueness slide).

Run alongside the API, e.g. as a separate process:
    python -m app.scheduler
"""
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import SessionLocal
from app.scraper.runner import run_scrape

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airindex.scheduler")


async def scheduled_scrape_job():
    db = SessionLocal()
    try:
        count = await run_scrape(db)
        logger.info("Scheduled scrape complete: %s records ingested", count)
    except Exception:
        logger.exception("Scheduled scrape failed")
    finally:
        db.close()


def main():
    scheduler = AsyncIOScheduler()
    # Every 6 hours by default — adjust to match source rate limits / ToS.
    # next_run_time=datetime.now() makes it fire once immediately on startup
    # (rather than being added paused, which is what next_run_time=None does
    # in APScheduler), then every 6h after that.
    scheduler.add_job(scheduled_scrape_job, "interval", hours=6, next_run_time=datetime.now())
    scheduler.start()
    logger.info("AIRINDEX scheduler started (every 6h).")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
