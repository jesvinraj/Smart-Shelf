"""Module 1 - User, Access & Security Management API."""
import re
import bcrypt
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from core.decorators import at_least
from core.security import (
    check_ip_rate_limited,
    client_ip,
    consume_reset_token,
    generate_totp_secret,
    is_user_locked,
    issue_reset_token,
    log_login,
    password_policy_error,
    register_failed_login,
    reset_failed_attempts,
    totp_uri,
    verify_totp,
)
from data.database import db
from data.models import LoginLog, Notification, Role, User
from services.alert_service import notify_roles
from services.audit_service import log_action

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def _find_user(identifier: str) -> User | None:
    return User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("username") or data.get("email") or "").strip()
    password = data.get("password") or ""
    otp_token = (data.get("otp") or "").strip()

    if not identifier or not password:
        return jsonify({"error": "username/email and password required"}), 400

    if check_ip_rate_limited():
        log_login(None, success=False)
        return jsonify({"error": "Too many login attempts. Try again later."}), 429

    user = _find_user(identifier)
    if user is None:
        verify_password(password, hash_password("dummy-placeholder-12345"))
        log_login(None, success=False)
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(password, user.password_hash):
        outcome = register_failed_login(user)
        if outcome["locked"]:
            return jsonify({
                "error": "Account locked due to too many failed attempts. Try again later.",
            }), 423
        return jsonify({"error": "Invalid credentials"}), 401

    if is_user_locked(user):
        return jsonify({
            "error": "Account locked due to too many failed attempts. Try again later.",
        }), 423

    if not user.is_active:
        log_login(user.id, success=False)
        if user.must_change_password:
            return jsonify({
                "error": "Your account is pending admin approval. Contact an administrator.",
            }), 403
        return jsonify({"error": "Account disabled"}), 403

    if user.totp_enabled:
        if not otp_token:
            return jsonify({"requires_2fa": True, "user": {"username": user.username}}), 200
        if not verify_totp(user.totp_secret, otp_token):
            register_failed_login(user)
            return jsonify({"error": "Invalid 2FA code"}), 401

    login_user(user)
    reset_failed_attempts(user)
    log_login(user.id, success=True, method="TOTP" if user.totp_enabled else "PASSWORD")
    log_action("LOGIN", "USER", user.id, f"login from {client_ip()}", user.id)

    resp = {"user": user.to_dict()}
    if user.must_change_password:
        resp["must_change_password"] = True
    return jsonify(resp)


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or username or "").strip()

    if not username or not email or not password:
        return jsonify({"error": "username, email, password required"}), 400

    if not re.match(r"^[A-Za-z0-9_.-]{3,50}$", username):
        return jsonify({"error": "Invalid username (3-50 chars, letters/digits/_ . -)"}), 400
    if "@" not in email or len(email) > 120:
        return jsonify({"error": "Invalid email address"}), 400
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username or email already exists"}), 409

    policy = password_policy_error(password)
    if policy:
        return jsonify({"error": policy}), 400

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        role=Role.USER.value,
        is_active=False,
        must_change_password=True,
    )
    db.session.add(user)
    db.session.commit()
    log_action("REGISTER", "USER", user.id, f"self-registration from {client_ip()}", user.id)
    notify_roles(
        [Role.ADMIN, Role.MANAGER],
        "New account pending approval",
        f"{full_name} (@{username}) registered and is waiting for approval.",
        severity="WARNING", link="/settings",
    )
    return jsonify({"user": user.to_dict()}), 201


@bp.get("/me")
@login_required
def me():
    return jsonify({"user": current_user.to_dict()})


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"ok": True})


@bp.post("/change-password")
@login_required
def change_password():
    data = request.get_json(silent=True) or {}
    old = data.get("old_password") or ""
    new = data.get("new_password") or ""

    if not verify_password(old, current_user.password_hash):
        return jsonify({"error": "Old password is incorrect"}), 400
    if old == new:
        return jsonify({"error": "New password must differ from the old one"}), 400

    policy = password_policy_error(new)
    if policy:
        return jsonify({"error": policy}), 400

    current_user.password_hash = hash_password(new)
    current_user.must_change_password = False
    db.session.commit()
    log_action("PASSWORD", "USER", current_user.id, "password changed", current_user.id)
    return jsonify({"ok": True})


@bp.get("/2fa/setup")
@login_required
def twofa_setup():
    if not current_user.totp_secret:
        current_user.totp_secret = generate_totp_secret()
        db.session.commit()
    uri = totp_uri(current_user.totp_secret, current_user.username)
    return jsonify({
        "secret": current_user.totp_secret,
        "otpauth_uri": uri,
        "issuer": "SmartShelf",
        "enabled": current_user.totp_enabled,
    })


@bp.post("/2fa/enable")
@login_required
def twofa_enable():
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    if not verify_totp(current_user.totp_secret, code):
        return jsonify({"error": "Invalid 2FA code. Please scan and try again."}), 400
    current_user.totp_enabled = True
    db.session.commit()
    log_action("2FA", "USER", current_user.id, "2FA enabled", current_user.id)
    return jsonify({"ok": True, "enabled": True})


