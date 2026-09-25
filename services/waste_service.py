"""Waste & Revenue Recovery Management service.

Records expired/wasted product, computes potential loss, recovered revenue
and savings realized through pre-expiry discounting.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from data.database import db
from data.models import InventoryMovement, Product, StockBatch, Wastage
from data.models.enums import MovementType


def record_wastage(
    product_id: int,
    quantity: int,
    reason: str,
    batch_id: int | None = None,
    location_id: int | None = None,
    user_id: int | None = None,
    notes: str | None = None,
) -> Wastage:
    product = db.session.get(Product, product_id)
    unit_cost = 0.0
    if batch_id:
        batch = db.session.get(StockBatch, batch_id)
        if batch:
            unit_cost = batch.cost_price or (product.cost_price if product else 0.0)
            batch.quantity = max(batch.quantity - quantity, 0)
            db.session.flush()
    elif product:
        unit_cost = product.cost_price or 0.0

    potential_loss = round(unit_cost * quantity, 2)
    wastage = Wastage(
        product_id=product_id,
        batch_id=batch_id,
        location_id=location_id,
        quantity=quantity,
        reason=reason,
        unit_cost=unit_cost,
        potential_loss=potential_loss,
        recorded_by=user_id,
        notes=notes,
    )
    db.session.add(wastage)
    db.session.flush()
    db.session.add(
        InventoryMovement(
            product_id=product_id,
            location_id=location_id,
            batch_id=batch_id,
            movement_type=MovementType.WASTAGE.value,
            quantity=-quantity,
            reference=f"WASTE-{wastage.id}",
            notes=notes,
            created_by=user_id,
        )
    )
    db.session.commit()
    return wastage


def apply_recovery(wastage: Wastage, discounted_sale_revenue: float, savings_from_discount: float) -> Wastage:
    """After a discounted sale avoids waste, attach recovery + savings figures."""
    wastage.recovered_revenue = round(discounted_sale_revenue, 2)
    wastage.savings = round(savings_from_discount, 2)
    db.session.commit()
    return wastage


def recovery_summary(days: int | None = None) -> dict:
    """Aggregate potential loss, recovered revenue and savings."""
    q = Wastage.query
    if days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        q = q.filter(Wastage.recorded_at >= cutoff)
    total_loss = q.with_entities(func.coalesce(func.sum(Wastage.potential_loss), 0.0)).scalar()
    total_recovered = q.with_entities(func.coalesce(func.sum(Wastage.recovered_revenue), 0.0)).scalar()
    total_savings = q.with_entities(func.coalesce(func.sum(Wastage.savings), 0.0)).scalar()
    return {
        "waste_count": q.count(),
        "potential_loss": round(float(total_loss), 2),
        "recovered_revenue": round(float(total_recovered), 2),
        "savings_from_discount": round(float(total_savings), 2),
        "net_waste_cost": round(float(total_loss) - float(total_recovered) - float(total_savings), 2),
    }
