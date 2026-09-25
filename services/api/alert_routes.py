"""Module 13 - Alert & Notification Management API."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from core.decorators import at_least
from data.database import db
from data.models import Notification, Role, StockBatch
from services.alert_service import alert_expiry, alert_high_risk, alert_low_stock
from services.expiry_service import classify_batch, scan_expiry
from services.notification_service import list_for_user, unread_for

bp = Blueprint("alerts", __name__, url_prefix="/api")


@bp.post("/alerts/scan")
@at_least(Role.MANAGER)
def scan():
    alert_days = int(request.args.get("days", 30))
    return jsonify(scan_expiry(alert_days=alert_days, notify=True))


@bp.post("/alerts/generate")
@at_least(Role.MANAGER)
def generate():
    alert_days = int(request.args.get("days", 30))
    results = {
        "low_stock": alert_low_stock(),
        "expiry": alert_expiry(alert_days),
        "high_risk": alert_high_risk(),
    }
    return jsonify(results)


@bp.get("/notifications")
@login_required
def notifications():
    return jsonify([
        {"id": n.id, "title": n.title, "message": n.message,
         "type": n.notification_type, "severity": n.severity,
         "is_read": n.is_read,
         "created_at": n.created_at.isoformat() if n.created_at else None}
        for n in list_for_user(current_user.id)
    ])


@bp.get("/notifications/unread-count")
@login_required
def unread_count():
    return jsonify({"count": unread_for(current_user.id)})


@bp.post("/notifications/<int:nid>/read")
@login_required
def mark_read(nid: int):
    n = db.session.get(Notification, nid)
    if n and (n.user_id is None or n.user_id == current_user.id):
        n.is_read = 1
        db.session.commit()
    return jsonify({"ok": True})


@bp.post("/notifications/read-all")
@login_required
def read_all():
    rows = Notification.query.filter(
        (Notification.user_id == current_user.id) & (Notification.is_read == 0)
    ).all()
    for n in rows:
        n.is_read = 1
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/expiry/scan")
@login_required
def expiry_scan():
    alert_days = int(request.args.get("days", 30))
    return jsonify(scan_expiry(alert_days=alert_days, notify=False))


@bp.get("/expiry/alerts")
@login_required
def expiry_alerts():
    alert_days = int(request.args.get("days", 30))
    out = []
    for b in StockBatch.query.filter(StockBatch.quantity > 0).all():
        status = classify_batch(b, alert_days)
        if status.value != "OK":
            out.append({
                "batch_id": b.id, "product_id": b.product_id,
                "batch_code": b.batch_code, "quantity": b.quantity,
                "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
                "status": status.value,
            })
    return jsonify(out)
