"""Alert & Notification Management service.

Generates alerts for near-expiry, high-risk, expired and low-stock products.
"""
from datetime import datetime

from data.database import db
from data.models import Notification, NotificationType, Product, StockBatch, User
from data.models.enums import Role


def _broadcast(title, message, ntype, severity="INFO", product_id=None, link=None):
    admins = User.query.filter(User.role.in_([Role.ADMIN.value, Role.MANAGER.value])).all()
    for u in admins:
        db.session.add(
            Notification(
                user_id=u.id, title=title, message=message, notification_type=ntype,
                severity=severity, product_id=product_id, link=link,
            )
        )
    db.session.add(
        Notification(
            title=title, message=message, notification_type=ntype,
            severity=severity, product_id=product_id, link=link,
        )
    )
    db.session.commit()


def notify_roles(roles, title, message, ntype="SYSTEM", severity="INFO", link=None):
    """Push a targeted notification to every user in the given roles (no global row)."""
    members = User.query.filter(User.role.in_([r.value for r in roles])).all()
    for u in members:
        db.session.add(
            Notification(
                user_id=u.id, title=title, message=message, notification_type=ntype,
                severity=severity, link=link,
            )
        )
    db.session.commit()


def alert_low_stock() -> int:
    """Alert for products at or below their reorder level. Returns count."""
    count = 0
    for p in Product.query.filter(Product.is_active.is_(True)).all():
        if p.total_stock <= p.reorder_level:
            _broadcast(
                f"Low stock: {p.name}",
                f"On hand {p.total_stock} is at/below reorder level {p.reorder_level}.",
                NotificationType.LOW_STOCK.value, severity="WARNING", product_id=p.id,
            )
            count += 1
    return count


def alert_expiry(alert_days: int) -> dict:
    """Alert for expired and near-expiry batches. Returns counts."""
    from services.expiry_service import scan_expiry

    result = scan_expiry(alert_days=alert_days, notify=False)
    for bid in result["expired"]:
        b = db.session.get(StockBatch, bid)
        if b:
            _broadcast(
                "Expired batch",
                f"Batch {b.batch_code or b.id} of {b.product.name if b.product else b.product_id} has expired.",
                NotificationType.EXPIRED.value, severity="CRITICAL", product_id=b.product_id,
            )
    for bid in result["expiring_soon"]:
        b = db.session.get(StockBatch, bid)
        if b:
            _broadcast(
                "Near-expiry",
                f"Batch {b.batch_code or b.id} of {b.product.name if b.product else b.product_id} expires within {alert_days} days.",
                NotificationType.NEAR_EXPIRY.value, severity="WARNING", product_id=b.product_id,
            )
    return result


def alert_high_risk(high_threshold: int = 70) -> int:
    """Alert for batches above a spoilage-risk threshold. Returns count."""
    from engines.demand_engine import sales_velocity
    from engines.risk_engine import batch_risk

    velocity = {}
    for row in sales_velocity(days=30).to_dict("records"):
        velocity[row["product_id"]] = row["velocity_per_day"]

    count = 0
    for b in StockBatch.query.filter(
        StockBatch.quantity > 0, StockBatch.expiry_date.isnot(None)
    ).all():
        risk = batch_risk(b, velocity.get(b.product_id))
        if risk["risk_score"] >= high_threshold:
            _broadcast(
                "High spoilage risk",
                f"Batch {b.batch_code or b.id} risk score {risk['risk_score']} ({risk['risk_level']}).",
                NotificationType.HIGH_RISK.value, severity="WARNING", product_id=b.product_id,
            )
            count += 1
    return count
