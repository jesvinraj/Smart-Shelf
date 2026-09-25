"""Dynamic Pricing Engine (pure Python).

Automatically recommends a discount percentage based on the spoilage risk
score, so higher-risk stock is discounted more aggressively to recover
revenue before expiry. Includes the discount amount/price helpers used by
the Pricing screen.
"""
from engines.risk_engine import risk_level


def recommended_discount_pct(risk_score_value: int) -> float:
    """Map a spoilage risk score (0-100) to a recommended discount %."""
    if risk_score_value >= 85:
        return 60.0
    if risk_score_value >= 70:
        return 45.0
    if risk_score_value >= 55:
        return 30.0
    if risk_score_value >= 40:
        return 20.0
    if risk_score_value >= 25:
        return 10.0
    return 0.0


def discounted_price(unit_price: float, discount_pct: float) -> float:
    return round(unit_price * (1 - discount_pct / 100), 2)


def discount_reason(
    risk_score_value: int,
    velocity_per_day: float | None = None,
    days_to_expiry: int | None = None,
) -> str:
    """Human-readable justification for the recommended discount."""
    reasons = []
    if days_to_expiry is not None:
        if days_to_expiry < 0:
            reasons.append("expired (must be written off or heavily discounted)")
        elif days_to_expiry <= 1:
            reasons.append("expires in 1 day")
        elif days_to_expiry <= 5:
            reasons.append(f"expires in {days_to_expiry} days")
        elif days_to_expiry <= 30:
            reasons.append(f"expires in {days_to_expiry} days")
    if risk_score_value >= 40:
        reasons.append("high spoilage risk")
    if velocity_per_day is not None and velocity_per_day < 1:
        reasons.append("slow-moving product")
    if not reasons:
        return "Low risk / healthy stock — no discount needed."
    pct = recommended_discount_pct(risk_score_value)
    level = risk_level(risk_score_value)
    if level in ("CRITICAL", "HIGH"):
        return f"{'Immediate' if level == 'CRITICAL' else 'Recommend'} {pct:.0f}% off ({', '.join(reasons)})."
    return f"Consider {pct:.0f}% off ({', '.join(reasons)})."


def pricing_suggestion(risk_payload: dict, unit_price: float = 0.0) -> dict:
    score = risk_payload["risk_score"]
    pct = recommended_discount_pct(score)
    return {
        "risk_score": score,
        "risk_level": risk_payload["risk_level"],
        "discount_pct": pct,
        "original_price": unit_price,
        "discounted_price": discounted_price(unit_price, pct),
        "reason": discount_reason(
            score,
            velocity_per_day=None,
            days_to_expiry=risk_payload.get("days_to_expiry"),
        ),
    }
