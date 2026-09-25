"""Stock management: receive/inbound, FEFO deduction, adjustment, transfer.

Used by Inventory, Batch and Sales flows. Deduction is FEFO-first and
expired batches are never sold.
"""
from datetime import datetime, timezone

from sqlalchemy import func

from data.database import db
from data.models import InventoryMovement, Location, MovementType, StockBatch
from engines.fefo_engine import select_batch_for_sale, sort_batches_fefo


def add_stock(
    product_id: int,
    quantity: int,
    location_id: int | None = None,
    supplier_id: int | None = None,
    cost_price: float | None = None,
    batch_code: str | None = None,
    batch_number: str | None = None,
    manufactured_date: datetime | None = None,
    expiry_date: datetime | None = None,
    user_id: int | None = None,
    reference: str | None = None,
    notes: str | None = None,
) -> StockBatch:
    """Register inbound stock and return the created batch."""
    batch = StockBatch(
        product_id=product_id,
        location_id=location_id,
        supplier_id=supplier_id,
        quantity=quantity,
        cost_price=cost_price,
        batch_code=batch_code,
        batch_number=batch_number or batch_code,
        manufactured_date=manufactured_date,
        expiry_date=expiry_date,
    )
    db.session.add(batch)
    db.session.flush()
    db.session.add(
        InventoryMovement(
            product_id=product_id,
            location_id=location_id,
            batch_id=batch.id,
            movement_type=MovementType.IN.value,
            quantity=quantity,
            reference=reference,
            notes=notes,
            created_by=user_id,
        )
    )
    db.session.commit()
    return batch


def _fefo_batches(product_id: int, location_id: int | None = None, now=None):
    """Batches ordered by earliest expiry (FEFO), excluding already-expired."""
    now = now or datetime.now(timezone.utc)
    q = StockBatch.query.filter(
        StockBatch.product_id == product_id,
        StockBatch.quantity > 0,
        (StockBatch.expiry_date.is_(None)) | (StockBatch.expiry_date >= now),
    )
    if location_id is not None:
        q = q.filter(StockBatch.location_id == location_id)
    return sort_batches_fefo(q.with_for_update().all(), now=now)


def deduct_stock(
    product_id: int,
    quantity: int,
    location_id: int | None = None,
    user_id: int | None = None,
    reference: str | None = None,
    notes: str | None = None,
) -> list[dict]:
    """Consume stock FEFO-first with atomic, guarded decrements.

    Returns [{"batch_id", "quantity"}].
    """
    batches = _fefo_batches(product_id, location_id)
    allocations = select_batch_for_sale(batches, quantity)
    for alloc in allocations:
        batch = next(b for b in batches if b.id == alloc["batch_id"])
        applied = (
            StockBatch.query.filter_by(id=batch.id)
            .filter(StockBatch.quantity >= alloc["quantity"])
            .update(
                {"quantity": StockBatch.quantity - alloc["quantity"]},
                synchronize_session=False,
            )
        )
        if not applied:
            db.session.rollback()
            raise ValueError(
                f"Insufficient usable stock after concurrent drawdown: "
                f"requested {quantity}"
            )
        db.session.expire(batch)
        db.session.add(
            InventoryMovement(
                product_id=product_id,
                location_id=batch.location_id,
                batch_id=batch.id,
                movement_type=MovementType.OUT.value,
                quantity=alloc["quantity"],
                reference=reference,
                notes=notes,
                created_by=user_id,
            )
        )
    db.session.commit()
    return allocations


def transfer_stock(
    product_id: int,
    from_location_id: int,
    to_location_id: int,
    quantity: int,
    user_id: int | None = None,
    notes: str | None = None,
):
    """Move stock between locations (FEFO-out from source)."""
    from data.models import LocationTransfer

    allocations = deduct_stock(
        product_id=product_id,
        quantity=quantity,
        location_id=from_location_id,
        user_id=user_id,
        reference="TRANSFER",
        notes=notes,
    )
    for alloc in allocations:
        batch = db.session.get(StockBatch, alloc["batch_id"])
        dest = StockBatch(
            product_id=product_id,
            location_id=to_location_id,
            supplier_id=batch.supplier_id,
            quantity=alloc["quantity"],
            cost_price=batch.cost_price,
            batch_code=batch.batch_code,
            manufactured_date=batch.manufactured_date,
            expiry_date=batch.expiry_date,
        )
        db.session.add(dest)
        db.session.flush()
        db.session.add(
            InventoryMovement(
                product_id=product_id,
                location_id=to_location_id,
                batch_id=dest.id,
                movement_type=MovementType.TRANSFER.value,
                quantity=alloc["quantity"],
                reference="TRANSFER",
                notes=notes,
                created_by=user_id,
            )
        )
    db.session.add(
        LocationTransfer(
            product_id=product_id,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            quantity=quantity,
            transferred_by=user_id,
            notes=notes,
        )
    )
    db.session.commit()
    return allocations


def adjust_stock(
    product_id: int,
    new_quantity: int,
    location_id: int | None = None,
    user_id: int | None = None,
    notes: str | None = None,
):
    """Set absolute quantity at a location by adjusting the delta."""
    target_id = location_id or db.session.query(Location.id).first()[0]
    current = (
        db.session.query(func.coalesce(func.sum(StockBatch.quantity), 0))
        .filter(StockBatch.product_id == product_id, StockBatch.location_id == target_id)
        .scalar()
    )
    delta = new_quantity - current
    if delta == 0:
        return 0
    if delta > 0:
        add_stock(product_id, delta, location_id=target_id, user_id=user_id, notes=notes)
    else:
        deduct_stock(product_id, abs(delta), location_id=target_id, user_id=user_id, notes=notes)
    return delta
