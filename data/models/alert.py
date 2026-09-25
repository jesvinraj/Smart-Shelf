"""Alert & Administration models: Notification and AuditLog."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from data.database import db


class Notification(db.Model):
    """In-app alert pushed to staff (near-expiry, high-risk, expired, low-stock)."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(120), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(20), nullable=False, default="SYSTEM")
    severity = Column(String(20), default="INFO")  # INFO | WARNING | CRITICAL
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    link = Column(String(120), nullable=True)
    is_read = Column(Integer, default=0)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    user = relationship("User")


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    user = relationship("User")
