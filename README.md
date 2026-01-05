cat > run_dev.sh <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

# ---------- Config ----------
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
VENV_DIR="$BACKEND_DIR/venv"
LOG_DIR=".logs"

# Celery pool:
# - "solo" is safest across environments (including Windows dev setups). [web:30]
# - On Linux/macOS you can switch to: export CELERY_POOL=prefork
CELERY_POOL="${CELERY_POOL:-solo}"

# ---------- Helpers ----------
die() { echo "ERROR: $*" >&2; exit 1; }
has() { command -v "$1" >/dev/null 2>&1; }

mkdir -p "$LOG_DIR"

# ---------- Validate folders ----------
[[ -d "$BACKEND_DIR" ]]  || die "Missing ./backend folder"
[[ -d "$FRONTEND_DIR" ]] || die "Missing ./frontend folder"
[[ -f "$BACKEND_DIR/requirements.txt" ]] || die "Missing backend/requirements.txt"
[[ -f "$BACKEND_DIR/app.py" ]] || die "Missing backend/app.py"
[[ -f "$FRONTEND_DIR/package.json" ]] || die "Missing frontend/package.json"

# ---------- Check prerequisites ----------
has python3 || has python || die "Python not found (install Python 3.x)"
has npm || die "npm not found (install Node.js + npm)"

PY_BIN="python3"
has python3 || PY_BIN="python"

# ---------- Backend setup ----------
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating Python venv..."
  "$PY_BIN" -m venv "$VENV_DIR"
fi

PIP_BIN="$VENV_DIR/bin/pip"
PY_VENV="$VENV_DIR/bin/python"
CELERY_BIN="$VENV_DIR/bin/celery"

[[ -x "$PIP_BIN" ]] || die "pip not found in venv (venv broken?)"
[[ -x "$PY_VENV" ]] || die "python not found in venv (venv broken?)"

echo "Installing backend dependencies..."
"$PIP_BIN" install -r "$BACKEND_DIR/requirements.txt" >"$LOG_DIR/pip_install.log" 2>&1 || {
  echo "Backend install failed. Check $LOG_DIR/pip_install.log"
  exit 1
}

# ---------- Frontend setup ----------
echo "Installing frontend dependencies..."
( cd "$FRONTEND_DIR" && npm install >"../$LOG_DIR/npm_install.log" 2>&1 ) || {
  echo "Frontend install failed. Check $LOG_DIR/npm_install.log"
  exit 1
}

# ---------- Start services ----------
PIDS=()

cleanup() {
  echo ""
  echo "Stopping services..."
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT INT TERM

# Redis (default port is 6379) [web:32]
echo "Starting Redis (if not already running)..."
if has redis-cli && redis-cli ping >/dev/null 2>&1; then
  echo "Redis already running."
else
  if has redis-server; then
    redis-server --port 6379 >"$LOG_DIR/redis.log" 2>&1 &
    PIDS+=("$!")
    sleep 1
  else
    echo "Redis not found. Install Redis or start it manually, then re-run."
    exit 1
  fi
fi

# MailHog (HTTP UI default port 8025) [web:21]
echo "Starting MailHog..."
if has MailHog; then
  MailHog >"$LOG_DIR/mailhog.log" 2>&1 &
  PIDS+=("$!")
elif has mailhog; then
  mailhog >"$LOG_DIR/mailhog.log" 2>&1 &
  PIDS+=("$!")
else
  echo "MailHog binary not found in PATH. Install/run MailHog manually, then re-run."
  exit 1
fi

# Flask API
echo "Starting Flask API..."
( cd "$BACKEND_DIR" && "$PY_VENV" app.py >"../$LOG_DIR/flask.log" 2>&1 ) &
PIDS+=("$!")

# Celery Worker
echo "Starting Celery Worker (pool=$CELERY_POOL)..."
( cd "$BACKEND_DIR" && "$CELERY_BIN" -A app.celery worker --pool="$CELERY_POOL" --loglevel=info >"../$LOG_DIR/celery_worker.log" 2>&1 ) &
PIDS+=("$!")

# Celery Beat
echo "Starting Celery Beat..."
( cd "$BACKEND_DIR" && "$CELERY_BIN" -A app.celery beat --loglevel=info >"../$LOG_DIR/celery_beat.log" 2>&1 ) &
PIDS+=("$!")

# Vue Dev Server
echo "Starting Vue frontend..."
( cd "$FRONTEND_DIR" && npm run dev >"../$LOG_DIR/frontend.log" 2>&1 ) &
PIDS+=("$!")

echo ""
echo "All services started."
echo "UI:      http://localhost:5173"
echo "MailHog:  http://localhost:8025"
echo "Logs:    $LOG_DIR/"
echo ""
echo "Press Ctrl+C to stop everything."

wait
BASH

chmod +x run_dev.sh
./run_dev.sh
