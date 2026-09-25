"""Modules 4 & 5 - Inventory & Batch Management API."""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from core.decorators import at_least, roles_required
from data.database import db
from data.models import InventoryMovement, Location, LocationTransfer, Role, StockBatch
from services.audit_service import log_action
from services.expiry_service import classify_batch
from services.stock_service import add_stock, adjust_stock, transfer_stock

bp = Blueprint("inventory", __name__, url_prefix="/api")


@bp.get("/inventory")
@login_required
def inventory():
    alert_days = 30
    items = []
    for b in StockBatch.query.all():
        exp = classify_batch(b, alert_days)
        items.append(
            {
                "id": b.id, "product_id": b.product_id, "batch_code": b.batch_code,
                "quantity": b.quantity, "location_id": b.location_id,
                "supplier_id": b.supplier_id,
                "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
                "status": exp.value,
            }
        )
    return jsonify({"items": items, "total": len(items)})


@bp.post("/inventory/receive")
@at_least(Role.MANAGER)
def receive():
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    if not product_id or not quantity:
        return jsonify({"error": "product_id, quantity required"}), 400
    expiry = None
    if data.get("expiry_date"):
        expiry = datetime.fromisoformat(data["expiry_date"])
    manuf = None
    if data.get("manufactured_date"):
        manuf = datetime.fromisoformat(data["manufactured_date"])
    batch = add_stock(
        product_id=product_id, quantity=int(quantity),
        location_id=data.get("location_id"), supplier_id=data.get("supplier_id"),
        cost_price=data.get("cost_price"), batch_code=data.get("batch_code") or data.get("batch_number"),
        manufactured_date=manuf, expiry_date=expiry,
        user_id=current_user.id, reference=data.get("reference"),
        notes=data.get("notes"),
    )
    log_action("STOCK_IN", "STOCK_BATCH", batch.id)
    return jsonify({"batch_id": batch.id, "quantity": batch.quantity}), 201


@bp.post("/inventory/adjust")
@at_least(Role.MANAGER)
def adjust():
    data = request.get_json(silent=True) or {}
    result = adjust_stock(
        product_id=data.get("product_id"),
        new_quantity=int(data.get("new_quantity", 0)),
        location_id=data.get("location_id"),
        user_id=current_user.id,
        notes=data.get("notes"),
    )
    log_action("ADJUST", "PRODUCT", data.get("product_id"))
    return jsonify({"delta": result})


@bp.get("/inventory/movements")
@login_required
def movements():
    q = request.args
    query = InventoryMovement.query
    if q.get("product_id"):
        query = query.filter(InventoryMovement.product_id == int(q["product_id"]))
    if q.get("days"):
        cutoff = datetime.now(timezone.utc) - timedelta(days=int(q["days"]))
        query = query.filter(InventoryMovement.movement_date >= cutoff)
    rows = query.order_by(InventoryMovement.movement_date.desc()).limit(500).all()
    return jsonify([
        {"id": m.id, "product_id": m.product_id, "type": m.movement_type,
         "quantity": m.quantity, "reference": m.reference,
         "date": m.movement_date.isoformat() if m.movement_date else None}
        for m in rows
    ])


@bp.get("/locations")
@login_required
def list_locations():
    return jsonify([{"id": l.id, "code": l.code, "name": l.name, "zone": l.zone}
                    for l in Location.query.all()])


@bp.post("/locations")
@at_least(Role.MANAGER)
def create_location():
    data = request.get_json(silent=True) or {}
    if not data.get("code") or not data.get("name"):
        return jsonify({"error": "code, name required"}), 400
    loc = Location(code=data["code"], name=data["name"], zone=data.get("zone"))
    db.session.add(loc)
    db.session.commit()
    return jsonify({"id": loc.id}), 201


@bp.post("/locations/transfer")
@roles_required(Role.STAFF, Role.MANAGER, Role.ADMIN)
def transfer():
    data = request.get_json(silent=True) or {}
    try:
        transfer_stock(
            product_id=data["product_id"],
            from_location_id=data["from_location_id"],
            to_location_id=data["to_location_id"],
            quantity=int(data["quantity"]),
            user_id=current_user.id,
            notes=data.get("notes"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    log_action("TRANSFER", "PRODUCT", data["product_id"])
    return jsonify({"ok": True})


@bp.get("/locations/transfers")
@login_required
def transfers():
    rows = LocationTransfer.query.order_by(LocationTransfer.transferred_at.desc()).all()
    return jsonify([
        {"id": t.id, "product_id": t.product_id, "from": t.from_location_id,
         "to": t.to_location_id, "quantity": t.quantity,
         "date": t.transferred_at.isoformat() if t.transferred_at else None}
        for t in rows
    ])
