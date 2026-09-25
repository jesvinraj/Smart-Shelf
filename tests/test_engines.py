"""Unit tests for the FEFO engine, spoilage risk scoring, and dynamic pricing."""
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.fefo_engine import (
    fefo_order,
    next_batch_to_sell,
    select_batch_for_sale,
    sort_batches_fefo,
)
from engines.pricing_engine import (
    discount_reason,
    discounted_price,
    pricing_suggestion,
    recommended_discount_pct,
)
from engines.risk_engine import (
    breakdown,
    risk_color,
    risk_level,
    risk_score,
)


class FakeBatch:
    def __init__(self, bid, qty, expiry):
        self.id = bid
        self.quantity = qty
        self.expiry_date = expiry
        self.batch_code = f"BATCH-{bid}"
        self.product_id = 1
        self.supplier_id = 1


class TestEngines(unittest.TestCase):

    def test_fefo_ordering(self):
        now = datetime.now(timezone.utc)
        b_late = FakeBatch(1, 10, now + timedelta(days=30))
        b_early = FakeBatch(2, 5, now + timedelta(days=2))
        b_expired = FakeBatch(3, 8, now - timedelta(days=1))
        b_noexp = FakeBatch(4, 15, None)
        ordered = sort_batches_fefo([b_late, b_early, b_expired, b_noexp], now=now)
        ids = [b.id for b in ordered]
        self.assertEqual(ids, [2, 1, 4], f"FEFO order wrong: {ids}")
        self.assertNotIn(3, ids, "expired batch must be excluded")

    def test_fefo_allocation_crosses_batches(self):
        now = datetime.now(timezone.utc)
        b1 = FakeBatch(1, 3, now + timedelta(days=1))
        b2 = FakeBatch(2, 5, now + timedelta(days=10))
        alloc = select_batch_for_sale([b2, b1], 6, now=now)
        self.assertEqual(alloc, [{"batch_id": 1, "quantity": 3}, {"batch_id": 2, "quantity": 3}])

    def test_fefo_insufficient_raises(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValueError):
            select_batch_for_sale([FakeBatch(1, 2, now + timedelta(days=1))], 5, now=now)

    def test_next_batch(self):
        now = datetime.now(timezone.utc)
        b1 = FakeBatch(1, 4, now + timedelta(days=5))
        b2 = FakeBatch(2, 4, now + timedelta(days=1))
        self.assertEqual(next_batch_to_sell([b1, b2], now=now).id, 2)

    def test_fefo_order_labels(self):
        now = datetime.now(timezone.utc)
        b1 = FakeBatch(1, 4, now + timedelta(days=2))
        b2 = FakeBatch(2, 4, now + timedelta(days=4))
        b3 = FakeBatch(3, 4, now + timedelta(days=20))
        order = fefo_order([b3, b1, b2], now=now)
        self.assertEqual(len(order), 3)
        self.assertEqual(order[0]["label"], "SELL_FIRST")
        self.assertEqual(order[1]["label"], "SELL_NEXT")
        self.assertEqual(order[2]["label"], "NORMAL")

    def test_risk_score_high_when_expired(self):
        score = risk_score(expiry_days=-1, perishability=0.8, storage_condition="CHILLED", velocity_per_day=0.1)
        self.assertGreaterEqual(score, 70)
        self.assertIn(risk_level(score), ("HIGH", "CRITICAL"))
        self.assertIn(risk_color(score), ("orange", "red"))

    def test_risk_score_low_when_fresh(self):
        score = risk_score(expiry_days=200, perishability=0.3, storage_condition="AMBIENT", velocity_per_day=5.0)
        self.assertLess(score, 40)
        self.assertEqual(risk_level(score), "LOW")
        self.assertEqual(risk_color(score), "green")

    def test_risk_breakdown(self):
        parts = breakdown(expiry_days=5, perishability=0.8, storage_condition="CHILLED", velocity_per_day=1.0)
        self.assertIn("expiry", parts)
        self.assertIn("category", parts)
        self.assertIn("storage", parts)
        self.assertIn("velocity", parts)

    def test_dynamic_pricing_calculation(self):
        self.assertEqual(recommended_discount_pct(90), 60.0)
        self.assertEqual(recommended_discount_pct(75), 45.0)
        self.assertEqual(recommended_discount_pct(60), 30.0)
        self.assertEqual(recommended_discount_pct(45), 20.0)
        self.assertEqual(recommended_discount_pct(30), 10.0)
        self.assertEqual(recommended_discount_pct(10), 0.0)
        self.assertEqual(discounted_price(100.0, 20.0), 80.0)

    def test_pricing_suggestion_payload(self):
        risk_payload = {"risk_score": 75, "risk_level": "HIGH", "days_to_expiry": 3}
        suggestion = pricing_suggestion(risk_payload, unit_price=100.0)
        self.assertEqual(suggestion["discount_pct"], 45.0)
        self.assertEqual(suggestion["discounted_price"], 55.0)
        self.assertTrue("45% off" in suggestion["reason"])


if __name__ == "__main__":
    unittest.main()
