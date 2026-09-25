"""Module 9 & 14 - Demand analysis, forecasting & dashboard analytics API."""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import func

from data.database import db
from data.models import Product, Sale, StockBatch, Wastage
from engines.demand_engine import classify_products, forecast_simple, sales_velocity
from engines.risk_engine import batch_risk
from services.expiry_service import classify_batch

bp = Blueprint("analytics", __name__, url_prefix="/api")


@bp.get("/dashboard")
@login_required
def dashboard():
    days = int(request.args.get("days", 30))
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    total_stock_value = (
        db.session.query(func.coalesce(func.sum(StockBatch.quantity * StockBatch.cost_price), 0.0))
        .scalar()
    )
    total_stock_units = (
        db.session.query(func.coalesce(func.sum(StockBatch.quantity), 0)).scalar()
    )
    product_count = Product.query.filter(Product.is_active.is_(True)).count()
    batch_count = StockBatch.query.count()
    revenue = (
        db.session.query(func.coalesce(func.sum(Sale.total_amount), 0.0))
        .filter(Sale.sale_date >= cutoff)
        .scalar()
    )
    sales_count = Sale.query.filter(Sale.sale_date >= cutoff).count()
    waste_value = (
        db.session.query(func.coalesce(func.sum(Wastage.potential_loss), 0.0)).scalar()
    )

    velocity_map = {r["product_id"]: r["velocity_per_day"] for r in sales_velocity(30).to_dict("records")}
    risks = []
    risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for b in StockBatch.query.filter(StockBatch.quantity > 0).all():
        r = batch_risk(b, velocity_map.get(b.product_id))
        risks.append({**r, "product_name": b.product.name if b.product else "",
                      "product_sku": b.product.sku if b.product else None,
                      "batch_code": b.batch_code,
                      "unit_price": b.product.unit_price if b.product else 0.0,
                      "days_left": r["days_to_expiry"]})
        level = r["risk_level"]
        bucket = "CRITICAL" if level == "HIGH" and r["risk_score"] >= 80 else level
        risk_dist[bucket] = risk_dist.get(bucket, 0) + 1
    risks.sort(key=lambda x: x["risk_score"], reverse=True)

    alert_days = 30
    exp_status = {"OK": 0, "EXPIRING_SOON": 0, "EXPIRED": 0}
    for b in StockBatch.query.filter(StockBatch.quantity > 0).all():
        exp_status[classify_batch(b, alert_days).value] += 1

    trend = (
        db.session.query(
            func.date(Sale.sale_date).label("d"),
            func.sum(Sale.total_amount).label("rev"),
        )
        .filter(Sale.sale_date >= cutoff)
        .group_by(func.date(Sale.sale_date))
        .order_by(func.date(Sale.sale_date))
        .all()
    )

    low_stock = [p for p in Product.query.all() if p.total_stock <= p.reorder_level]

    return jsonify({
        "kpis": {
            "product_count": product_count,
            "stock_units": int(total_stock_units),
            "batch_count": batch_count,
            "inventory_value": round(float(total_stock_value), 2),
            "revenue": round(float(revenue), 2),
            "sales_count": sales_count,
            "waste_value": round(float(waste_value), 2),
            "risk_items": len(risks),
            "expiring_count": exp_status["EXPIRING_SOON"],
            "expired_count": exp_status["EXPIRED"],
        },
        "expiry_summary": exp_status,
        "risk_distribution": risk_dist,
        "sales_trend": [{"date": str(r.d), "revenue": round(float(r.rev), 2)} for r in trend],
        "top_risk": risks[:10],
        "low_stock": [{"id": p.id, "name": p.name, "sku": p.sku, "stock": p.total_stock,
                       "reorder_level": p.reorder_level} for p in low_stock[:10]],
    })


@bp.get("/ai/velocity")
@login_required
def velocity():
    return jsonify(classify_products())


@bp.get("/ai/demand-analysis")
@login_required
def demand_analysis():
    days = int(request.args.get("days", 30))
    velocity_df = sales_velocity(days=days)
    return jsonify(velocity_df.to_dict("records"))


@bp.get("/ai/forecast/<int:product_id>")
@login_required
def forecast(product_id: int):
    horizon = int(request.args.get("horizon", 7))
    return jsonify(forecast_simple(product_id, history_days=60, horizon=horizon))
