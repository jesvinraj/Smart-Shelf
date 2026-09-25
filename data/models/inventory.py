"""Inventory Management models: Location, InventoryMovement, LocationTransfer.
(StockBatch lives in data/models/batch.py; Wastage lives in data/models/waste.py.)
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from data.database import db


class Location(db.Model):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    zone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)

    batches = relationship("StockBatch", back_populates="location")


class InventoryMovement(db.Model):
    """Audit ledger of every stock modification."""

    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    batch_id = Column(Integer, ForeignKey("stock_batches.id"), nullable=True)
    movement_type = Column(String(20), nullable=False)  # IN | OUT | TRANSFER | ADJUSTMENT | WASTAGE
    quantity = Column(Integer, nullable=False)
    reference = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    movement_date = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )


class LocationTransfer(db.Model):
    __tablename__ = "location_transfers"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    from_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    to_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    transferred_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    transferred_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(Text, nullable=True)
