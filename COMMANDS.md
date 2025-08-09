# 🚀 FIXORA PRO - Command Reference

## 📦 Installation Commands

```bash
# Install packages
pip install requests python-telegram-bot python-dotenv

# Or use the installer
install.bat
```

## 🧪 Testing Commands

```bash
# Test API configuration
python test_api_config.py

# Test real-time system
python test_realtime.py
```

## 🚀 Running Commands

```bash
# Daily analysis (runs once, then stops)
python main.py

# Real-time monitor (runs continuously)
python start_realtime.py
```

## 📱 Telegram Commands

Send these to your bot in Telegram:
```
/start     - Start the bot
/help      - Show help
/status    - Check bot status
/setchat   - Set chat ID for notifications
```

## 🛑 Stopping Commands

```bash
# Stop real-time monitor
Ctrl + C

# Stop any running process
Ctrl + C
```

## 🔧 Configuration Files

- `config.py` - Main configuration (API keys, settings)
- `telegram_chat_id.txt` - Saved chat ID (auto-created)

## 📊 Log Files

- `betting_system.log` - System logs
- `realtime_system.log` - Real-time logs

---

## 🎯 Quick Start Sequence

1. `install.bat` (or `pip install requests python-telegram-bot python-dotenv`)
2. Edit `config.py` with your API key and bot token
3. `python test_api_config.py`
4. Send `/setchat` to your Telegram bot
5. `python start_realtime.py`

---

**💡 Tip: Use `python start_realtime.py` for continuous real-time updates!**
