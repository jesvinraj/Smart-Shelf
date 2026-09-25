#!/bin/sh
set -e

echo "[SmartShelf] waiting for the database..."
python - <<'PY'
import os
import time

dsn = os.environ.get("DATABASE_URL", "")
if not dsn.startswith("mysql"):
    print("non-MySQL backend: skipping database wait")
    raise SystemExit(0)

from urllib.parse import urlparse  # noqa: E402

import pymysql  # noqa: E402

p = urlparse(dsn.replace("mysql+pymysql", "mysql", 1))
for _ in range(60):
    try:
        conn = pymysql.connect(
            host=p.hostname,
            port=p.port or 3306,
            user=p.username,
            password=p.password,
            database=(p.path or "/").lstrip("/"),
        )
        conn.close()
        print("database is up")
        raise SystemExit(0)
    except Exception:
        time.sleep(1)
print("database never became ready; continuing anyway")
PY

echo "[SmartShelf] applying schema..."
flask --app app init-db

if [ "${SEED_DEMO:-false}" = "true" ]; then
    echo "[SmartShelf] seeding demo data..."
    flask --app app seed || echo "[SmartShelf] seed skipped (already seeded)"
fi

echo "[SmartShelf] starting gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --threads "${GUNICORN_THREADS:-4}" \
    --timeout 60 \
    app:app