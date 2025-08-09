# 🚀 FIXORA PRO - Quick Setup Guide

## 🎯 Super Simple Setup (5 Minutes)

### Step 1: Install Everything
Double-click `install.bat` and wait for it to finish.

### Step 2: Get Your API Key
1. Go to: https://dashboard.api-football.com
2. Sign up for free account
3. Copy your API key

### Step 3: Get Your Telegram Bot
1. Open Telegram
2. Search for "@BotFather"
3. Send: `/newbot`
4. Follow instructions
5. Copy the bot token

### Step 4: Configure the System
1. Open `config.py` in Notepad
2. Replace these lines:
   ```python
   API_FOOTBALL_KEY = "YOUR_API_KEY_HERE"
   TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```
3. Save the file

### Step 5: Test Everything
```bash
python test_api_config.py
```

### Step 6: Start Using!

**For Daily Updates:**
```bash
python main.py
```

**For Real-Time (Recommended):**
```bash
python start_realtime.py
```

---

## 📱 Telegram Setup

1. Find your bot in Telegram
2. Send: `/setchat`
3. You're done! 🎉

---

## ❓ Need Help?

- Check the main README.md file
- Make sure your API account is not suspended
- Verify your bot token is correct

---

**That's it! You're ready to start betting analysis! 🚀**
