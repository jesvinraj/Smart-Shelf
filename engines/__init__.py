"""Intelligence & Engine Layer: FEFO allocation, Spoilage Risk, Dynamic Pricing & Demand Forecasting."""
from engines.demand_engine import classify_products, forecast_simple, load_sales_frame, sales_velocity
from engines.fefo_engine import fefo_order, next_batch_to_sell, select_batch_for_sale, sort_batches_fefo
from engines.pricing_engine import discount_reason, discounted_price, pricing_suggestion, recommended_discount_pct
from engines.risk_engine import batch_risk, breakdown, risk_color, risk_level, risk_score

__all__ = [
    "sort_batches_fefo",
    "select_batch_for_sale",
    "next_batch_to_sell",
    "fefo_order",
    "risk_score",
    "risk_level",
    "risk_color",
    "batch_risk",
    "breakdown",
    "recommended_discount_pct",
    "discounted_price",
    "discount_reason",
    "pricing_suggestion",
    "load_sales_frame",
    "sales_velocity",
    "classify_products",
    "forecast_simple",
]
