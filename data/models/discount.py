"""Discount & Promotion Management model (approval workflow)."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from data.database import db
from data.models.enums import PromoStatus


class Promotion(db.Model):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    discount_type = Column(String(20), nullable=False)  # PERCENTAGE | FIXED | BUY_X_GET_Y
    value = Column(Float, nullable=False)
    suggested_discount = Column(Float, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    min_quantity = Column(Integer, default=1)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(20), default=PromoStatus.DRAFT.value)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product")
    category = relationship("Category")

    @property
    def is_active(self) -> bool:
        return self.status == PromoStatus.ACTIVE.value
