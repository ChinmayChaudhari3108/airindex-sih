"""
MockFareSource

Generates plausible synthetic fare quotes so the full ETL pipeline
(validate -> normalize -> index engine -> API -> dashboard) is runnable
and demoable without depending on live, permitted scraping targets.

Swap this out for PlaywrightFareSource (see playwright_source.py) once
real, ToS-compliant source connectors are wired up for specific
airline/OTA pages.
"""
import random
from datetime import date
from typing import List

from app.config import AIRLINES
from app.scraper.base import BaseFareSource, RawFareQuote

_ROUTE_BASE_FARE = {
    "DEL-BOM": 5200, "DEL-BLR": 5800, "BOM-BLR": 4300,
    "DEL-CCU": 6100, "BLR-HYD": 3400, "MAA-DEL": 6600,
}
_AIRLINE_FACTOR = {"IndiGo": 1.00, "Air India": 1.12, "SpiceJet": 0.94, "Akasa Air": 0.97}


def _lead_time_multiplier(days: int) -> float:
    # Fares rise sharply as departure nears (elasticity curve).
    import math
    return 1 + 0.9 * math.exp(-days / 9)


class MockFareSource(BaseFareSource):
    name = "mock"

    async def fetch_quotes(self, route_code: str, lead_time_days: int) -> List[RawFareQuote]:
        base = _ROUTE_BASE_FARE.get(route_code, 5000)
        market_fare = base * _lead_time_multiplier(lead_time_days) * random.uniform(0.97, 1.03)

        quotes = []
        for airline in AIRLINES:
            noise = random.uniform(0.94, 1.06)
            fare = round(market_fare * _AIRLINE_FACTOR.get(airline, 1.0) * noise / 10) * 10
            tax = round(fare * 0.18 / 10) * 10
            available = random.random() > 0.08
            quotes.append(RawFareQuote(
                observed_date=date.today(),
                route_code=route_code,
                airline=airline,
                lead_time_days=lead_time_days,
                base_fare=float(fare),
                tax=float(tax),
                available=available,
                source=self.name,
            ))
        return quotes
