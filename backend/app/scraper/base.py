from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class RawFareQuote:
    """One quote as it comes off a source, before validation/normalization."""
    observed_date: date
    route_code: str
    airline: str
    lead_time_days: int
    base_fare: float
    tax: float
    available: bool
    source: str


class BaseFareSource(ABC):
    """
    Every fare source (mock, a specific airline site, an OTA) implements
    this interface, so the runner and pipeline don't care where the data
    came from. This is the "modular source connectors" point from the
    Feasibility slide (Maintainability).
    """

    name: str = "base"

    @abstractmethod
    async def fetch_quotes(self, route_code: str, lead_time_days: int) -> List[RawFareQuote]:
        """Return raw fare quotes for one route + lead time, across airlines."""
        raise NotImplementedError
