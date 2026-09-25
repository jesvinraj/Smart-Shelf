"""Notification query helpers (Module 13 - Alerts & Notifications)."""
from data.models import Notification


def unread_for(user_id: int) -> int:
    return Notification.query.filter(
        Notification.user_id == user_id, Notification.is_read == 0
    ).count()


def list_for_user(user_id: int, limit: int = 100) -> list:
    return (
        Notification.query.filter(
            (Notification.user_id == user_id) | (Notification.user_id.is_(None))
        )
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
