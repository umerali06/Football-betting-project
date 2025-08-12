# 🚀 Quick Setup Guide - FIXORA PRO

Get your football betting analysis system running in 5 minutes!

## ⚡ Super Quick Start

### 1. Install Dependencies (Choose your OS)

#### Windows
```bash
# Double-click this file:
install_dependencies.bat
```

#### Linux/Mac
```bash
# Run this command:
./install_dependencies.sh
```

### 2. Configure API Keys
Edit `config.py` and add your keys:
```python
API_FOOTBALL_API_KEY = "your_api_football_key"
SPORTMONKS_API_KEY = "your_sportmonks_key"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
```

### 3. Start the System

#### Full System (Recommended)
```bash
# Windows
start_unified_system.bat

# Linux/Mac
python main_realtime.py
```

#### Bot Only
```bash
# Windows
start_interactive_bot.bat

# Linux/Mac
python bot_interface/telegram_bot.py
```

## 🔑 Getting API Keys

### API-Football (Primary)
1. Go to [api-sports.io](https://api-sports.io)
2. Sign up → Football API → Get your key

### SportMonks (Fallback)
1. Go to [sportmonks.com](https://sportmonks.com)
2. Sign up → Get your API token

### Telegram Bot
1. Message [@BotFather](https://t.me/botfather)
2. `/newbot` → Follow instructions → Get token

## 📱 Using the Bot

1. Start the system
2. Find your bot on Telegram
3. Send `/start`
4. Use commands: `/help`, `/analyze`, `/live`

## ❗ Common Issues

### "Module not found"
```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### "API access denied"
- Normal for free plans
- System continues working with available data
- Upgrade plan for more features

### Bot not responding
- Check bot token in config.py
- Ensure system is running
- Check internet connection

## 🎯 What You Get

- ✅ **Real-time match analysis**
- ✅ **Live odds and predictions**
- ✅ **Value betting opportunities**
- ✅ **Interactive Telegram bot**
- ✅ **Dual API system** (automatic fallback)

## 🆘 Need Help?

- 📖 Read the full [README.md](README.md)
- 🐛 Check [troubleshooting section](README.md#troubleshooting)
- 💬 Open an issue on GitHub

---

**Happy Betting Analysis! ⚽🎯**
