#!/bin/bash

# Install script for graphics/python
# Creates a virtual environment and installs required dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "Creating virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR"

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "Done! Virtual environment created at: $VENV_DIR"
echo ""
echo "To activate the environment, run:"
echo "  source $VENV_DIR/bin/activate"
