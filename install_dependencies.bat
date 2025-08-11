@echo off
echo ========================================
echo   FIXORA PRO - Dependency Installer
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Checking version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8+ is required
    echo Current version:
    python --version
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation Completed Successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit config.py with your API keys
echo 2. Run start_unified_system.bat to start the system
echo 3. Or run start_interactive_bot.bat for bot only
echo.
echo Press any key to exit...
pause >nul
