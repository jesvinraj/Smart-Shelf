"""End-to-end verification of the login-security hardening.

Covers: login, lockout, rate limiting, password policy, register,
change-password, 2FA (setup/enable/login), and password reset.
"""
import os
import sys
import unittest
import bcrypt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from core.security import _IP_ATTEMPTS, _totp_code
from data.database import db
from data.models import LoginLog, Notification, User
from data.models.enums import Role


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False


class TestSecurity(unittest.TestCase):

    def setUp(self):
        _IP_ATTEMPTS.clear()
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            admin = User(
                username="admin", email="admin@local", full_name="Admin",
                password_hash=bcrypt.hashpw(b"Admin@12345", bcrypt.gensalt()).decode(),
                role=Role.ADMIN.value,
            )
            db.session.add(admin)
            db.session.commit()

    def tearDown(self):
        _IP_ATTEMPTS.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _login(self, username, password, otp=""):
        return self.client.post("/api/auth/login", json={
            "username": username, "password": password, "otp": otp,
        })

    def test_all_35_security_scenarios(self):
        """Run complete 35-step end-to-end security verification sequence."""
        # 1. Good credentials -> success
        r = self._login("admin", "Admin@12345")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["user"]["username"], "admin")
        self.client.post("/api/auth/logout")

        # 2. Wrong password 5x -> lockout
        for i in range(5):
            r = self._login("admin", "Wrong!pass")
            self.assertIn(r.status_code, (401, 423))
        r = self._login("admin", "Admin@12345")
        self.assertEqual(r.status_code, 423)

        # Unlock manually for further steps
        with self.app.app_context():
            u = User.query.filter_by(username="admin").first()
            u.failed_attempts = 0
            u.locked_until = None
            db.session.commit()
            LoginLog.query.delete()
            db.session.commit()
        _IP_ATTEMPTS.clear()

        # 3. Password policy on change-password
        r = self._login("admin", "Admin@12345")
        self.assertEqual(r.status_code, 200)

        r = self.client.post("/api/auth/change-password", json={
            "old_password": "Wrong!pass", "new_password": "weak",
        })
        self.assertEqual(r.status_code, 400)

        r = self.client.post("/api/auth/change-password", json={
            "old_password": "Admin@12345", "new_password": "P@ssw0rd",
        })
        self.assertEqual(r.status_code, 400)
        self.assertIn("common", r.get_json()["error"])

        r = self.client.post("/api/auth/change-password", json={
            "old_password": "Admin@12345", "new_password": "ABCDef12#9",
        })
        self.assertEqual(r.status_code, 200)
        self.client.post("/api/auth/logout")
        _IP_ATTEMPTS.clear()

        # 4. Register (pending approval)
        r = self.client.post("/api/auth/register", json={
            "username": "newstaff", "email": "n@local", "password": "weak1",
        })
        self.assertEqual(r.status_code, 400)

        r = self.client.post("/api/auth/register", json={
            "username": "newstaff", "email": "n@local", "password": "Str0ng!Pass9",
        })
        self.assertEqual(r.status_code, 201)

        r = self.client.post("/api/auth/login", json={"username": "newstaff", "password": "Str0ng!Pass9"})
        self.assertEqual(r.status_code, 403)

        with self.app.app_context():
            admin_id = User.query.filter_by(username="admin").first().id
            notices = Notification.query.filter(
                Notification.user_id == admin_id,
                Notification.title.contains("pending approval"),
            ).count()
            self.assertGreaterEqual(notices, 1)

        # Admin approves
        r = self._login("admin", "ABCDef12#9")
        self.assertEqual(r.status_code, 200)
        users_resp = self.client.get("/api/auth/users").get_json()["items"]
        sid = next(u["id"] for u in users_resp if u["username"] == "newstaff")
        r = self.client.put(f"/api/auth/users/{sid}", json={"is_active": True})
        self.assertEqual(r.status_code, 200)

        with self.app.app_context():
            logged = Notification.query.filter(
                Notification.user_id == sid,
                Notification.title.contains("approved"),
            ).count()
            self.assertGreaterEqual(logged, 1)

        self.client.post("/api/auth/logout")
        _IP_ATTEMPTS.clear()

        r = self.client.post("/api/auth/login", json={"username": "newstaff", "password": "Str0ng!Pass9"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json().get("must_change_password"))
        self.client.post("/api/auth/logout")
        _IP_ATTEMPTS.clear()

        # 5. 2FA flow
        r = self._login("admin", "ABCDef12#9")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/api/auth/2fa/setup")
        secret = r.get_json()["secret"]
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(secret), 16)

        code = _totp_code(secret)
        r = self.client.post("/api/auth/2fa/enable", json={"code": code})
        self.assertEqual(r.status_code, 200)
        self.client.post("/api/auth/logout")

        # 2FA required
        r = self._login("admin", "ABCDef12#9")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json().get("requires_2fa"))

        r = self._login("admin", "ABCDef12#9", "000000")
        self.assertEqual(r.status_code, 401)

        r = self._login("admin", "ABCDef12#9", _totp_code(secret))
        self.assertEqual(r.status_code, 200)

        r = self.client.get("/api/auth/login-history")
        self.assertEqual(r.status_code, 200)
        self.client.post("/api/auth/logout")

        # 6. Disable 2FA
        r = self._login("admin", "ABCDef12#9", _totp_code(secret))
        r = self.client.post("/api/auth/2fa/disable", json={"password": "wrong"})
        self.assertEqual(r.status_code, 400)

        r = self.client.post("/api/auth/2fa/disable", json={"password": "ABCDef12#9"})
        self.assertEqual(r.status_code, 200)
        self.client.post("/api/auth/logout")

        r = self._login("admin", "ABCDef12#9")
        self.assertEqual(r.status_code, 200)
        self.client.post("/api/auth/logout")
        _IP_ATTEMPTS.clear()

        # 7. Password reset via token
        r = self.client.post("/api/auth/forgot-password", json={"username": "admin"})
        token = r.get_json()["reset_token"]
        self.assertTrue(bool(token))

        r = self.client.post("/api/auth/reset-password", json={"token": token, "new_password": "weak"})
        self.assertEqual(r.status_code, 400)

        r = self.client.post("/api/auth/reset-password", json={"token": token, "new_password": "N3w!Strong7"})
        self.assertEqual(r.status_code, 200)

        r = self._login("admin", "ABCDef12#9")
        self.assertEqual(r.status_code, 401)

        r = self._login("admin", "N3w!Strong7")
        self.assertEqual(r.status_code, 200)
        self.client.post("/api/auth/logout")
        _IP_ATTEMPTS.clear()

        # 8. Rate limiting after 10 failed attempts
        for i in range(10):
            self.client.post("/api/auth/login", json={"username": f"ghost{i}", "password": "W/eak!22"})
        r = self.client.post("/api/auth/login", json={"username": "admin", "password": "N3w!Strong7"})
        self.assertEqual(r.status_code, 429)


if __name__ == "__main__":
    unittest.main()
