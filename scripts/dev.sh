#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d backend/.venv ]]; then
  python3 -m venv backend/.venv
  backend/.venv/bin/pip install -r backend/requirements.txt
fi
if [[ ! -d frontend/node_modules ]]; then
  (cd frontend && npm install)
fi

cleanup() {
  if [[ -n "${API_PID:-}" ]]; then
    kill "$API_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

(cd backend && "$ROOT/backend/.venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port 8000) &
API_PID=$!
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
