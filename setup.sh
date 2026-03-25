#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -d ".venv" ]; then
	python3 -m venv .venv
fi

./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install Flask

export FLASK_APP=app
./.venv/bin/flask run --debug
