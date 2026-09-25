"""Reporting & Administration service.

Generates inventory, sales, expiry, discount, waste and performance reports.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from data.database import db
from data.models import (
    AuditLog,
    Product,
    Promotion,
    Sale,
    SaleItem,
    StockBatch,
    Wastage,
)
from data.models.enums import WastageReason


def sales_report(days: int = 30) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.session.query(
            func.date(Sale.sale_date).label("date"),
            func.count(Sale.id).label("orders"),
            func.coalesce(func.sum(Sale.total_amount), 0.0).label("revenue"),
            func.coalesce(func.sum(Sale.discount_amount), 0.0).label("discounts"),
        )
        .filter(Sale.sale_date >= cutoff)
        .group_by(func.date(Sale.sale_date))
        .order_by(func.date(Sale.sale_date))
        .all()
    )
    return {
        "period_days": days,
        "daily": [
            {"date": str(r.date), "orders": r.orders, "revenue": round(r.revenue, 2),
             "discounts": round(r.discounts, 2)}
            for r in rows
        ],
    }


def inventory_report() -> dict:
    batches = StockBatch.query.all()
    products = {p.id: p for p in Product.query.all()}
    items = []
    for b in batches:
        p = products.get(b.product_id)
        items.append(
            {
                "product": p.name if p else b.product_id,
                "sku": p.sku if p else None,
                "batch": b.batch_code,
                "quantity": b.quantity,
                "expiry": b.expiry_date.isoformat() if b.expiry_date else None,
                "cost_value": round((b.cost_price or 0) * b.quantity, 2),
                "location": b.location.name if b.location else None,
            }
        )
    total_value = sum(i["cost_value"] for i in items)
    return {"total_stock": len(batches), "total_value": round(total_value, 2), "items": items}


def expiry_report() -> dict:
    from services.expiry_service import remaining_shelf_life_days, scan_expiry

    alert_days = 30
    scan = scan_expiry(alert_days=alert_days, notify=False)
    batches = StockBatch.query.order_by(StockBatch.expiry_date.asc()).all()
    return {
        "expired_count": scan["expired_count"],
        "expiring_soon_count": scan["expiring_soon_count"],
        "batches": [
            {"id": b.id, "product_id": b.product_id, "batch_code": b.batch_code,
             "quantity": b.quantity,
             "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
             "days_left": remaining_shelf_life_days(b)}
            for b in batches
        ],
    }


def discount_report() -> dict:
    promotions = Promotion.query.all()
    return {
        "total": len(promotions),
        "active": sum(1 for p in promotions if p.is_active),
        "pending_approval": sum(1 for p in promotions if p.status == "PENDING_APPROVAL"),
        "items": [
            {"id": p.id, "name": p.name, "discount_type": p.discount_type,
             "value": p.value, "status": p.status}
            for p in promotions
        ],
    }


def waste_report(days: int | None = None) -> dict:
    q = Wastage.query
    if days is not None:
        q = q.filter(Wastage.recorded_at >= datetime.now(timezone.utc) - timedelta(days=days))
    total_loss = q.with_entities(func.coalesce(func.sum(Wastage.potential_loss), 0.0)).scalar()
    return {
        "count": q.count(),
        "potential_loss": round(float(total_loss), 2),
        "by_reason": {r.value: q.filter(Wastage.reason == r.value).count() for r in WastageReason},
    }


def performance_report() -> list:
    products = Product.query.all()
    item_counts = dict(
        db.session.query(SaleItem.product_id, func.sum(SaleItem.quantity))
        .group_by(SaleItem.product_id)
        .all()
    )
    return [
        {"product_id": p.id, "name": p.name, "total_sold": int(item_counts.get(p.id, 0)),
         "stock_on_hand": p.total_stock}
        for p in products
    ]


def audit_report(limit: int = 200) -> list:
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {"id": l.id, "user": l.user.full_name if l.user else None, "action": l.action,
         "entity": f"{l.entity_type}:{l.entity_id}", "details": l.details,
         "created_at": l.created_at.isoformat() if l.created_at else None}
        for l in logs
    ]
