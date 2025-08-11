@echo off
echo ========================================
echo    FIXORA PRO Enhanced Startup Script
echo ========================================
echo.

echo Starting FIXORA PRO Real-Time Football Analysis System...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Starting system...
echo.

REM Start the enhanced real-time system
python main_realtime.py

echo.
echo System stopped. Press any key to exit...
pause >nul
