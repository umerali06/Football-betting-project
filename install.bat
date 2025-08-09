@echo off
echo.
echo ========================================
echo 🚀 FIXORA PRO - Installation Script
echo ========================================
echo.

echo 📦 Installing required packages...
pip install requests python-telegram-bot python-dotenv

echo.
echo ✅ Installation complete!
echo.
echo 📋 Next steps:
echo 1. Edit config.py with your API key and Telegram token
echo 2. Run: python test_api_config.py
echo 3. Start the system with: python start_realtime.py
echo.
echo Press any key to continue...
pause > nul
