@echo off
REM Installation script for Almacén Digital on Windows
REM This script sets up the Python environment and installs dependencies

echo ========================================
echo  Almacén Digital - Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check Python version (basic check)
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.9 or higher is required
    echo Please upgrade Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully
echo.

echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

echo Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo ========================================
echo  Installation completed successfully!
echo ========================================
echo.
echo To run the application:
echo   1. Activate the virtual environment: .venv\Scripts\activate
echo   2. Run: python main.py
echo.
echo Or simply run: scripts\run.bat
echo.
pause
