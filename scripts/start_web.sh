#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../web"
echo "Installing frontend dependencies ..."
npm install
echo "Starting Vite dev server on http://localhost:5173 ..."
npm run dev
