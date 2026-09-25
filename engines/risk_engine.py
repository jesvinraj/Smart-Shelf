"""Spoilage Risk Prediction Engine (pure Python).

Computes a spoilage risk score (0-100) per batch using:
  - days to expiry (the nearer, the riskier)       -> 0-45 points
  - product category perishability + storage         -> 0-35 points
  - sales velocity (slow movers are riskier)         -> 0-20 points

Higher score = higher risk of spoilage/waste.
"""
from datetime import datetime

from data.models import ExpiryStatus, StockBatch
from services.expiry_service import remaining_shelf_life_days

STORAGE_MULTIPLIER = {
    "AMBIENT": 1.0,
    "CHILLED": 1.3,
    "FROZEN": 1.1,
}

MAX_SCORE = 100.0


def _category_perishability(product) -> float:
    if product is None:
        return 0.5
    if product.is_perishable:
        return 0.8
    cat = product.category
    if cat and any(k in cat.name.upper() for k in ("DAIRY", "MEAT", "PRODUCE", "FRESH")):
        return 0.85
    return 0.4


def breakdown(
    expiry_days: int | None,
    perishability: float,
    storage_condition: str,
    velocity_per_day: float | None,
) -> dict:
    """Return the four sub-scores that compose the total risk score.

    This is used by the Risk Analysis screen to explain the score.
    """
    # 1) Time-to-expiry component (max 45).
    if expiry_days is None:
        time_component = 5.0
    elif expiry_days < 0:
        time_component = 45.0
    elif expiry_days <= 7:
        time_component = 45.0
    elif expiry_days <= 30:
        time_component = 45.0 * (1 - (expiry_days - 7) / 23)
    else:
        time_component = max(0.0, 45.0 * (1 - (expiry_days - 30) / 90))
        if expiry_days > 120:
            time_component = min(time_component, 4.0)

    # 2) Perishability + storage component (max 35).
    storage = STORAGE_MULTIPLIER.get((storage_condition or "AMBIENT").upper(), 1.0)
    perish_component = min(35.0, perishability * 35.0 * storage)

    # 3) Velocity component (max 20): slow movers riskier.
    if velocity_per_day is None or velocity_per_day >= 3:
        velocity_component = 0.0
    else:
        velocity_component = min(20.0, 20.0 * (1 - velocity_per_day / 3))

    return {
        "expiry": round(time_component, 1),
        "category": round(perish_component, 1),
        "storage": round(perish_component, 1),
        "velocity": round(velocity_component, 1),
        "max_expiry": 45,
        "max_category": 20,
        "max_storage": 15,
        "max_velocity": 20,
    }


def risk_score(
    expiry_days: int | None,
    perishability: float,
    storage_condition: str,
    velocity_per_day: float | None,
    with_breakdown: bool = False,
):
    """Return the risk score (int), or a dict with breakdown if requested."""
    parts = breakdown(expiry_days, perishability, storage_condition, velocity_per_day)
    total = parts["expiry"] + parts["category"] + parts["velocity"]
    total = round(total)
    if with_breakdown:
        return {"score": total, **parts}
    return total


def risk_level(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def risk_color(score: int) -> str:
    return {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "yellow", "LOW": "green"}[risk_level(score)]


def batch_risk(batch: StockBatch, velocity_per_day: float | None, now=None) -> dict:
    days = remaining_shelf_life_days(batch, now=now)
    product = batch.product
    score = risk_score(
        days,
        _category_perishability(product),
        product.storage_condition if product else "AMBIENT",
        velocity_per_day,
    )
    return {
        "batch_id": batch.id,
        "product_id": batch.product_id,
        "days_to_expiry": days,
        "risk_score": score,
        "risk_level": risk_level(score),
        "risk_color": risk_color(score),
        "expiry_status": (
            ExpiryStatus.OK.value if (days is None or days > 0) else ExpiryStatus.EXPIRED.value
        ),
    }
