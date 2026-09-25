"""Expiry & Shelf-Life Management service.

Categorizes batches into OK / EXPIRING_SOON / EXPIRED and computes remaining
shelf life in days.
"""
from datetime import datetime, timezone

from data.models import ExpiryStatus, Notification, NotificationType, StockBatch, User
from data.models.enums import Role


def remaining_shelf_life_days(batch: StockBatch, now: datetime | None = None) -> int | None:
    """Whole (rounded) days between today and expiry. None if no expiry."""
    if batch.expiry_date is None:
        return None
    now = now or datetime.now(timezone.utc)
    exp = batch.expiry_date
    if exp.tzinfo is None and now.tzinfo is not None:
        exp = exp.replace(tzinfo=timezone.utc)
    now_cmp = now if exp.tzinfo is not None else (now.replace(tzinfo=None) if now.tzinfo else now)
    delta = exp - now_cmp
    return int(delta.days)


def classify_days(days_left: int | None, alert_days: int) -> ExpiryStatus:
    if days_left is None:
        return ExpiryStatus.OK
    if days_left < 0:
        return ExpiryStatus.EXPIRED
    if days_left <= alert_days:
        return ExpiryStatus.EXPIRING_SOON
    return ExpiryStatus.OK


def classify_batch(batch: StockBatch, alert_days: int) -> ExpiryStatus:
    return classify_days(remaining_shelf_life_days(batch), alert_days)


def scan_expiry(alert_days: int, notify: bool = False) -> dict:
    """Return expired / expiring soon batches. Optionally push notifications."""
    from sqlalchemy import or_
    from data.database import db

    now = datetime.now(timezone.utc)

    def q(cond):
        return (
            StockBatch.query.filter(
                StockBatch.quantity > 0,
                StockBatch.expiry_date.isnot(None),
                cond,
            )
            .order_by(StockBatch.expiry_date.asc())
            .all()
        )

    expired = [b for b in q(StockBatch.expiry_date < now)]
    expiring = [
        b
        for b in q(or_(StockBatch.expiry_date >= now, StockBatch.expiry_date.is_(None)))
        if remaining_shelf_life_days(b) is not None
        and remaining_shelf_life_days(b) <= alert_days
    ]

    if notify and (expired or expiring):
        _notify_staff(expired, expiring)

    return {
        "expired": [b.id for b in expired],
        "expiring_soon": [b.id for b in expiring],
        "expired_count": len(expired),
        "expiring_soon_count": len(expiring),
    }


def _notify_staff(expired, expiring) -> None:
    from data.database import db

    staff = User.query.filter(User.role.in_([Role.ADMIN.value, Role.MANAGER.value])).all()
    if expired:
        db.session.add(
            Notification(
                title="Expired items",
                message=f"{len(expired)} batch(es) have expired and are blocked from sale.",
                notification_type=NotificationType.EXPIRED.value,
                severity="CRITICAL",
            )
        )
    if expiring:
        db.session.add(
            Notification(
                title="Near-expiry alert",
                message=f"{len(expiring)} batch(es) are expiring within the alert window.",
                notification_type=NotificationType.NEAR_EXPIRY.value,
                severity="WARNING",
            )
        )
    db.session.commit()
