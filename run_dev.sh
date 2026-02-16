#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

# ---------- Config ----------
START_PORT=8000
HOST=127.0.0.1

# Activate the virtual environment
source marites-venv/bin/activate

# Install dependencies
pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# Install app package
pip install -e .

# ---------- Find free port ----------
PORT=$START_PORT
while lsof -i :"$PORT" >/dev/null 2>&1; do
  PORT=$((PORT + 1))
done

echo "Using free port: $PORT"

# ---------- Cleanup handler ----------
cleanup() {
  echo ""
  echo "Shutting down server..."
  if [[ -n "$UVICORN_PID" ]]; then
    kill "$UVICORN_PID" 2>/dev/null || true
  fi
  deactivate || true
  exit 0
}

trap cleanup INT TERM EXIT

# ---------- Wait for DB ----------
echo "Checking database connection..."

until alembic current >/dev/null 2>&1; do
  echo "Database not ready yet..."
  sleep 2
done

echo "Database is reachable."

# ---------- Check for alembic_version table ----------
echo "Checking alembic version
HAS_VERSION_TABLE=$(psql "$DATABASE_URL" -tAc "
  SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_name = 'alembic_version'
  );
")
echo "alembic version: $HAS_VERSION_TABLE"

if [ "$HAS_VERSION_TABLE" = "t" ]; then
  echo "Migration history table exists."
  echo "Upgrading to latest migration if needed..."
  alembic upgrade head
else
  echo "No migration history found."
  echo "Running full migration..."
  alembic upgrade head
fi

# ---------- Start server ----------
echo "Starting server..."
uvicorn app.main:app \
  --env-file .env \
  --reload \
  --host "$HOST" \
  --port "$PORT" &

UVICORN_PID=$!

# ---------- Wait ----------
wait "$UVICORN_PID"
