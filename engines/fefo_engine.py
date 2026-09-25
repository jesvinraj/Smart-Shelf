"""FEFO Inventory Engine (pure Python algorithm).

FEFO = First Expired, First Out. Batches with the earliest expiry date are
sold and dispatched first. Expired batches are excluded from sale. This
module is database-agnostic for unit testing and reuse by stock/risk logic.
"""
from datetime import datetime, timezone
from typing import Iterable, Protocol


class FEFOBatch(Protocol):
    id: int
    quantity: int
    expiry_date: datetime | None


def _normalize_dt(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def sort_batches_fefo(batches: Iterable[FEFOBatch], now: datetime | None = None) -> list:
    """Return batches ordered by earliest expiry first (FEFO).

    Rules:
      - Expired batches (expiry_date < now) are excluded.
      - Quantity <= 0 batches are excluded.
      - Batches without an expiry date sort last (sell fresh/ambient last).
    """
    now_dt = _normalize_dt(now) or datetime.now(timezone.utc)
    usable = []
    for b in batches:
        if b.quantity is None or b.quantity <= 0:
            continue
        if b.expiry_date is not None:
            exp = _normalize_dt(b.expiry_date)
            if exp < now_dt:
                continue
        usable.append(b)

    return sorted(
        usable,
        key=lambda b: (
            _normalize_dt(b.expiry_date)
            if b.expiry_date is not None
            else datetime.max.replace(tzinfo=timezone.utc)
        ),
    )


def select_batch_for_sale(
    batches: Iterable[FEFOBatch], quantity: int, now: datetime | None = None
) -> list[dict]:
    """Allocate `quantity` units from the earliest-expiring batches.

    Returns [{"batch_id", "quantity"}]. Raises ValueError if insufficient
    usable (non-expired) stock remains.
    """
    ordered = sort_batches_fefo(batches, now=now)
    remaining = quantity
    allocation: list[dict] = []
    for b in ordered:
        if remaining <= 0:
            break
        take = min(b.quantity, remaining)
        remaining -= take
        allocation.append({"batch_id": b.id, "quantity": take})
    if remaining > 0:
        raise ValueError(
            f"Insufficient usable stock: requested {quantity}, available "
            f"{quantity - remaining}"
        )
    return allocation


def next_batch_to_sell(batches: Iterable[FEFOBatch], now: datetime | None = None):
    """Return the single next batch that should be sold first, or None."""
    ordered = sort_batches_fefo(batches, now=now)
    return ordered[0] if ordered else None


def fefo_order(batches: Iterable[FEFOBatch], now: datetime | None = None) -> list[dict]:
    """Return FEFO-ordered batches annotated with their sell priority.

    Each entry: {batch, rank, label} where label is SELL_FIRST/NEXT/NORMAL.
    """
    now_dt = _normalize_dt(now) or datetime.now(timezone.utc)
    ordered = sort_batches_fefo(batches, now=now_dt)
    result = []
    for idx, b in enumerate(ordered):
        if b.expiry_date is not None:
            exp = _normalize_dt(b.expiry_date)
            days = (exp - now_dt).days
        else:
            days = None

        if idx == 0:
            label = "SELL_FIRST"
        elif days is not None and days <= 5:
            label = "SELL_NEXT"
        else:
            label = "NORMAL"
        result.append({"batch": b, "rank": idx + 1, "label": label, "days_left": days})
    return result
