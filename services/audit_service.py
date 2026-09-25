"""Audit trail helper used across mutation endpoints."""
from datetime import datetime, timezone

from data.database import db
from data.models import AuditLog


def log_action(
    action: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    details: str | None = None,
    user_id: int | None = None,
    username: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(entry)
    db.session.commit()
    return entry
