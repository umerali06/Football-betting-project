@echo off
echo ========================================
echo FIXORA PRO - Real-Time Betting System
echo ========================================
echo.
echo Starting real-time football analysis...
echo.
echo Features:
echo - Live match monitoring
echo - Real-time odds analysis
echo - Value bet detection
echo - Telegram notifications
echo - Risk assessment
echo.
echo Press Ctrl+C to stop the system
echo.
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo No virtual environment found, using system Python
)

REM Start the real-time system
python main_realtime.py

echo.
echo System stopped.
pause
