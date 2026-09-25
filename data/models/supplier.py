"""Supplier Management model."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from data.database import db


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, index=True)
    contact_person = Column(String(120), nullable=True)
    email = Column(String(120), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    batches = relationship("StockBatch", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
