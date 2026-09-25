"""Modules 10, 11, 12 - Spoilage risk, dynamic pricing & promotion management API."""
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from core.decorators import at_least
from data.database import db
from data.models import Product, PromoStatus, Promotion, Role, StockBatch
from engines.demand_engine import sales_velocity
from engines.pricing_engine import discount_reason, discounted_price, recommended_discount_pct
from engines.risk_engine import batch_risk
from services.audit_service import log_action

bp = Blueprint("pricing", __name__, url_prefix="/api")


def _velocity_map():
    return {
        r["product_id"]: r["velocity_per_day"]
        for r in sales_velocity(days=30).to_dict("records")
    }


@bp.get("/ai/risk")
@login_required
def risk():
    """Spoilage risk score for every in-stock batch."""
    velocity = _velocity_map()
    out = []
    for b in StockBatch.query.filter(StockBatch.quantity > 0).all():
        r = batch_risk(b, velocity.get(b.product_id))
        r["product_id"] = b.product_id
        out.append(r)
    out.sort(key=lambda x: x["risk_score"], reverse=True)
    return jsonify(out)


@bp.get("/ai/risk/<int:batch_id>")
@login_required
def risk_single(batch_id: int):
    b = db.session.get(StockBatch, batch_id)
    if not b:
        return jsonify({"error": "Not found"}), 404
    vel_map = _velocity_map()
    return jsonify(batch_risk(b, vel_map.get(b.product_id)))


@bp.get("/ai/pricing")
@login_required
def pricing():
    """Recommended pricing/discount for all at-risk batches."""
    velocity = _velocity_map()
    out = []
    for b in StockBatch.query.filter(StockBatch.quantity > 0).all():
        r = batch_risk(b, velocity.get(b.product_id))
        price = b.product.unit_price if b.product else 0.0
        disc = recommended_discount_pct(r["risk_score"])
        out.append({
            "batch_id": b.id,
            "product_id": b.product_id,
            "product_name": b.product.name if b.product else None,
            "quantity": b.quantity,
            "risk_score": r["risk_score"],
            "risk_level": r["risk_level"],
            "unit_price": price,
            "recommended_discount_pct": disc,
            "discounted_price": discounted_price(price, disc),
            "reason": discount_reason(r["risk_score"], velocity.get(b.product_id),
                                      r.get("days_to_expiry")),
        })
    out.sort(key=lambda x: x["recommended_discount_pct"], reverse=True)
    return jsonify(out)


# ---- Promotions (Module 12) ----
@bp.get("/promotions")
@login_required
def list_promotions():
    return jsonify([_promo(p) for p in Promotion.query.all()])


@bp.post("/promotions")
@at_least(Role.MANAGER)
def create_promotion():
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("discount_type") or "value" not in data:
        return jsonify({"error": "name, discount_type, value required"}), 400
    promo = Promotion(
        name=data["name"], description=data.get("description"),
        discount_type=data["discount_type"], value=data["value"],
        product_id=data.get("product_id"), category_id=data.get("category_id"),
        min_quantity=data.get("min_quantity"),
        start_date=_parse_dt(data.get("start_date")),
        end_date=_parse_dt(data.get("end_date")),
        status=PromoStatus.DRAFT.value,
        created_by=current_user.id,
        suggested_discount=data.get("suggested_discount"),
    )
    db.session.add(promo)
    db.session.commit()
    log_action("CREATE", "PROMOTION", promo.id)
    return jsonify(_promo(promo)), 201


@bp.put("/promotions/<int:pid>")
@at_least(Role.MANAGER)
def update_promotion(pid: int):
    promo = db.session.get(Promotion, pid)
    if not promo:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    for field in ("name", "description", "discount_type", "value", "product_id",
                  "category_id", "min_quantity", "suggested_discount"):
        if field in data:
            setattr(promo, field, data[field])
    if data.get("start_date"):
        promo.start_date = _parse_dt(data["start_date"])
    if data.get("end_date"):
        promo.end_date = _parse_dt(data["end_date"])
    db.session.commit()
    log_action("UPDATE", "PROMOTION", pid)
    return jsonify(_promo(promo))


@bp.post("/promotions/<int:pid>/submit")
@at_least(Role.MANAGER)
def submit_promotion(pid: int):
    promo = db.session.get(Promotion, pid)
    if not promo:
        return jsonify({"error": "Not found"}), 404
    promo.status = PromoStatus.PENDING_APPROVAL.value
    db.session.commit()
    log_action("SUBMIT", "PROMOTION", pid)
    return jsonify(_promo(promo))


@bp.post("/promotions/<int:pid>/approve")
@at_least(Role.ADMIN)
def approve_promotion(pid: int):
    promo = db.session.get(Promotion, pid)
    if not promo:
        return jsonify({"error": "Not found"}), 404
    promo.status = PromoStatus.ACTIVE.value
    promo.approved_by = current_user.id
    promo.approved_at = datetime.now(timezone.utc)
    db.session.commit()
    log_action("APPROVE", "PROMOTION", pid)
    return jsonify(_promo(promo))


@bp.post("/promotions/<int:pid>/reject")
@at_least(Role.ADMIN)
def reject_promotion(pid: int):
    promo = db.session.get(Promotion, pid)
    if not promo:
        return jsonify({"error": "Not found"}), 404
    promo.status = PromoStatus.REJECTED.value
    db.session.commit()
    log_action("REJECT", "PROMOTION", pid)
    return jsonify(_promo(promo))


@bp.post("/promotions/<int:pid>/toggle")
@at_least(Role.MANAGER)
def toggle_promotion(pid: int):
    promo = db.session.get(Promotion, pid)
    if not promo:
        return jsonify({"error": "Not found"}), 404
    promo.status = (
        PromoStatus.ACTIVE.value if promo.status != PromoStatus.ACTIVE.value
        else PromoStatus.INACTIVE.value
    )
    db.session.commit()
    return jsonify(_promo(promo))


def _parse_dt(value):
    return datetime.fromisoformat(value) if value else None


def _promo(p: Promotion) -> dict:
    return {
        "id": p.id, "name": p.name, "description": p.description,
        "discount_type": p.discount_type, "value": p.value,
        "suggested_discount": p.suggested_discount,
        "product_id": p.product_id, "category_id": p.category_id,
        "min_quantity": p.min_quantity,
        "start_date": p.start_date.isoformat() if p.start_date else None,
        "end_date": p.end_date.isoformat() if p.end_date else None,
        "status": p.status, "is_active": p.is_active,
    }
