"""Batch Management model: StockBatch.

A discrete quantity of a product with batch code, batch number, manufacturing
date and expiry date. FEFO ordering is applied on these records.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from data.database import db


class StockBatch(db.Model):
    __tablename__ = "stock_batches"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    batch_code = Column(String(50), nullable=False, index=True)
    batch_number = Column(String(50), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    cost_price = Column(Float, nullable=True)
    manufactured_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="batches")
    location = relationship("Location", back_populates="batches")
    supplier = relationship("Supplier", back_populates="batches")
