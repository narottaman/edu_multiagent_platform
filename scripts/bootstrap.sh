#!/usr/bin/env sh
set -eu
[ -f .env ] || cp .env.example .env
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev,ui]'
echo "Ready. Run: make test && make run"
