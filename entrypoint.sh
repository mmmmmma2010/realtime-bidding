#!/usr/bin/env bash
set -e

# Simple wait-for for postgres and redis
host_is_up() {
  python - <<PY
import os,sys
import socket
host,port = os.environ.get('DB_WAIT_HOST','db').split(':') if ':' in os.environ.get('DB_WAIT_HOST','db:5432') else (os.environ.get('DB_WAIT_HOST','db'),5432)
try:
    s=socket.create_connection((host,int(port)),2)
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
}

echo "Waiting for services..."

# Wait for Postgres (retry)
for i in {1..30}; do
  if pg_isready -h ${DB_HOST:-db} -U ${POSTGRES_USER:-realtime}; then
    echo "Postgres is up"
    break
  fi
  echo "Waiting for Postgres... ($i)"
  sleep 2
done

# Optionally run migrations and collectstatic
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

# run passed command
exec "$@"