"""Waste & Revenue Recovery model: Wastage."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from data.database import db


class Wastage(db.Model):
    """Expired/wasted product with loss, recovered revenue and savings."""

    __tablename__ = "wastage"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("stock_batches.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(20), default="EXPIRED")
    unit_cost = Column(Float, default=0.0)
    potential_loss = Column(Float, default=0.0)
    recovered_revenue = Column(Float, default=0.0)
    savings = Column(Float, default=0.0)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(Text, nullable=True)

    product = relationship("Product")
    batch = relationship("StockBatch")
    location = relationship("Location")
