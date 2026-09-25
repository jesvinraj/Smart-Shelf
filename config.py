"""Application configuration loaded from environment variables.

Supports SQLite (default, zero setup), MySQL and PostgreSQL as backends.
Set `DATABASE_URL` to switch, e.g.:

    mysql+pymysql://user:pass@localhost/smartshelf
    postgresql+psycopg2://user:pass@localhost/smartshelf

The correct driver must be installed (see requirements-optional.txt).
"""
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_DEFAULT_URL = "sqlite:///" + os.path.join(BASE_DIR, "smart_shelf.db")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", _DEFAULT_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLite rejects pooling options, so only apply them to MySQL/Postgres.
    _URI = os.getenv("DATABASE_URL", _DEFAULT_URL).split("?", 1)[0]
    SQLALCHEMY_ENGINE_OPTIONS = (
        {}
        if _URI.startswith("sqlite")
        else {
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
            "pool_pre_ping": True,
        }
    )

    # Security
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))

    # Session / cookie security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() in (
        "1", "true", "yes",
    )
    PERMANENT_SESSION_LIFETIME = int(os.getenv("SESSION_LIFETIME_SECONDS", "3600"))
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    # Business rules
    EXPIRY_ALERT_DAYS = int(os.getenv("EXPIRY_ALERT_DAYS", "30"))
    REORDER_SAFETY_FACTOR = float(os.getenv("REORDER_SAFETY_FACTOR", "1.5"))

    # Presentation / Static paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "presentation", "static", "uploads")
    STATIC_FOLDER = os.path.join(BASE_DIR, "presentation", "static")
    TEMPLATES_FOLDER = os.path.join(BASE_DIR, "presentation", "templates")


def is_sqlite(db_uri: str = None) -> bool:
    """Return True when the configured database is SQLite."""
    uri = (db_uri or Config.SQLALCHEMY_DATABASE_URI).split("?", 1)[0]
    return uri.startswith("sqlite")
