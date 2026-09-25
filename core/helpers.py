"""General helpers shared across the application."""
import re
import secrets


def make_ref(prefix: str, length: int = 8) -> str:
    """Generate a short unique reference like `INV-1D54F2A3`."""
    return f"{prefix}-{secrets.token_hex(length // 2).upper()}"


def sku_clean(name: str) -> str:
    """Derive a simple SKU from a product name."""
    base = re.sub(r"[^A-Za-z0-9]+", "", name).upper()[:8]
    return base or "SKU"


def risk_color(score: int) -> str:
    """Map a spoilage risk score to a status class name."""
    if score >= 80:
        return "red"
    if score >= 70:
        return "orange"
    if score >= 40:
        return "yellow"
    return "green"
