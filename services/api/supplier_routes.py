"""Module 3 - Supplier Management API."""
from flask import Blueprint, jsonify, request
from flask_login import login_required

from core.decorators import at_least
from data.database import db
from data.models import Role, StockBatch, Supplier
from services.audit_service import log_action

bp = Blueprint("suppliers", __name__, url_prefix="/api")


@bp.get("/suppliers")
@login_required
def list_suppliers():
    return jsonify([_sup(s) for s in Supplier.query.all()])


@bp.get("/suppliers/<int:sid>")
@login_required
def get_supplier(sid: int):
    s = db.session.get(Supplier, sid)
    if not s:
        return jsonify({"error": "Not found"}), 404
    return jsonify(_sup(s))


@bp.post("/suppliers")
@at_least(Role.MANAGER)
def create_supplier():
    data = request.get_json(silent=True) or {}
    if not data.get("name"):
        return jsonify({"error": "name required"}), 400
    s = Supplier(
        name=data["name"], contact_person=data.get("contact_person"),
        email=data.get("email"), phone=data.get("phone"), address=data.get("address"),
    )
    db.session.add(s)
    db.session.commit()
    log_action("CREATE", "SUPPLIER", s.id)
    return jsonify(_sup(s)), 201


@bp.put("/suppliers/<int:sid>")
@at_least(Role.MANAGER)
def update_supplier(sid: int):
    s = db.session.get(Supplier, sid)
    if not s:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    for field in ("name", "contact_person", "email", "phone", "address", "is_active"):
        if field in data:
            setattr(s, field, data[field])
    db.session.commit()
    log_action("UPDATE", "SUPPLIER", s.id)
    return jsonify(_sup(s))


@bp.delete("/suppliers/<int:sid>")
@at_least(Role.MANAGER)
def delete_supplier(sid: int):
    s = db.session.get(Supplier, sid)
    if not s:
        return jsonify({"error": "Not found"}), 404
    s.is_active = False
    db.session.commit()
    log_action("DELETE", "SUPPLIER", s.id)
    return jsonify({"ok": True})


@bp.get("/suppliers/<int:sid>/batches")
@login_required
def supplier_batches(sid: int):
    batches = StockBatch.query.filter(StockBatch.supplier_id == sid).all()
    return jsonify([
        {"id": b.id, "product_id": b.product_id, "batch_code": b.batch_code,
         "quantity": b.quantity, "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None}
        for b in batches
    ])


def _sup(s: Supplier) -> dict:
    return {"id": s.id, "name": s.name, "contact_person": s.contact_person,
            "email": s.email, "phone": s.phone, "address": s.address,
            "is_active": s.is_active, "created_at": s.created_at.isoformat() if s.created_at else None}
