#!/usr/bin/env bash
set -e

# Default port
WEB_PORT=${WEB_PORT:-8000}

echo "Waiting for services..."

# Wait for Postgres
for i in {1..30}; do
  if pg_isready -h ${DB_HOST:-db} -U ${POSTGRES_USER:-realtime}; then
    echo "Postgres is up"
    break
  fi
  echo "Waiting for Postgres... ($i)"
  sleep 2
done

# Wait for Redis
for i in {1..30}; do
  if nc -z ${REDIS_HOST:-redis} 6379; then
    echo "Redis is up"
    break
  fi
  echo "Waiting for Redis... ($i)"
  sleep 2
done

# Run migrations and collectstatic
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

# Run Daphne on specified port
exec daphne -b 0.0.0.0 -p "$WEB_PORT" realtime_bidding.asgi:application
