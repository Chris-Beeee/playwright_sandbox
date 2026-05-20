@echo off
echo ===================================================
echo  Playwright Sandbox - Environment Setup
echo ===================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

:: 2. Create virtual environment if it doesn't exist
if not exist .venv (
    echo [1/4] Creating virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment (.venv) already exists. Skipping creation.
)

:: 3. Activate virtual environment and upgrade pip/setuptools
echo [2/4] Activating virtual environment and upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel >nul

:: 4. Install requirements
if exist requirements.txt (
    echo [3/4] Installing Python requirements from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install requirements.
        pause
        exit /b 1
    )
) else (
    echo [WARNING] requirements.txt not found. Skipping dependency installation.
)

:: 5. Install Playwright browser binaries
echo [4/4] Installing Playwright browser binaries (Chromium, Firefox, WebKit)...
playwright install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Playwright browser binaries.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo  Setup Completed Successfully!
echo ===================================================
echo.
echo To run your tests:
echo   1. Activate the virtual environment:
echo      .venv\Scripts\activate
echo   2. Run pytest:
echo      pytest --headed
echo.
pause
