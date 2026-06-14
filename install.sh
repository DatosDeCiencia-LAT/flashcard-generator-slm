#!/usr/bin/env bash
set -e

echo ""
echo "========================================"
echo " Flashcard Generator - Installation"
echo "========================================"
echo ""

OS="$(uname -s)"

# ── 1. System dependencies ────────────────────────────────────────────────────

install_system_deps_linux() {
    echo ">>> Installing system dependencies (requires sudo)..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y python3 python3-pip python3-venv \
            libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
            libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
            libglib2.0-0 libsm6 libxrender1 libxext6
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip \
            cairo pango gdk-pixbuf2 libffi \
            glib2 libSM libXrender libXext
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy --noconfirm python python-pip \
            cairo pango gdk-pixbuf2 libffi
    else
        echo "WARNING: Could not detect package manager. Install these manually if WeasyPrint or EasyOCR fail:"
        echo "  libcairo2, libpango, libgdk-pixbuf2, libffi, libglib2, libSM, libXrender, libXext"
    fi
}

install_system_deps_mac() {
    if ! command -v brew &>/dev/null; then
        echo "ERROR: Homebrew is not installed."
        echo "Install it from https://brew.sh and then re-run this script."
        exit 1
    fi
    echo ">>> Installing system dependencies via Homebrew..."
    brew install cairo pango libffi gdk-pixbuf
}

case "$OS" in
    Linux)  install_system_deps_linux ;;
    Darwin) install_system_deps_mac ;;
    *)
        echo "ERROR: Unsupported OS: $OS"
        exit 1
        ;;
esac

echo "[OK] System dependencies installed"

# ── 2. Python check ───────────────────────────────────────────────────────────

PYTHON=""
for cmd in python3.10 python3.11 python3.12 python3; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3 not found after installation. Please install Python 3.10+ manually."
    exit 1
fi

echo "[OK] Using $($PYTHON --version)"

# ── 3. Virtual environment ────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo ">>> Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

echo "[OK] Virtual environment ready"

# ── 4. Install Python packages ────────────────────────────────────────────────

echo ""
echo ">>> Installing Python packages (this may take several minutes)..."
echo ""

"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "========================================"
echo " [OK] Installation complete!"
echo "========================================"
echo ""
echo "To launch the app, run:"
echo "  ./run.sh"
echo ""
