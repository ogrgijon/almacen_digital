#!/bin/bash
# Installation script for Almacén Digital on Unix-like systems (Linux/macOS)
# This script sets up the Python environment and installs dependencies

echo "========================================"
echo " Almacén Digital - Installation Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9 or higher:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  macOS: brew install python3"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

echo "Python found:"
python3 --version
echo ""

# Check Python version
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo "ERROR: Python 3.9 or higher is required"
    echo "Please upgrade Python"
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "Virtual environment created successfully"
echo ""

echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo "Virtual environment activated"
echo ""

echo "Upgrading pip..."
python -m pip install --upgrade pip
echo ""

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

echo "Compiling translations..."
python utils/compile_translations.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to compile translations"
    exit 1
fi
echo ""

echo "========================================"
echo " Installation completed successfully!"
echo "========================================"
echo ""
echo "To run the application:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Run: python main.py"
echo ""
echo "Or simply run: ./scripts/run.sh"
echo ""
