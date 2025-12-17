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

# Ensure the src directory is in the PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src/app"

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

# ---------- Start server ----------
uvicorn main:app \
  --env-file dev.env \
  --reload \
  --host "$HOST" \
  --port "$PORT" &

UVICORN_PID=$!

# ---------- Wait ----------
wait "$UVICORN_PID"