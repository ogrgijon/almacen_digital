@echo off
REM Build script for Windows
REM Usage: build.bat [--portable]
echo ================================================
echo   Almacen Digital - Windows Build
echo ================================================
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Run build script with arguments
echo.
echo Starting build process...
if "%1"=="--portable" (
    echo Building PORTABLE version...
    python build.py --portable
) else (
    echo Building REGULAR version...
    python build.py
)

echo.
echo ================================================
echo   Build process completed!
echo ================================================
echo.
echo To build portable version: build.bat --portable
pause
