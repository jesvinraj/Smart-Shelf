"""End-to-end smoke test verifying core flows across all 5 layers."""
import os
import sys
import unittest
from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from cli import seed
from core.security import _IP_ATTEMPTS
from data.database import db


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPIRY_ALERT_DAYS = 30
    REORDER_SAFETY_FACTOR = 1.5


class TestSmoke(unittest.TestCase):

    def setUp(self):
        _IP_ATTEMPTS.clear()
        self.app = create_app(TestConfig)
        with self.app.app_context():
            db.create_all()
            runner = CliRunner()
            runner.invoke(seed)
        self.client = self.app.test_client()

    def tearDown(self):
        _IP_ATTEMPTS.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_full_flow(self):
        # 1. Login
        r = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(r.status_code, 200, f"Login failed: {r.data}")

        # 2. Dashboard KPIs
        r = self.client.get("/api/dashboard")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("kpis", data)
        self.assertGreater(data["kpis"]["product_count"], 0)

        # 3. Inbound stock receiving
        r = self.client.post(
            "/api/inventory/receive",
            json={
                "product_id": 1,
                "quantity": 10,
                "batch_code": "FEFO-LATE",
                "expiry_date": "2030-12-31",
            },
        )
        self.assertEqual(r.status_code, 201)

        # 4. FEFO checkout
        r = self.client.post("/api/sales", json={"items": [{"product_id": 1, "quantity": 5}]})
        self.assertEqual(r.status_code, 201)
        invoice = r.get_json()["invoice_number"]
        self.assertTrue(invoice.startswith("INV-"))

        # 5. FEFO ordering API
        r = self.client.get("/api/fefo")
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.get_json()["items"]), 0)

        # 6. Spoilage risk and dynamic pricing endpoints
        r = self.client.get("/api/ai/pricing")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/api/ai/risk")
        self.assertEqual(r.status_code, 200)

        # 7. Reports
        for path in (
            "/api/reports/sales?days=30",
            "/api/reports/inventory",
            "/api/reports/expiry",
            "/api/reports/discounts",
            "/api/reports/waste",
            "/api/reports/performance",
        ):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, f"Path {path} failed with {r.status_code}")

        # 8. Alert scans
        r = self.client.post("/api/alerts/scan")
        self.assertEqual(r.status_code, 200)

        # 9. Server-rendered presentation pages
        for page in (
            "/",
            "/products",
            "/suppliers",
            "/inventory",
            "/batches",
            "/scan",
            "/fefo",
            "/risk",
            "/pricing",
            "/sales",
            "/analytics",
            "/alerts",
            "/waste",
            "/reports",
            "/settings",
        ):
            r = self.client.get(page)
            self.assertEqual(r.status_code, 200, f"Page {page} failed to render")


if __name__ == "__main__":
    unittest.main()
