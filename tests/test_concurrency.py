"""Concurrency and atomicity test for FEFO stock deduction."""
import os
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.exc import OperationalError
from app import create_app
from data.database import db
from data.models import InventoryMovement, Product, StockBatch
from data.models.enums import MovementType
from services.stock_service import deduct_stock


def _config(db_path: str):
    return type(
        "ConcurrencyConfig",
        (),
        {
            "TESTING": True,
            "SECRET_KEY": "concurrency-test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ENGINE_OPTIONS": {"connect_args": {"timeout": 5}},
            "SQLALCHEMY_POOL_SIZE": 25,
            "SQLALCHEMY_MAX_OVERFLOW": 25,
        },
    )


def _seed(app, units: int, expiry_days: int = 30) -> int:
    with app.app_context():
        db.create_all()
        product = Product(
            name="Concurrency Milk",
            sku="CONC-1",
            unit="btl",
            unit_price=60.0,
            cost_price=40.0,
            is_perishable=True,
        )
        db.session.add(product)
        db.session.flush()
        batch = StockBatch(
            product_id=product.id,
            batch_code="CONC-B1",
            quantity=units,
            expiry_date=datetime.now(timezone.utc) + timedelta(days=expiry_days),
        )
        db.session.add(batch)
        db.session.commit()
        return product.id


def _worker(app, product_id, results, index, retries, delay):
    for _ in range(retries):
        try:
            with app.app_context():
                deduct_stock(product_id, 1, reference="CONC-TEST")
            results[index] = ("OK", None)
            return
        except OperationalError as exc:
            if "locked" in str(exc).lower():
                time.sleep(delay)
                continue
            results[index] = ("ERR", str(exc))
            return
        except ValueError:
            time.sleep(delay)
            continue
    results[index] = ("FAILED", "retries exhausted")


class TestConcurrency(unittest.TestCase):

    def test_concurrent_fefo_deductions_prevent_oversell(self):
        units = 20
        threads = 20
        retries = 80
        delay = 0.01

        tmp = tempfile.mkdtemp()
        db_path = os.path.join(tmp, "concurrency.db")
        app = create_app(_config(db_path))
        product_id = _seed(app, units)

        results = [None] * threads
        jobs = [
            threading.Thread(
                target=_worker, args=(app, product_id, results, i, retries, delay)
            )
            for i in range(threads)
        ]
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()

        with app.app_context():
            batch = StockBatch.query.filter_by(batch_code="CONC-B1").one()
            final_qty = batch.quantity
            outs = (
                InventoryMovement.query.filter_by(movement_type=MovementType.OUT.value)
                .count()
            )

        ok = sum(1 for r in results if r is not None and r[0] == "OK")
        errs = [r for r in results if r is not None and r[0] != "OK"]

        self.assertEqual(ok, units, f"Expected {units} successful checkouts, got {ok}")
        self.assertEqual(final_qty, 0, f"Expected 0 remaining stock, got {final_qty}")
        self.assertEqual(outs, ok, f"Expected {ok} OUT movements, got {outs}")
        self.assertEqual(len(errs), 0, f"Unexpected errors: {errs}")

        # Drain check: oversell attempt must raise ValueError
        with self.assertRaises(ValueError):
            with app.app_context():
                deduct_stock(product_id, 1, reference="CONC-OVERSELL")

        with app.app_context():
            db.session.remove()
            db.engine.dispose()

        # Clean up temporary database file safely
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
            if os.path.exists(tmp):
                os.rmdir(tmp)
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
