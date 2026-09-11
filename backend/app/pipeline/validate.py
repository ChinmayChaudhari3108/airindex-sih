"""
Stage 3 — Validation (Technical Approach slide's Data Flow).

Flags/excludes: missing values, duplicate quotes, and implausible fares
(e.g. zero or negative), before anything reaches normalization.
"""
from typing import List

from app.scraper.base import RawFareQuote


def validate_quotes(quotes: List[RawFareQuote]) -> List[RawFareQuote]:
    seen = set()
    clean: List[RawFareQuote] = []

    for q in quotes:
        if q.base_fare is None or q.base_fare <= 0:
            continue
        if q.tax is None or q.tax < 0:
            continue
        if not q.route_code or not q.airline:
            continue

        key = (q.observed_date, q.route_code, q.airline, q.lead_time_days, q.source)
        if key in seen:
            continue
        seen.add(key)

        clean.append(q)

    return clean
