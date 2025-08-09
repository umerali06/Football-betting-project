# 🚀 FIXORA PRO - Football Betting System

## 📋 Table of Contents
1. [What is FIXORA PRO?](#what-is-fixora-pro)
2. [Installation Guide](#installation-guide)
3. [Setup Guide](#setup-guide)
4. [How to Use](#how-to-use)
5. [Daily Updates vs Real-Time](#daily-updates-vs-real-time)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## 🎯 What is FIXORA PRO?

FIXORA PRO is an advanced football betting analysis system that:
- 📊 Analyzes football matches using AI models
- 💎 Finds value betting opportunities
- 📱 Sends notifications to your Telegram
- 🔄 Works in two modes: Daily Updates and Real-Time

### 🎮 Two Modes Available:

#### 1. **Daily Updates** (`main.py`)
- Runs once per day at 9:00 AM
- Analyzes all available matches
- Posts summary to Telegram
- Good for regular betting analysis

#### 2. **Real-Time Monitor** (`start_realtime.py`)
- Runs continuously 24/7
- Checks for new matches every 5 minutes
- Posts value bets instantly when found
- Perfect for live betting opportunities

---

## 🛠️ Installation Guide

### Step 1: Download and Extract
1. Download the project files
2. Extract to a folder (e.g., `G:\Projects\football-project`)
3. Open Command Prompt or PowerShell in that folder

### Step 2: Install Python
1. Download Python from: https://www.python.org/downloads/
2. Install Python (make sure to check "Add Python to PATH")
3. Verify installation:
   ```bash
   python --version
   ```

### Step 3: Install Required Packages
```bash
pip install requests python-telegram-bot python-dotenv
```

### Step 4: Verify Installation
```bash
python test_api_config.py
```

---

## ⚙️ Setup Guide

### Step 1: Get API Key
1. Go to: https://dashboard.api-football.com
2. Create an account
3. Get your API key
4. Make sure your account is active (not suspended)

### Step 2: Get Telegram Bot Token
1. Open Telegram
2. Search for "@BotFather"
3. Send: `/newbot`
4. Follow instructions to create a bot
5. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 3: Configure the System
1. Open `config.py` in a text editor
2. Replace the API key:
   ```python
   API_FOOTBALL_KEY = "YOUR_API_KEY_HERE"
   ```
3. Replace the Telegram token:
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```
4. Save the file

### Step 4: Test Configuration
```bash
python test_api_config.py
```
You should see: ✅ API is accessible

---

## 🚀 How to Use

### 🎯 Option 1: Daily Updates (Recommended for Beginners)

#### What it does:
- Analyzes matches once per day
- Posts summary to Telegram
- Good for regular betting analysis

#### How to run:
```bash
python main.py
```

#### What happens:
1. System starts and connects to API
2. Fetches today's matches
3. Analyzes each match
4. Posts results to Telegram
5. Stops automatically

#### Expected output:
```
🚀 FIXORA PRO - Daily Betting Analysis
✅ Found 15 matches for today
📊 Analyzing matches...
💎 Found 3 value bets
📱 Posted to Telegram
✅ Analysis complete!
```

---

### ⚡ Option 2: Real-Time Monitor (Advanced)

#### What it does:
- Runs continuously 24/7
- Checks for new matches every 5 minutes
- Posts value bets instantly when found
- Perfect for live betting

#### How to run:
```bash
python start_realtime.py
```

#### What happens:
1. System starts and shows menu
2. Type `y` to start
3. System runs continuously
4. Press `Ctrl+C` to stop

#### Expected output:
```
🚀 FIXORA PRO - Real-Time Football Betting Monitor
============================================================
📊 Features:
   • Real-time match monitoring
   • Live API data analysis
   • Automatic value bet detection
   • Instant Telegram notifications
   • No mock data - only real data
============================================================

Start real-time monitor? (y/n): y

🔄 Starting real-time monitor...
💡 Press Ctrl+C to stop the monitor
============================================================
🚀 Real-Time Betting Monitor Started!
✅ System is now running and monitoring for new matches
🔄 Checking every 5 minutes for new matches
```

---

## 📱 Telegram Setup

### Step 1: Find Your Bot
1. Open Telegram
2. Search for your bot name (the one you created)
3. Click on it

### Step 2: Set Chat ID
1. Send this command to your bot:
   ```
   /setchat
   ```
2. The bot will reply: "✅ Chat ID set to: [number]"

### Step 3: Test Notifications
1. Run the system (daily or real-time)
2. You should receive messages in Telegram

---

## 📊 Understanding the Output

### Daily Analysis Messages:
```
📊 Daily Betting Summary

🎯 Total Bets Analyzed: 15
💎 Value Bets Found: 3
📈 Average Edge: 12.5%
💰 Total ROI: 8.2%

📅 Next analysis scheduled for tomorrow.
```

### Real-Time Value Bet Messages:
```
🎯 PREMIUM VALUE BETS FOUND!

📊 Analysis Summary:
• Total Value Bets: 2
• Average Edge: 15.2%
• Average Confidence: 78.5%

1. ⚽ Manchester United vs Liverpool
   🎯 Match Result - Home Win
   📊 Odds: 2.15
   📈 Edge: 15.2%
   🎯 Confidence: 82.1%
   💰 Kelly %: 8.5%
   💵 Recommended: £25.00
```

### No Matches Message:
```
🔍 No Matches Found

Currently no matches available for analysis.
The system will automatically check again in 5 minutes.
```

---

## 🔧 Troubleshooting

### ❌ Problem: "API Errors: Your account is suspended"
**Solution:**
1. Go to https://dashboard.api-football.com
2. Log in to your account
3. Check subscription status
4. Reactivate if suspended
5. Ensure you have credits

### ❌ Problem: "Bot token is invalid"
**Solution:**
1. Check your bot token in `config.py`
2. Make sure you copied it correctly
3. Create a new bot if needed

### ❌ Problem: "No matches found"
**Solution:**
1. This is normal - not all days have matches
2. Check if your API account is active
3. Try running real-time monitor instead

### ❌ Problem: "Module not found"
**Solution:**
```bash
pip install requests python-telegram-bot python-dotenv
```

### ❌ Problem: "Telegram notifications not working"
**Solution:**
1. Send `/setchat` to your bot in Telegram
2. Make sure the bot has permission to send messages
3. Check your internet connection

---

## ❓ FAQ

### Q: Which mode should I use?
**A:** 
- **Beginners**: Start with Daily Updates (`python main.py`)
- **Advanced users**: Use Real-Time Monitor (`python start_realtime.py`)

### Q: How often does it check for matches?
**A:** 
- **Daily mode**: Once per day at 9:00 AM
- **Real-time mode**: Every 5 minutes

### Q: What are value bets?
**A:** Value bets are when the system's prediction is better than the bookmaker's odds by 8% or more.

### Q: How do I stop the real-time monitor?
**A:** Press `Ctrl+C` in the terminal.

### Q: Can I change the check interval?
**A:** Yes, edit `realtime_monitor.py` and change `self.check_interval = 300` (300 seconds = 5 minutes).

### Q: What if I don't get any value bets?
**A:** This is normal! Value bets require significant edge. The system will continue monitoring and notify you when opportunities arise.

---

## 📁 File Structure

```
football-project/
├── README.md                 # This guide
├── config.py                 # Configuration file
├── main.py                   # Daily analysis system
├── start_realtime.py         # Real-time monitor
├── realtime_monitor.py       # Real-time system core
├── test_api_config.py        # API testing
├── test_realtime.py          # System testing
├── api/
│   └── api_football.py       # API client
├── bot_interface/
│   └── telegram_bot.py       # Telegram bot
├── models/                   # Prediction models
├── betting/                  # Betting analysis
└── REALTIME_GUIDE.md         # Advanced real-time guide
```

---

## 🎯 Quick Start Checklist

- [ ] Python installed
- [ ] Packages installed (`pip install requests python-telegram-bot python-dotenv`)
- [ ] API key configured in `config.py`
- [ ] Telegram bot token configured in `config.py`
- [ ] API account active (not suspended)
- [ ] Chat ID set (`/setchat` command sent to bot)

### Ready to Start?

**For Daily Updates:**
```bash
python main.py
```

**For Real-Time Monitoring:**
```bash
python start_realtime.py
```

---

## 📞 Support

If you need help:
1. Check this README first
2. Look at the troubleshooting section
3. Check your API account status
4. Verify your Telegram bot setup

---

**🚀 Happy Betting with FIXORA PRO!**
