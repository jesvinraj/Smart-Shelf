"""Product Management model: Category, Brand, Product."""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from data.database import db


class Category(db.Model):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    products = relationship("Product", back_populates="category")


class Brand(db.Model):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    products = relationship("Product", back_populates="brand")


class Product(db.Model):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    barcode = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    unit = Column(String(20), default="pcs")
    unit_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    tax_rate = Column(Float, default=0.0)
    shelf_life_days = Column(Integer, nullable=True)
    storage_condition = Column(String(20), default="AMBIENT")  # AMBIENT | CHILLED | FROZEN
    reorder_level = Column(Integer, default=10)
    lead_time_days = Column(Integer, default=1)
    image_url = Column(String(255), nullable=True)
    is_perishable = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    batches = relationship("StockBatch", back_populates="product", cascade="all, delete-orphan")

    @property
    def total_stock(self) -> int:
        return sum(b.quantity for b in self.batches if b.quantity is not None)
