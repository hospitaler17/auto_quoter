#!/usr/bin/env bash
set -euo pipefail

# Запуск основного скрипта проекта (main.py).
# Если есть виртуальное окружение в `.venv`, используется оно, иначе — системный `python3`.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PY="$ROOT_DIR/.venv/bin/python"

if [ -f "$ROOT_DIR/.env" ]; then
  echo "Loading environment from .env"
  # shellcheck disable=SC1090
  set -a
  . "$ROOT_DIR/.env"
  set +a
fi

if [ -x "$VENV_PY" ]; then
  echo "Using venv python: $VENV_PY"
  "$VENV_PY" "$ROOT_DIR/main.py"
else
  echo "No .venv detected, using system python3"
  python3 "$ROOT_DIR/main.py"
fi
