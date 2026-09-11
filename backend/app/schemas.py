from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class FareObservationOut(BaseModel):
    observed_date: date
    route_code: str
    airline: str
    lead_time_days: int
    base_fare: float
    tax: float
    total_fare: float
    available: bool
    source: str

    class Config:
        from_attributes = True


class IndexPoint(BaseModel):
    date: date
    index_value: float


class IndexTrendResponse(BaseModel):
    routes: List[str]
    reference_lead_time_days: int
    aggregation: str
    points: List[IndexPoint]


class HeatmapCell(BaseModel):
    route_code: str
    lead_time_days: int
    avg_fare: float
    pct_change_vs_window_start: float


class HeatmapResponse(BaseModel):
    window_days: int
    cells: List[HeatmapCell]


class ElasticityPoint(BaseModel):
    lead_time_days: int
    avg_fare: float


class ElasticityResponse(BaseModel):
    routes: List[str]
    points: List[ElasticityPoint]


class AirlineComparisonPoint(BaseModel):
    airline: str
    avg_fare: float


class ScrapeRunRequest(BaseModel):
    routes: Optional[List[str]] = None       # None => use full basket
    lead_times: Optional[List[int]] = None   # None => use configured lead times


class ScrapeRunResult(BaseModel):
    records_ingested: int
    source_mode: str
    observed_date: date
