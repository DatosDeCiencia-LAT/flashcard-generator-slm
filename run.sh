#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "ERROR: Virtual environment not found."
    echo "Please run ./install.sh first."
    exit 1
fi

echo "Starting Flashcard Generator..."
"$VENV_DIR/bin/python" "$SCRIPT_DIR/app.py"
