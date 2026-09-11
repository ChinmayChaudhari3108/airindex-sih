"""
Central configuration for the AIRINDEX pipeline.

This mirrors the "representative route basket" and lead-time buckets
described in the SIH26056 proposal (Technical Approach / Data Flow).
Weights should ideally be derived from DGCA passenger-traffic shares
(see slide 4 / 6 references) — sample values are provided here.
"""
import os

# Default to SQLite for local development (no Postgres setup needed).
# Set DATABASE_URL env-var to a postgres:// URI in production.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./airindex.db",
)

# Representative route basket + weight (sums to 1.0).
# In production, source these shares from DGCA domestic traffic stats.
ROUTE_BASKET = [
    {"code": "DEL-BOM", "label": "Delhi -> Mumbai", "weight": 0.24},
    {"code": "DEL-BLR", "label": "Delhi -> Bengaluru", "weight": 0.20},
    {"code": "BOM-BLR", "label": "Mumbai -> Bengaluru", "weight": 0.16},
    {"code": "DEL-CCU", "label": "Delhi -> Kolkata", "weight": 0.14},
    {"code": "BLR-HYD", "label": "Bengaluru -> Hyderabad", "weight": 0.13},
    {"code": "MAA-DEL", "label": "Chennai -> Delhi", "weight": 0.13},
]

LEAD_TIMES_DAYS = [1, 3, 7, 14, 21, 30, 45]

AIRLINES = ["IndiGo", "Air India", "SpiceJet", "Akasa Air"]

# Default reference lead time used for the headline index figure.
DEFAULT_REFERENCE_LEAD_TIME = 14

# Scraper politeness settings (Feasibility slide: "Compliance").
SCRAPER_MIN_DELAY_SECONDS = 2.0
SCRAPER_MAX_DELAY_SECONDS = 5.0
SCRAPER_USER_AGENT = "AIRINDEX-Bot/1.0 (+https://example.gov.in/airindex; research use)"

# When true, the pipeline uses MockSource instead of live Playwright
# scraping. Keep this True until real, permitted source connectors
# (with their own selectors and a checked robots.txt) are added —
# see backend/app/scraper/playwright_source.py.
USE_MOCK_SOURCE = os.getenv("AIRINDEX_USE_MOCK_SOURCE", "true").lower() == "true"
