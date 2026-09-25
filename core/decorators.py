"""Authentication and authorization decorators (RBAC).

Roles (lowest to highest): USER < STAFF < CASHIER < BILLER < MANAGER < ADMIN.
"""
from functools import wraps

from flask import abort
from flask_login import current_user

from data.models.enums import Role


def login_required_view(fn):
    """Require an authenticated user; return JSON 401 for API callers."""
    from flask_login import login_required
    return login_required(fn)


def roles_required(*roles: Role):
    """Require the current user to hold one of the given roles."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in {r.value for r in roles}:
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def at_least(role: Role):
    """Require the current user to be at least the given role (hierarchical)."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(role):
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
