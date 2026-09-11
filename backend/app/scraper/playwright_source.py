"""
PlaywrightFareSource — template for a real, JS-rendered fare source.

This is the connector referenced on the Technical Approach slide
("Playwright / Selenium — JS-rendered source handling"). It is left as
a working *template*, not a finished scraper against a specific airline
or OTA, because:

  1. Real selectors are site-specific and change frequently — hardcoding
     them here would break on the first UI update.
  2. Each target site's robots.txt and Terms of Service need to be
     checked before enabling live scraping against it (Feasibility
     slide: "Compliance").

To wire up a real source:
  1. Confirm the target's /robots.txt allows the paths you need
     (see `_is_allowed_by_robots` below).
  2. Fill in `_build_search_url` and the CSS/XPath selectors in
     `_extract_quotes_from_page`.
  3. Register an instance of this class (or a subclass per source) in
     `runner.py`'s SOURCES list.

Requires: pip install playwright && playwright install chromium
"""
import asyncio
import random
import urllib.robotparser as robotparser
from datetime import date
from typing import List
from urllib.parse import urlparse

from playwright.async_api import async_playwright

from app.config import SCRAPER_MIN_DELAY_SECONDS, SCRAPER_MAX_DELAY_SECONDS, SCRAPER_USER_AGENT
from app.scraper.base import BaseFareSource, RawFareQuote


def _is_allowed_by_robots(url: str, user_agent: str = SCRAPER_USER_AGENT) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # If robots.txt can't be fetched, fail closed — don't scrape.
        return False
    return rp.can_fetch(user_agent, url)


class PlaywrightFareSource(BaseFareSource):
    """
    Generic JS-rendered fare source. Subclass and override
    `_build_search_url` and `_extract_quotes_from_page` per target site.
    """

    name = "playwright_template"
    base_url = "https://example-airline-or-ota.example"  # TODO: real host

    def _build_search_url(self, route_code: str, lead_time_days: int) -> str:
        """TODO: build the real search URL for this route + lead time."""
        origin, destination = route_code.split("-")
        # Placeholder query-string shape — replace with the real one.
        return f"{self.base_url}/search?from={origin}&to={destination}&leadDays={lead_time_days}"

    async def _extract_quotes_from_page(self, page, route_code, lead_time_days) -> List[RawFareQuote]:
        """
        TODO: replace with real selectors for the target site, e.g.:

            rows = await page.query_selector_all(".fare-card")
            for row in rows:
                airline = await (await row.query_selector(".airline-name")).inner_text()
                fare_text = await (await row.query_selector(".fare-amount")).inner_text()
                ...

        Return one RawFareQuote per airline result found on the page.
        """
        raise NotImplementedError(
            "Fill in real selectors for this source before enabling it in runner.py"
        )

    async def fetch_quotes(self, route_code: str, lead_time_days: int) -> List[RawFareQuote]:
        url = self._build_search_url(route_code, lead_time_days)

        if not _is_allowed_by_robots(url):
            raise PermissionError(f"robots.txt disallows fetching {url}")

        # Politeness delay between requests (Feasibility: rate-limited collection).
        await asyncio.sleep(random.uniform(SCRAPER_MIN_DELAY_SECONDS, SCRAPER_MAX_DELAY_SECONDS))

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=SCRAPER_USER_AGENT)
            page = await context.new_page()
            try:
                await page.goto(url, wait_until="networkidle", timeout=30_000)
                quotes = await self._extract_quotes_from_page(page, route_code, lead_time_days)
            finally:
                await browser.close()

        for q in quotes:
            q.observed_date = date.today()
            q.source = self.name
        return quotes
