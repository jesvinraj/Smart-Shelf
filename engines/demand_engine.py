"""Demand & Sales Analysis using Pandas.

Computes sales velocity and classifies fast/slow-moving products from the
historical SaleItem table.
"""
from datetime import datetime, timedelta, timezone

import pandas as pd

from data.database import db
from data.models import Product, Sale, SaleItem


def load_sales_frame(days: int | None = None) -> pd.DataFrame:
    """Return a DataFrame of sale line items with date + qty."""
    q = db.session.query(
        SaleItem.product_id.label("product_id"),
        SaleItem.quantity.label("quantity"),
        Sale.sale_date.label("sale_date"),
    ).join(Sale, Sale.id == SaleItem.sale_id)
    if days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        q = q.filter(Sale.sale_date >= cutoff)
    rows = q.all()
    return pd.DataFrame(
        [
            {"product_id": r.product_id, "quantity": r.quantity, "sale_date": r.sale_date}
            for r in rows
        ]
    )


def sales_velocity(days: int = 30) -> pd.DataFrame:
    """Units sold per day per product over a window."""
    df = load_sales_frame(days=days)
    if df.empty:
        return pd.DataFrame(columns=["product_id", "total_quantity", "velocity_per_day"])
    g = df.groupby("product_id")["quantity"].sum().reset_index()
    g["velocity_per_day"] = (g["quantity"] / days).round(3)
    return g


def classify_products() -> list[dict]:
    """Return per-product velocity and fast/slow movement classification."""
    velocity = sales_velocity(days=30)
    if velocity.empty:
        return []
    median = velocity["velocity_per_day"].median() or 0
    result = []
    products = {p.id: p.name for p in Product.query.all()}
    for _, row in velocity.iterrows():
        v = float(row["velocity_per_day"])
        category = "FAST" if v >= median * 1.2 else ("SLOW" if v <= median * 0.5 else "NORMAL")
        result.append(
            {
                "product_id": int(row["product_id"]),
                "product_name": products.get(int(row["product_id"]), ""),
                "total_quantity": int(row["quantity"]),
                "velocity_per_day": v,
                "movement_class": category,
            }
        )
    result.sort(key=lambda r: r["velocity_per_day"], reverse=True)
    return result


def forecast_simple(product_id: int, history_days: int = 60, horizon: int = 7) -> dict:
    """Forecast demand over the next `horizon` days via moving average."""
    df = load_sales_frame(days=history_days)
    if df.empty:
        return {"product_id": product_id, "forecast": [], "model": "none", "confidence": 0.0}
    sub = df[df.product_id == product_id]
    if sub.empty:
        return {"product_id": product_id, "forecast": [], "model": "none", "confidence": 0.0}
    daily = (
        sub.groupby(sub.sale_date.dt.date)["quantity"]
        .sum()
        .reindex(
            pd.date_range(start=sub.sale_date.min(), end=datetime.now(timezone.utc).date()).floor("D"),
            fill_value=0,
        )
    )
    window = max(7, min(30, len(daily) // 2)) if len(daily) else 7
    avg = float(daily.tail(window).mean()) if len(daily) else 0.0
    forecast = [{"day": i + 1, "qty": round(avg, 3)} for i in range(horizon)]
    confidence = min(1.0, len(daily) / max(history_days, 1))
    return {
        "product_id": product_id,
        "forecast": forecast,
        "model": "moving_average",
        "confidence": round(confidence, 3),
    }
