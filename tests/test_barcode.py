"""Unit and integration tests for Module 17 - Barcode Scanning & Lookup API."""
import os
import sys
import unittest
from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from cli import seed
from core.security import _IP_ATTEMPTS
from data.database import db
from data.models import Product


class TestBarcodeConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPIRY_ALERT_DAYS = 30
    REORDER_SAFETY_FACTOR = 1.5


class TestBarcodeModule(unittest.TestCase):

    def setUp(self):
        _IP_ATTEMPTS.clear()
        self.app = create_app(TestBarcodeConfig)
        with self.app.app_context():
            db.create_all()
            runner = CliRunner()
            runner.invoke(seed)
        self.client = self.app.test_client()
        # Login as admin
        r = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(r.status_code, 200, "Setup login failed")

    def tearDown(self):
        _IP_ATTEMPTS.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_barcode_lookup_existing_product(self):
        """Confirm barcode lookup returns matching product details."""
        r = self.client.get("/api/products/lookup/8901030000014")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["name"], "Milk 1L")
        self.assertEqual(data["sku"], "MILK1")
        self.assertEqual(data["barcode"], "8901030000014")
        self.assertEqual(data["category"], "Dairy")
        self.assertEqual(data["unit"], "btl")
        self.assertEqual(data["unit_price"], 60.0)
        self.assertEqual(data["cost_price"], 40.0)
        self.assertTrue(data["is_perishable"])
        self.assertEqual(data["reorder_level"], 20)

    def test_barcode_lookup_unknown_barcode_returns_404(self):
        """Confirm lookup of non-existent barcode returns clear 404 response."""
        r = self.client.get("/api/products/lookup/9999999999999")
        self.assertEqual(r.status_code, 404)
        data = r.get_json()
        self.assertIn("error", data)
        self.assertEqual(data["barcode"], "9999999999999")

    def test_barcode_duplicate_prevention(self):
        """Confirm product creation rejects duplicate barcode with 409."""
        r = self.client.post(
            "/api/products",
            json={
                "name": "Another Milk",
                "sku": "MILK-NEW",
                "barcode": "8901030000014",  # Already assigned to Milk 1L
                "unit_price": 65.0,
                "cost_price": 45.0,
            },
        )
        self.assertEqual(r.status_code, 409)
        self.assertIn("Barcode exists", r.get_json().get("error", ""))

    def test_quick_batch_inflow_after_barcode_lookup(self):
        """Confirm end-to-end flow: lookup product -> receive inbound batch."""
        lookup_res = self.client.get("/api/products/lookup/8901030000021")  # Bread
        self.assertEqual(lookup_res.status_code, 200)
        prod = lookup_res.get_json()

        recv_res = self.client.post(
            "/api/inventory/receive",
            json={
                "product_id": prod["id"],
                "quantity": 25,
                "batch_code": "BARCODE-BATCH-01",
                "cost_price": prod["cost_price"],
                "expiry_date": "2026-10-15",
                "notes": "Scanned via Barcode Quick Entry",
            },
        )
        self.assertEqual(recv_res.status_code, 201)

    def test_scan_presentation_page_renders(self):
        """Confirm /scan presentation page renders 200 for authenticated user."""
        r = self.client.get("/scan")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Barcode Scanning & Quick Entry", r.data)
        self.assertIn(b"html5-qrcode", r.data)


if __name__ == "__main__":
    unittest.main()
