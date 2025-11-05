#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN=${PYTHON:-python3}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: Could not find Python executable '$PYTHON_BIN'." >&2
  echo "Set the PYTHON environment variable to the desired interpreter before running this script." >&2
  exit 1
fi

if [ -d "$VENV_DIR" ]; then
  echo "Virtual environment already exists at $VENV_DIR"
else
  echo "Creating virtual environment with $PYTHON_BIN at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

if ! python -m pip install --upgrade pip; then
  echo "Warning: Unable to upgrade pip. Check your internet connection or proxy settings." >&2
fi

REQ_FILE="${ROOT_DIR}/backend/requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "Installing backend requirements from $REQ_FILE"
  if ! pip install -r "$REQ_FILE"; then
    echo "Warning: Failed to install dependencies from $REQ_FILE. You may need to install them manually." >&2
  fi
else
  echo "No backend requirements file found at $REQ_FILE"
fi

echo
echo "Virtual environment ready. Activate it with:"
echo "  source .venv/bin/activate"
