"""Security & Authentication helpers for SmartShelf.

Implements:
  - Password policy complexity checks
  - TOTP 2FA code generation & verification
  - Account lockout tracking (max 5 failed attempts -> 15 min lock)
  - IP-based rate limiting
  - Signed password reset tokens
  - Login audit trail logging
"""
import base64
import hashlib
import hmac
import os
import struct
import time
from datetime import datetime, timedelta, timezone

from flask import current_app, request

from data.database import db
from data.models import LoginLog, User

# In-memory IP rate-limit tracker: {ip: [timestamps]}
_IP_ATTEMPTS = {}
IP_WINDOW_SECONDS = 60
IP_MAX_ATTEMPTS = 10
LOCKOUT_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

COMMON_PASSWORDS = {
    "password", "password123", "123456", "12345678", "qwerty", "admin123",
    "welcome", "welcome1", "pass@123", "p@ssword", "p@ssw0rd", "abc12345",
}


def client_ip() -> str:
    """Return the client IP address, checking X-Forwarded-For first."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def check_ip_rate_limited() -> bool:
    """Return True if the current client IP has exceeded the login threshold."""
    ip = client_ip()
    now = time.time()
    history = _IP_ATTEMPTS.get(ip, [])
    history = [t for t in history if now - t < IP_WINDOW_SECONDS]
    _IP_ATTEMPTS[ip] = history
    if len(history) >= IP_MAX_ATTEMPTS:
        return True
    _IP_ATTEMPTS[ip].append(now)
    return False


def is_user_locked(user: User) -> bool:
    """Return True if the user is currently locked out."""
    if not user or not user.locked_until:
        return False
    now = datetime.now(timezone.utc)
    locked = user.locked_until
    if locked.tzinfo is None:
        locked = locked.replace(tzinfo=timezone.utc)
    return locked > now


def register_failed_login(user: User | None) -> dict:
    """Increment failed login count on user and trigger lockout if >= 5."""
    if not user:
        return {"locked": False, "attempts": 0}
    user.failed_attempts = (user.failed_attempts or 0) + 1
    locked = False
    if user.failed_attempts >= LOCKOUT_ATTEMPTS:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
        locked = True
    db.session.commit()
    return {"locked": locked, "attempts": user.failed_attempts}


def reset_failed_attempts(user: User) -> None:
    """Clear failed attempts and lockout upon successful authentication."""
    user.failed_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    user.last_login_ip = client_ip()
    db.session.commit()


def log_login(user_id: int | None, success: bool, method: str = "PASSWORD") -> LoginLog:
    """Record a login attempt in the login audit log."""
    entry = LoginLog(
        user_id=user_id,
        ip_address=client_ip(),
        user_agent=(request.headers.get("User-Agent") or "")[:250],
        success=success,
        method=method,
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def password_policy_error(password: str) -> str | None:
    """Validate password against complexity rules."""
    if not password or len(password) < 8:
        return "Password must be at least 8 characters long."
    if len(password) > 128:
        return "Password must not exceed 128 characters."
    if password.lower() in COMMON_PASSWORDS:
        return "Password is too common or easily guessable."
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    if not (has_upper and has_lower and (has_digit or has_special)):
        return "Password must contain uppercase, lowercase, and at least one number or special character."
    return None


def generate_totp_secret() -> str:
    """Generate a random 32-character base32 TOTP secret."""
    return base64.b32encode(os.urandom(20)).decode("utf-8").replace("=", "")


def _totp_code(secret: str, intervals_no: int | None = None) -> str:
    """Calculate the 6-digit TOTP code for a secret and time interval."""
    if intervals_no is None:
        intervals_no = int(time.time() // 30)
    key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8), casefold=True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    code = (struct.unpack(">I", h[o:o + 4])[0] & 0x7FFFFFFF) % 1000000
    return f"{code:06d}"


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against the current and adjacent 30-second windows."""
    if not secret or not code:
        return False
    code = str(code).strip()
    current_interval = int(time.time() // 30)
    for offset in (-1, 0, 1):
        if _totp_code(secret, current_interval + offset) == code:
            return True
    return False


def totp_uri(secret: str, username: str, issuer: str = "SmartShelf") -> str:
    """Return otpauth:// URI for authenticator app QR codes."""
    return f"otpauth://totp/{issuer}:{username}?secret={secret}&issuer={issuer}"


def issue_reset_token(user_id: int, expires_in: int = 3600) -> str:
    """Generate a signed, time-limited password reset token."""
    expiry = int(time.time()) + expires_in
    data = f"{user_id}:{expiry}"
    secret = current_app.config.get("SECRET_KEY", "fallback-secret").encode("utf-8")
    sig = hmac.new(secret, data.encode("utf-8"), hashlib.sha256).hexdigest()
    raw = f"{data}:{sig}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def consume_reset_token(token: str) -> int | None:
    """Verify and consume a password reset token; returns user_id or None."""
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        parts = raw.split(":")
        if len(parts) != 3:
            return None
        user_id_str, expiry_str, sig = parts
        user_id = int(user_id_str)
        expiry = int(expiry_str)
        if time.time() > expiry:
            return None
        secret = current_app.config.get("SECRET_KEY", "fallback-secret").encode("utf-8")
        expected = hmac.new(secret, f"{user_id}:{expiry}".encode("utf-8"), hashlib.sha256).hexdigest()
        if hmac.compare_digest(sig, expected):
            return user_id
    except Exception:
        return None
    return None
