"""Module 2 - Product Management API (also brands & categories)."""
from flask import Blueprint, jsonify, request
from flask_login import login_required

from core.decorators import at_least
from data.database import db
from data.models import Brand, Category, Product, Role, StockBatch
from services.audit_service import log_action

bp = Blueprint("products", __name__, url_prefix="/api")


@bp.get("/categories")
@login_required
def list_categories():
    return jsonify(
        [{"id": c.id, "name": c.name, "parent_id": c.parent_id,
          "is_active": c.is_active} for c in Category.query.all()]
    )


@bp.post("/categories")
@at_least(Role.MANAGER)
def create_category():
    data = request.get_json(silent=True) or {}
    cat = Category(name=data["name"], parent_id=data.get("parent_id"),
                   description=data.get("description"))
    db.session.add(cat)
    db.session.commit()
    log_action("CREATE", "CATEGORY", cat.id)
    return jsonify({"id": cat.id}), 201


@bp.get("/brands")
@login_required
def list_brands():
    return jsonify([{"id": b.id, "name": b.name, "is_active": b.is_active}
                    for b in Brand.query.all()])


@bp.post("/brands")
@at_least(Role.MANAGER)
def create_brand():
    data = request.get_json(silent=True) or {}
    if Brand.query.filter(Brand.name == data["name"]).first():
        return jsonify({"error": "Brand exists"}), 409
    b = Brand(name=data["name"], description=data.get("description"))
    db.session.add(b)
    db.session.commit()
    return jsonify({"id": b.id}), 201


@bp.get("/products")
@login_required
def list_products():
    q = request.args
    query = Product.query
    if q.get("q"):
        query = query.filter(Product.name.ilike(f"%{q['q']}%"))
    if q.get("category_id"):
        query = query.filter(Product.category_id == int(q["category_id"]))
    if q.get("active_only") in ("1", "true"):
        query = query.filter(Product.is_active.is_(True))
    items = query.all()
    return jsonify({"items": [_prod(p) for p in items], "total": len(items)})


@bp.get("/products/low-stock")
@login_required
def low_stock():
    items = [p for p in Product.query.all() if p.total_stock <= p.reorder_level]
    return jsonify([_prod(p) for p in items])


@bp.get("/products/out-of-stock")
@login_required
def out_of_stock():
    items = [p for p in Product.query.all() if p.total_stock <= 0]
    return jsonify([_prod(p) for p in items])


@bp.get("/products/<int:pid>")
@login_required
def get_product(pid: int):
    p = db.session.get(Product, pid)
    if not p:
        return jsonify({"error": "Not found"}), 404
    return jsonify(_prod(p))


@bp.get("/products/lookup/<string:barcode>")
@login_required
def lookup_product_by_barcode(barcode: str):
    code = barcode.strip()
    p = Product.query.filter(Product.barcode == code).first()
    if not p:
        return jsonify({"error": "Product not found", "barcode": code}), 404
    data = _prod(p)
    data["category"] = p.category.name if p.category else None
    data["brand"] = p.brand.name if p.brand else None
    return jsonify(data)


@bp.post("/products")
@at_least(Role.MANAGER)
def create_product():
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("sku"):
        return jsonify({"error": "name, sku required"}), 400
    if Product.query.filter(Product.sku == data["sku"]).first():
        return jsonify({"error": "SKU exists"}), 409
    if data.get("barcode") and Product.query.filter(Product.barcode == data["barcode"]).first():
        return jsonify({"error": "Barcode exists"}), 409
    p = Product(**{k: v for k, v in data.items() if k not in ("category_id", "brand_id")})
    p.category_id = data.get("category_id")
    p.brand_id = data.get("brand_id")
    db.session.add(p)
    db.session.commit()
    log_action("CREATE", "PRODUCT", p.id)
    return jsonify(_prod(p)), 201


@bp.put("/products/<int:pid>")
@at_least(Role.MANAGER)
def update_product(pid: int):
    p = db.session.get(Product, pid)
    if not p:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    for field in ("name", "sku", "barcode", "description", "unit", "unit_price",
                  "cost_price", "tax_rate", "shelf_life_days", "storage_condition",
                  "reorder_level", "lead_time_days", "image_url", "is_perishable",
                  "is_active", "category_id", "brand_id"):
        if field in data:
            setattr(p, field, data[field])
    db.session.commit()
    log_action("UPDATE", "PRODUCT", p.id)
    return jsonify(_prod(p))


@bp.delete("/products/<int:pid>")
@at_least(Role.MANAGER)
def delete_product(pid: int):
    p = db.session.get(Product, pid)
    if not p:
        return jsonify({"error": "Not found"}), 404
    p.is_active = False
    db.session.commit()
    log_action("DELETE", "PRODUCT", pid)
    return jsonify({"ok": True})


@bp.get("/products/<int:pid>/batches")
@login_required
def product_batches(pid: int):
    batches = StockBatch.query.filter(StockBatch.product_id == pid).all()
    return jsonify([
        {"id": b.id, "batch_code": b.batch_code, "quantity": b.quantity,
         "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
         "location_id": b.location_id}
        for b in batches
    ])


def _prod(p: Product) -> dict:
    return {
        "id": p.id, "name": p.name, "sku": p.sku, "barcode": p.barcode,
        "description": p.description, "category_id": p.category_id,
        "brand_id": p.brand_id, "unit": p.unit, "unit_price": p.unit_price,
        "cost_price": p.cost_price, "tax_rate": p.tax_rate,
        "shelf_life_days": p.shelf_life_days, "storage_condition": p.storage_condition,
        "reorder_level": p.reorder_level, "lead_time_days": p.lead_time_days,
        "is_perishable": p.is_perishable, "is_active": p.is_active,
        "total_stock": p.total_stock,
    }
