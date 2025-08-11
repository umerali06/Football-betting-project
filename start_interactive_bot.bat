@echo off
echo ========================================
echo    FIXORA PRO Interactive Bot Startup
echo ========================================
echo.

echo Starting FIXORA PRO Interactive Telegram Bot...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Starting interactive bot...
echo.

REM Set console encoding to UTF-8
chcp 65001 >nul

echo ========================================
echo BOT STARTING - READY FOR USERS!
echo ========================================
echo.
echo The bot is now starting and will be interactive.
echo Users can send messages to @Percentvaluebot
echo and the bot will respond automatically.
echo.
echo Commands available:
echo   /start - Welcome message
echo   /help - Show help
echo   /status - Check bot status
echo   /analyze - Analyze today's matches
echo   /live - Show live matches
echo.
echo Press Ctrl+C to stop the bot
echo ========================================

REM Start the interactive bot
python test_bot.py

echo.
echo Bot stopped. Press any key to exit...
pause >nul
