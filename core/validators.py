"""Validation helpers used across routes."""
from datetime import datetime


def parse_date(value, field="date"):
    """Parse an ISO-8601 date/datetime string, or return None."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        raise ValueError(f"Invalid {field}: {value!r}")


def require_json_payload(data, required: tuple[str, ...]):
    """Raise a ValueError listing any missing required keys."""
    missing = [k for k in required if k not in data or data[k] in (None, "")]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")


def to_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def str2bool(value):
    if value is None:
        return False
    return str(value).strip().lower() in ("1", "true", "yes", "on")
