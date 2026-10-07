#!/bin/bash
# Build script for macOS and Linux
# Usage: ./build.sh [--portable]

echo "================================================"
echo "  Almacén Digital - Unix Build"
echo "================================================"
echo ""

# Detect OS
OS=$(uname -s)
echo "Detected OS: $OS"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install/update PyInstaller
echo "Installing PyInstaller..."
python3 -m pip install --upgrade pyinstaller

# Run build script with arguments
echo ""
if [ "$1" = "--portable" ]; then
    echo "Building PORTABLE version..."
    python3 build.py --portable
else
    echo "Building REGULAR version..."
    python3 build.py
fi

echo ""
echo "================================================"
echo "  Build process completed!"
echo "================================================"
echo ""
echo "To build portable version: ./build.sh --portable"
