#!/usr/bin/env bash
set -euo pipefail

# Запуск тестов (pytest). Использует виртуальное окружение `.venv` если оно есть.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PY="$ROOT_DIR/.venv/bin/python"

if [ -x "$VENV_PY" ]; then
  echo "Running tests with venv python: $VENV_PY"
  "$VENV_PY" -m pytest -q
else
  echo "No .venv detected, running system pytest (python3 -m pytest)"
  python3 -m pytest -q
fi
