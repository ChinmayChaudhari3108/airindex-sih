from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, UniqueConstraint, Index
)

from app.database import Base


class FareObservation(Base):
    """
    A single normalized fare quote: one route, one airline, one lead time,
    observed on one day. This is the table the Index Engine reads from.
    Corresponds to slide 2's "Stores route, airline, fare, tax, availability".
    """
    __tablename__ = "fare_observations"

    id = Column(Integer, primary_key=True, index=True)
    observed_date = Column(Date, nullable=False, default=date.today, index=True)
    route_code = Column(String(16), nullable=False, index=True)   # e.g. "DEL-BOM"
    airline = Column(String(64), nullable=False, index=True)
    lead_time_days = Column(Integer, nullable=False, index=True)  # T+n

    base_fare = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    total_fare = Column(Float, nullable=False)
    available = Column(Boolean, nullable=False, default=True)

    source = Column(String(64), nullable=False)  # e.g. "mock", "indigo_direct", "ota_x"
    scraped_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "observed_date", "route_code", "airline", "lead_time_days", "source",
            name="uq_fare_observation_unique_quote",
        ),
        Index("ix_fare_lookup", "observed_date", "route_code", "lead_time_days"),
    )


class IndexSnapshot(Base):
    """
    A computed Base-100 index value for a given date + reference lead time
    + route basket. Cached so the dashboard doesn't recompute on every read.
    """
    __tablename__ = "index_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(Date, nullable=False, index=True)
    reference_lead_time_days = Column(Integer, nullable=False)
    route_basket_key = Column(String(256), nullable=False)  # sorted, comma-joined route codes
    index_value = Column(Float, nullable=False)
    anchor_value = Column(Float, nullable=False)  # raw weighted fare on the anchor date
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "snapshot_date", "reference_lead_time_days", "route_basket_key",
            name="uq_index_snapshot_unique",
        ),
    )
