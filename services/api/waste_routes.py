"""Module 15 - Waste & Revenue Recovery Management API."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from core.decorators import at_least
from data.models import Role, Wastage
from services.audit_service import log_action
from services.waste_service import record_wastage, recovery_summary

bp = Blueprint("wastage", __name__, url_prefix="/api")


@bp.get("/wastage")
@login_required
def list_wastage():
    rows = Wastage.query.order_by(Wastage.recorded_at.desc()).limit(200).all()
    return jsonify([_w(w) for w in rows])


@bp.post("/wastage")
@at_least(Role.STAFF)
def create_wastage():
    data = request.get_json(silent=True) or {}
    try:
        w = record_wastage(
            product_id=data["product_id"],
            quantity=int(data["quantity"]),
            reason=data.get("reason", "EXPIRED"),
            batch_id=data.get("batch_id"),
            location_id=data.get("location_id"),
            user_id=current_user.id,
            notes=data.get("notes"),
        )
    except KeyError:
        return jsonify({"error": "product_id, quantity required"}), 400
    log_action("WASTAGE", "WASTAGE", w.id)
    return jsonify(_w(w)), 201


@bp.get("/wastage/summary")
@login_required
def summary():
    days = request.args.get("days")
    return jsonify(recovery_summary(days=int(days) if days else None))


def _w(w: Wastage) -> dict:
    return {
        "id": w.id, "product_id": w.product_id, "batch_id": w.batch_id,
        "quantity": w.quantity, "reason": w.reason, "unit_cost": w.unit_cost,
        "potential_loss": w.potential_loss, "recovered_revenue": w.recovered_revenue,
        "savings": w.savings,
        "recorded_at": w.recorded_at.isoformat() if w.recorded_at else None,
        "notes": w.notes,
    }
