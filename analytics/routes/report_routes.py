"""Module 16 - Reporting & Administration API."""
from flask import Blueprint, jsonify, request
from flask_login import login_required

from analytics.report_service import (
    audit_report,
    discount_report,
    expiry_report,
    inventory_report,
    performance_report,
    sales_report,
    waste_report,
)
from core.decorators import at_least
from data.database import check_database
from data.models import Role

bp = Blueprint("reports", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    """Liveness + DB connectivity probe (no auth required)."""
    from flask import current_app
    info = check_database(current_app)
    return jsonify({"status": "ok" if info["ok"] else "degraded", **info})


@bp.get("/reports/sales")
@login_required
def sales():
    return jsonify(sales_report(days=int(request.args.get("days", 30))))


@bp.get("/reports/inventory")
@login_required
def inventory():
    return jsonify(inventory_report())


@bp.get("/reports/expiry")
@login_required
def expiry():
    return jsonify(expiry_report())


@bp.get("/reports/discounts")
@login_required
def discounts():
    return jsonify(discount_report())


@bp.get("/reports/waste")
@login_required
def waste():
    days = request.args.get("days")
    return jsonify(waste_report(days=int(days) if days else None))


@bp.get("/reports/performance")
@login_required
def performance():
    return jsonify(performance_report())


@bp.get("/reports/audit")
@at_least(Role.MANAGER)
def audit():
    return jsonify(audit_report())
