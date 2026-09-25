"""Batch Management API (FEFO-aware)."""
from flask import Blueprint, jsonify
from flask_login import login_required

from data.models import StockBatch
from engines.fefo_engine import fefo_order

bp = Blueprint("batches", __name__, url_prefix="/api")


@bp.get("/batches")
@login_required
def batches():
    items = StockBatch.query.order_by(StockBatch.expiry_date.asc().nulls_last()).all()
    return jsonify([
        {"id": b.id, "product_id": b.product_id, "batch_code": b.batch_code,
         "batch_number": b.batch_number, "quantity": b.quantity,
         "manufactured_date": b.manufactured_date.isoformat() if b.manufactured_date else None,
         "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
         "location_id": b.location_id, "supplier_id": b.supplier_id}
        for b in items
    ])


@bp.get("/fefo")
@login_required
def fefo():
    """Batches ordered for FEFO fulfilment with rank/label/days-left per batch."""
    ordered = fefo_order(StockBatch.query.all())
    items = [
        {
            "rank": e["rank"],
            "label": e["label"],
            "days_left": e["days_left"],
            "batch_code": e["batch"].batch_code,
            "product_id": e["batch"].product_id,
            "quantity": e["batch"].quantity,
            "expiry_date": (
                e["batch"].expiry_date.isoformat()
                if e["batch"].expiry_date is not None
                else None
            ),
            "supplier_id": e["batch"].supplier_id,
        }
        for e in ordered
    ]
    return jsonify({"items": items})
