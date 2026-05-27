#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Starting ST Platform API on http://localhost:8000 ..."
PYTHONPATH=src python3 -m uvicorn st_platform.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