@bp.post("/2fa/disable")
@login_required
def twofa_disable():
    data = request.get_json(silent=True) or {}
    if not verify_password(data.get("password", ""), current_user.password_hash):
        return jsonify({"error": "Password is incorrect"}), 400
    current_user.totp_enabled = False
    current_user.totp_secret = None
    db.session.commit()
    log_action("2FA", "USER", current_user.id, "2FA disabled", current_user.id)
    return jsonify({"ok": True, "enabled": False})


@bp.post("/forgot-password")
def forgot_password():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("username") or data.get("email") or "").strip()
    user = _find_user(identifier) if identifier else None
    if user and user.is_active:
        token = issue_reset_token(user.id)
        log_action("RESET_LINK", "USER", user.id, f"reset link issued from {client_ip()}", user.id)
        return jsonify({"ok": True, "reset_token": token})
    return jsonify({"ok": True})


@bp.post("/reset-password")
def reset_password():
    data = request.get_json(silent=True) or {}
    token = data.get("token") or ""
    new_password = data.get("new_password") or ""
    user_id = consume_reset_token(token)
    if user_id is None:
        return jsonify({"error": "Reset token is invalid or expired"}), 400
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Account not available"}), 400

    policy = password_policy_error(new_password)
    if policy:
        return jsonify({"error": policy}), 400

    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    user.failed_attempts = 0
    user.locked_until = None
    db.session.commit()
    log_action("RESET", "USER", user.id, "password reset via token", user.id)
    return jsonify({"ok": True})


@bp.get("/login-history")
@login_required
def login_history():
    rows = (
        LoginLog.query.filter(LoginLog.user_id == current_user.id)
        .order_by(LoginLog.created_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([
        {
            "id": r.id, "ip_address": r.ip_address, "method": r.method,
            "success": r.success, "user_agent": r.user_agent,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ])


@bp.get("/users")
@at_least(Role.MANAGER)
def users():
    items = [u.to_dict() for u in User.query.all()]
    return jsonify({"items": items, "total": len(items)})


@bp.post("/users")
@at_least(Role.MANAGER)
def create_user():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username, password required"}), 400
    if User.query.filter(User.username == username).first():
        return jsonify({"error": "Username exists"}), 409

    policy = password_policy_error(password)
    if policy:
        return jsonify({"error": policy}), 400

    role = (data.get("role") or Role.STAFF.value).strip().upper()
    if role not in {r.value for r in Role}:
        return jsonify({"error": "Invalid role"}), 400
    if role == Role.ADMIN.value and not current_user.is_admin:
        return jsonify({"error": "Only admins can assign the ADMIN role"}), 403

    user = User(
        username=username,
        email=(data.get("email") or "").strip() or f"{username}@local",
        full_name=(data.get("full_name") or username).strip(),
        password_hash=hash_password(password),
        role=role,
        phone=data.get("phone"),
        must_change_password=True,
    )
    db.session.add(user)
    db.session.commit()
    log_action("CREATE", "USER", user.id, f"user created by {current_user.username}", current_user.id)
    return jsonify({"user": user.to_dict()}), 201


@bp.put("/users/<int:user_id>")
@at_least(Role.MANAGER)
def update_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}

    if data.get("role") and data["role"] != user.role:
        if user.is_admin and user.id != current_user.id and not current_user.is_admin:
            return jsonify({"error": "Only admins can change an admin's role"}), 403
        new_role = data["role"]
        if new_role == Role.ADMIN.value and not current_user.is_admin:
            return jsonify({"error": "Only admins can assign the ADMIN role"}), 403
        if new_role in (Role.MANAGER.value, Role.ADMIN.value) and not current_user.has_role(Role.MANAGER):
            return jsonify({"error": "Insufficient permissions to assign this role"}), 403
        user.role = new_role

    if "full_name" in data:
        user.full_name = data["full_name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "is_active" in data:
        if user.id == current_user.id and not bool(data["is_active"]):
            return jsonify({"error": "You cannot deactivate your own account"}), 400
        if not user.is_active and bool(data["is_active"]):
            db.session.add(Notification(
                user_id=user.id,
                title="Account approved",
                message="Your account has been approved. You can now log in.",
                severity="INFO", link="/",
            ))
        user.is_active = bool(data["is_active"])
    if data.get("password"):
        policy = password_policy_error(data["password"])
        if policy:
            return jsonify({"error": policy}), 400
        user.password_hash = hash_password(data["password"])
    db.session.commit()
    log_action("UPDATE", "USER", user.id, f"user updated by {current_user.username}", current_user.id)
    return jsonify({"user": user.to_dict()})


@bp.delete("/users/<int:user_id>")
@at_least(Role.ADMIN)
def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    if user.id == current_user.id:
        return jsonify({"error": "You cannot delete your own account"}), 400
    user.is_active = False
    db.session.commit()
    log_action("DELETE", "USER", user.id, f"user disabled by {current_user.username}", current_user.id)
    return jsonify({"ok": True})
