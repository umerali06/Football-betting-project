# 🚀 FIXORA PRO - Real-Time Football Betting Monitor

## Overview

This is a **real-time football betting monitor** that continuously fetches live data from the API and updates the bot dynamically. The system:

- ✅ **Fetches real-time data** from API Football
- ✅ **Analyzes matches dynamically** as they become available
- ✅ **Posts value bets instantly** to Telegram
- ✅ **No mock data** - only real API data
- ✅ **Continuous monitoring** - checks every 5 minutes
- ✅ **Automatic updates** - no manual intervention needed

## 🎯 How It Works

### Real-Time Flow:
1. **Continuous Monitoring**: System checks for new matches every 5 minutes
2. **Live Data Fetching**: Gets real-time match data, odds, and team form
3. **Dynamic Analysis**: Analyzes each match using multiple models (Elo + xG + Corners)
4. **Value Bet Detection**: Identifies bets where model probability > bookmaker odds
5. **Instant Notifications**: Posts value bets to Telegram immediately
6. **No Duplicates**: Tracks analyzed matches to avoid re-analyzing

### When No Matches Available:
- System shows "No matches available at the moment"
- Continues monitoring in background
- Automatically detects when new matches become available

## 🚀 Quick Start

### 1. Setup API Key
Make sure your API key is set in `config.py`:
```python
API_FOOTBALL_KEY = "your_api_key_here"
```

### 2. Setup Telegram Bot
Make sure your Telegram bot token is set in `config.py`:
```python
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
```

### 3. Start Real-Time Monitor
```bash
python start_realtime.py
```

### 4. Set Chat ID
When the system starts, send `/setchat` to your Telegram bot to set up notifications.

## 📊 System Features

### Real-Time Monitoring
- **Check Interval**: Every 5 minutes
- **Match Range**: Today + 3 days ahead
- **League Coverage**: Major leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
- **Duplicate Prevention**: Tracks analyzed matches

### Live Data Analysis
- **Match Data**: Real-time fixtures and schedules
- **Team Form**: Recent match history and performance
- **Live Odds**: Current bookmaker odds
- **Statistics**: Match statistics when available

### Multi-Model Predictions
- **Elo Ratings**: Team strength and historical performance
- **Expected Goals (xG)**: Goal-scoring probability analysis
- **Corners Model**: Corner kick predictions
- **Combined Analysis**: Weighted predictions from all models

### Value Bet Detection
- **Edge Calculation**: Model probability vs bookmaker odds
- **Threshold**: 8% edge required for premium analysis
- **Risk Management**: Kelly Criterion and bankroll management
- **Confidence Scoring**: Model confidence assessment

## 🔧 Configuration

### Check Interval
Modify the check interval in `realtime_monitor.py`:
```python
self.check_interval = 300  # Check every 5 minutes (300 seconds)
```

### Supported Markets
The system analyzes these betting markets:
- **Match Result**: Home Win / Draw / Away Win
- **Both Teams to Score**: Yes / No
- **Over/Under Goals**: Various goal lines
- **Corners**: Total corners over/under

### Value Bet Threshold
Adjust the threshold in `config.py`:
```python
VALUE_BET_THRESHOLD = 0.08  # 8% edge required
```

## 📱 Telegram Notifications

### Startup Message
When the system starts, you'll receive:
```
🚀 Real-Time Betting Monitor Started!

✅ System is now running and monitoring for new matches
🔄 Checking every 5 minutes for new matches
💎 Value bets will be posted automatically when found
```

### Value Bet Notifications
When value bets are found:
```
🎯 PREMIUM VALUE BETS FOUND!

📊 Analysis Summary:
• Total Value Bets: 3
• Average Edge: 12.5%
• Average Confidence: 78.2%

1. ⚽ Manchester United vs Liverpool
   🎯 Match Result - Home Win
   📊 Odds: 2.15
   📈 Edge: 15.2%
   🎯 Confidence: 82.1%
   💰 Kelly %: 8.5%
   💵 Recommended: £25.00
   ⚠️ Risk Score: 0.234
```

### No Matches Message
When no matches are available:
```
🔍 No Matches Found

Currently no matches available for analysis.
The system will automatically check again in 5 minutes.
```

## 🛠️ Troubleshooting

### API Issues
If you see API errors:
1. Check your API key in `config.py`
2. Verify your API account status at https://dashboard.api-football.com
3. Ensure your subscription is active

### Telegram Issues
If Telegram notifications aren't working:
1. Check your bot token in `config.py`
2. Send `/setchat` to your bot in Telegram
3. Verify the bot has permission to send messages

### No Value Bets
If no value bets are found:
1. This is normal - value bets require significant edge
2. System will continue monitoring for new opportunities
3. Check the threshold setting in `config.py`

## 📈 Performance Monitoring

### Log Files
- `realtime_system.log`: Real-time system logs
- `betting_system.log`: General system logs

### Key Metrics
- Matches analyzed per day
- Value bets found
- Average edge percentage
- System uptime

## 🔄 System Commands

### Start Real-Time Monitor
```bash
python start_realtime.py
```

### Test System
```bash
python test_realtime.py
```

### Stop System
Press `Ctrl+C` to stop the monitor gracefully.

## 📞 Support

If you encounter issues:
1. Check the log files for error messages
2. Verify your API and Telegram configurations
3. Ensure your API account is active and has sufficient credits

## 🎯 Success Indicators

Your real-time system is working correctly when you see:
- ✅ "Real-Time Betting Monitor Started!" message in Telegram
- ✅ Regular "Checking for new matches" log messages
- ✅ Value bet notifications when opportunities are found
- ✅ "No matches" messages when no opportunities exist
- ✅ Continuous operation without errors

---

**🚀 Your real-time betting monitor is now ready to find value bets automatically!**
