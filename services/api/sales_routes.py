"""Modules 7 & 8 - Sales & Transaction Management API.
Records a sale, deducts inventory FEFO-first, and tracks the exact batch sold.
"""
import secrets
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from core.decorators import at_least
from data.database import db
from data.models import (
    Customer,
    Payment,
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    Role,
    Sale,
    SaleItem,
)
from data.models.enums import PaymentMethod
from services.audit_service import log_action
from services.stock_service import add_stock, deduct_stock

bp = Blueprint("sales", __name__, url_prefix="/api")


@bp.get("/sales")
@login_required
def list_sales():
    rows = Sale.query.order_by(Sale.sale_date.desc()).limit(300).all()
    return jsonify([_sale(s) for s in rows])


@bp.get("/sales/<int:sale_id>")
@login_required
def get_sale(sale_id: int):
    s = db.session.get(Sale, sale_id)
    if not s:
        return jsonify({"error": "Not found"}), 404
    data = _sale(s)
    data["items"] = [
        {"product_id": it.product_id, "batch_id": it.batch_id, "quantity": it.quantity,
         "unit_price": it.unit_price, "line_total": it.line_total}
        for it in s.items
    ]
    return jsonify(data)


@bp.post("/sales")
@at_least(Role.STAFF)
def create_sale():
    data = request.get_json(silent=True) or {}
    items = data.get("items") or []
    if not items:
        return jsonify({"error": "items required"}), 400

    sale = Sale(
        invoice_number=_invoice(),
        customer_id=data.get("customer_id"),
        user_id=current_user.id,
        payment_method=data.get("payment_method", PaymentMethod.CASH.value),
        notes=data.get("notes"),
    )
    db.session.add(sale)
    db.session.flush()

    subtotal = 0.0
    discount_total = 0.0
    for it in items:
        product = db.session.get(Product, it["product_id"])
        if not product:
            return jsonify({"error": f"product {it['product_id']} not found"}), 400
        qty = int(it["quantity"])
        try:
            allocations = deduct_stock(
                product.id, qty, user_id=current_user.id, reference=sale.invoice_number
            )
        except ValueError as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

        unit_price = float(it.get("unit_price", product.unit_price))
        discount = float(it.get("discount_amount", 0.0))
        for alloc in allocations:
            line_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                batch_id=alloc["batch_id"],
                quantity=alloc["quantity"],
                unit_price=unit_price,
                discount_amount=(discount * alloc["quantity"] / qty) if qty else 0.0,
                line_total=unit_price * alloc["quantity"],
            )
            db.session.add(line_item)
        subtotal += unit_price * qty
        discount_total += discount

    tax_rate = 0.0
    tax = subtotal * tax_rate
    sale.subtotal = subtotal
    sale.discount_amount = discount_total
    sale.tax_amount = tax
    sale.total_amount = subtotal - discount_total + tax
    db.session.add(
        Payment(sale_id=sale.id, method=sale.payment_method, amount=sale.total_amount)
    )
    db.session.commit()
    log_action("SALE", "SALE", sale.id, f"invoice {sale.invoice_number}", current_user.id)
    return jsonify(_sale(sale)), 201


@bp.get("/customers")
@login_required
def customers():
    return jsonify([{"id": c.id, "name": c.name, "phone": c.phone}
                    for c in Customer.query.all()])


@bp.post("/customers")
@at_least(Role.STAFF)
def create_customer():
    data = request.get_json(silent=True) or {}
    c = Customer(name=data["name"], phone=data.get("phone"),
                 email=data.get("email"), address=data.get("address"))
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id}), 201


@bp.get("/purchases")
@login_required
def purchases():
    rows = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    return jsonify([
        {"id": p.id, "po_number": p.po_number, "supplier_id": p.supplier_id,
         "status": p.status, "total_amount": p.total_amount,
         "order_date": p.order_date.isoformat() if p.order_date else None}
        for p in rows
    ])


@bp.post("/purchases")
@at_least(Role.MANAGER)
def create_purchase():
    data = request.get_json(silent=True) or {}
    po = PurchaseOrder(
        po_number=f"PO-{secrets.token_hex(4).upper()}",
        supplier_id=data["supplier_id"],
        expected_date=datetime.fromisoformat(data["expected_date"]) if data.get("expected_date") else None,
        created_by=current_user.id,
        status="ORDERED",
    )
    db.session.add(po)
    db.session.flush()
    total = 0.0
    for it in data.get("items") or []:
        item = PurchaseOrderItem(
            purchase_order_id=po.id, product_id=it["product_id"],
            quantity=it["quantity"], unit_cost=it.get("unit_cost", 0.0),
            batch_code=it.get("batch_code"), expiry_date=datetime.fromisoformat(it["expiry_date"]) if it.get("expiry_date") else None,
        )
        db.session.add(item)
        total += item.quantity * item.unit_cost
    po.total_amount = total
    db.session.commit()
    return jsonify({"id": po.id, "po_number": po.po_number}), 201


@bp.post("/purchases/<int:po_id>/receive")
@at_least(Role.MANAGER)
def receive_purchase(po_id: int):
    po = db.session.get(PurchaseOrder, po_id)
    if not po:
        return jsonify({"error": "Not found"}), 404
    for item in po.items:
        qty = item.quantity - item.received_quantity
        if qty <= 0:
            continue
        add_stock(
            product_id=item.product_id, quantity=qty,
            supplier_id=po.supplier_id, cost_price=item.unit_cost,
            batch_code=item.batch_code, expiry_date=item.expiry_date,
            user_id=current_user.id, reference=po.po_number,
        )
        item.received_quantity = item.quantity
    po.status = "RECEIVED"
    db.session.commit()
    return jsonify({"ok": True})


def _sale(s: Sale) -> dict:
    return {
        "id": s.id, "invoice_number": s.invoice_number,
        "customer_id": s.customer_id, "user_id": s.user_id,
        "sale_date": s.sale_date.isoformat() if s.sale_date else None,
        "subtotal": s.subtotal, "discount_amount": s.discount_amount,
        "tax_amount": s.tax_amount, "total_amount": s.total_amount,
        "status": s.status, "payment_method": s.payment_method,
    }


def _invoice() -> str:
    return f"INV-{secrets.token_hex(4).upper()}"
