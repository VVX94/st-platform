#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
VENV=".venv-spagcn/bin/python"
if [ ! -f "$VENV" ]; then
  echo "ERROR: $VENV not found. Create it with: uv venv .venv-spagcn --python 3.11" >&2
  exit 1
fi
echo "Starting ST Platform API on http://localhost:8000 ..."
PYTHONPATH=src $VENV -m uvicorn st_platform.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
