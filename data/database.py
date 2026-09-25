"""Shared SQLAlchemy / Flask-Login / Flask-Migrate instances.

Central place for the extension objects so models, routes and services all
import `db` from the same location. This mirrors the `utils.database`
module referenced in the SmartShelf structure.
"""
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def check_database(app) -> dict:
    """Verify DB connectivity and return backend info for a /api/health check.

    Never raises: returns a dict with ``ok`` and a human-readable message so
    the API can surface DB misconfiguration gracefully.
    """
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    from config import is_sqlite

    if is_sqlite(uri):
        backend = "sqlite"
    elif uri.startswith("mysql"):
        backend = "mysql"
    elif uri.startswith(("postgresql", "postgres")):
        backend = "postgresql"
    else:
        backend = "unknown"

    try:
        with app.app_context():
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        return {"ok": True, "backend": backend, "driver": uri.split("://", 1)[0]}
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"ok": False, "backend": backend, "error": str(exc)}
