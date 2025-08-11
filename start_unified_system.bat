@echo off
echo ========================================
echo    FIXORA PRO Unified API System
echo ========================================
echo.

echo Starting FIXORA PRO with Unified API System...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Starting unified system...
echo.

REM Set console encoding to UTF-8
chcp 65001 >nul

echo ========================================
echo UNIFIED API SYSTEM STARTING!
echo ========================================
echo.
echo The system is now using:
echo   - API-Football as PRIMARY data source
echo   - SportMonks as FALLBACK data source
echo   - Automatic failover when primary fails
echo.
echo Interactive Telegram bot is also running!
echo Users can send messages to @Percentvaluebot
echo.
echo Press Ctrl+C to stop the system
echo ========================================

REM Start the unified system
python main_realtime.py

echo.
echo System stopped. Press any key to exit...
pause >nul
