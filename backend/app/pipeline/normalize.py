"""
Stage 4 — Normalization (Technical Approach slide's Data Flow).

Standardizes base fare, taxes and charges into one common schema
regardless of which source the quote came from.
"""
from app.scraper.base import RawFareQuote


def normalize_quote(q: RawFareQuote) -> RawFareQuote:
    # Round to the nearest rupee; different sources report varying decimal
    # precision (some show paise, some round to 10s).
    q.base_fare = round(q.base_fare)
    q.tax = round(q.tax)
    return q
