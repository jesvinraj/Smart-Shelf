"""User & Access Management model.
Roles (lowest to highest): USER, STAFF, CASHIER, BILLER, MANAGER, ADMIN.
Used for RBAC and the audit trail.

Includes security-related fields: account lockout, TOTP 2FA, and last login.
"""
from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from data.database import db, login_manager
from data.models.enums import Role


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default=Role.STAFF.value)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Security fields
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    totp_secret = Column(String(64), nullable=True)
    totp_enabled = Column(Boolean, default=False)
    must_change_password = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)

    # Relationships
    login_logs = relationship(
        "LoginLog", back_populates="user", cascade="all, delete-orphan"
    )

    _ROLE_HIERARCHY = [
        Role.USER.value,
        Role.STAFF.value,
        Role.CASHIER.value,
        Role.BILLER.value,
        Role.MANAGER.value,
        Role.ADMIN.value,
    ]

    def has_role(self, required_role: Role) -> bool:
        """Hierarchical role check: returns True if user is >= required_role."""
        try:
            user_idx = self._ROLE_HIERARCHY.index(self.role)
            req_idx = self._ROLE_HIERARCHY.index(
                required_role.value if isinstance(required_role, Role) else required_role
            )
            return user_idx >= req_idx
        except ValueError:
            return False

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN.value

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "phone": self.phone,
            "is_active": self.is_active,
            "totp_enabled": self.totp_enabled,
            "must_change_password": self.must_change_password,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
