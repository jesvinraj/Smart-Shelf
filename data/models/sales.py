"""Sales & Transaction models: Customer, PurchaseOrder, PurchaseOrderItem,
Sale, SaleItem (batch-tracked for FEFO), Payment.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from data.database import db


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True)
    po_number = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expected_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="ORDERED")  # DRAFT | ORDERED | RECEIVED | CANCELLED
    total_amount = Column(Float, default=0.0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    received_quantity = Column(Integer, default=0)
    unit_cost = Column(Float, nullable=False)
    batch_code = Column(String(50), nullable=True)
    expiry_date = Column(DateTime, nullable=True)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")


class Customer(db.Model):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(120), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Sale(db.Model):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sale_date = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    status = Column(String(20), default="COMPLETED")
    payment_method = Column(String(20), default="CASH")
    notes = Column(Text, nullable=True)

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="sale", uselist=False)


class SaleItem(db.Model):
    """Line item with batch linkage so FEFO allocations are fully tracked."""

    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("stock_batches.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    line_total = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")
    batch = relationship("StockBatch")


class Payment(db.Model):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    method = Column(String(20), default="CASH")
    amount = Column(Float, nullable=False)
    paid_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sale = relationship("Sale", back_populates="payment")
