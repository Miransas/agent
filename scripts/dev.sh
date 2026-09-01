#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec uv run uvicorn app.server.api:app --reload --host 127.0.0.1 --port 8000
