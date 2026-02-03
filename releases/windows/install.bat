@echo off
title R.E.X. Installer for Windows

echo [INFO] Starting R.E.X. Installation...
echo ========================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from python.org and try again.
    pause
    exit /b 1
)

:: 2. Check Node
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERR] Node.js is not installed or not in PATH.
    echo Please install Node.js 18+ from nodejs.org and try again.
    pause
    exit /b 1
)

:: 3. Setup Python Backend
echo [INFO] Setting up Python Environment...
if not exist "venv" (
    echo     Running: python -m venv venv
    python -m venv venv
)

echo     Activating venv...
call venv\Scripts\activate.bat

echo     Installing Requirements...
pip install -r requirements.txt

:: 4. Setup Node Frontend
echo [INFO] Setting up Node.js Frontend...
call npm install

echo ========================================
echo [SUCCESS] Installation Complete!
echo You can now run R.E.X. using: start_rex.bat
pause
