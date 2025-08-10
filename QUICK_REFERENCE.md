# 🚀 FIXORA PRO - Quick Reference Guide

Quick commands and settings for daily use of your football betting analysis system.

## 🎯 Quick Start Commands

### Start the System
```bash
# Windows (double-click)
start.bat

# Manual start
python main.py

# With virtual environment
.venv\Scripts\activate  # Windows
python main.py
```

### Stop the System
- Press `Ctrl+C` in the terminal

## ⚙️ Configuration Quick Edit

### Edit Settings
```bash
# Open config file
notepad config.py  # Windows
nano config.py     # Linux/macOS
```

### Key Settings to Check
```python
# API Keys
SPORTMONKS_API_TOKEN = "your_token_here"
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"

# Betting Parameters
VALUE_BET_THRESHOLD = 0.05  # 5% edge required
MIN_ODDS = 1.5               # Minimum odds
MAX_ODDS = 10.0              # Maximum odds
CONFIDENCE_THRESHOLD = 0.6   # Minimum confidence
```

## 📱 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize the system |
| `/status` | Check system status |
| `/analyze` | Run manual analysis |
| `/odds <id>` | Get odds for match |
| `/predictions <id>` | Get model predictions |
| `/help` | Show all commands |

## 🔧 Common Tasks

### Check System Status
```bash
# View logs
tail -f betting_system.log  # Linux/macOS
type betting_system.log      # Windows

# Check Python version
python --version

# Check installed packages
pip list
```

### Install/Update Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Update specific package
pip install --upgrade requests

# Check for outdated packages
pip list --outdated
```

### Test API Connection
```bash
python -c "
import requests
from config import SPORTMONKS_API_TOKEN, SPORTMONKS_BASE_URL
response = requests.get(f'{SPORTMONKS_BASE_URL}/core/countries', 
                       params={'api_token': SPORTMONKS_API_TOKEN})
print('✅ API OK' if response.status_code == 200 else '❌ API Error')
"
```

### Test Telegram Bot
```bash
python -c "
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
data = {'chat_id': TELEGRAM_CHAT_ID, 'text': '🚀 Test message'}
response = requests.post(url, data=data)
print('✅ Telegram OK' if response.status_code == 200 else '❌ Telegram Error')
"
```

## 📊 Understanding Output

### System Messages
- `🚀 FIXORA PRO - Football Betting Analysis System` - System starting
- `📊 Starting daily analysis...` - Analysis beginning
- `🔍 Fetching today's fixtures...` - Getting match data
- `✅ Found X matches for analysis` - Matches found
- `💎 Found X value bets` - Value bets identified
- `📱 Posted to Telegram successfully` - Notifications sent
- `✅ Daily analysis complete!` - Analysis finished

### Value Bet Format
```
🎯 PREMIUM VALUE BETS FOUND!

📊 Analysis Summary:
• Total Value Bets: 2
• Average Edge: 15.2%
• Average Confidence: 78.5%

1. ⚽ Team A vs Team B
   🎯 Market: Match Result - Home Win
   📊 Odds: 2.15
   📈 Edge: 15.2%
   🎯 Confidence: 82.1%
   💰 Kelly %: 8.5%
   💵 Recommended: £25.00
```

## 🚨 Troubleshooting Quick Fixes

### Common Errors & Solutions

| Error | Quick Fix |
|-------|-----------|
| `Module not found` | `pip install -r requirements.txt` |
| `API connection failed` | Check token in `config.py` |
| `Telegram bot not responding` | Verify bot token and chat ID |
| `No matches found` | Normal - wait for matches |
| `Permission denied` | Run as administrator |

### Debug Mode
```python
# In config.py, change:
LOG_LEVEL = "DEBUG"  # Instead of "INFO"
```

### Reset System
```bash
# Stop system (Ctrl+C)
# Clear logs (optional)
del betting_system.log  # Windows
rm betting_system.log   # Linux/macOS
# Restart
python main.py
```

## 📁 File Locations

| File | Purpose | Location |
|------|---------|----------|
| `main.py` | Main application | Root directory |
| `config.py` | Settings | Root directory |
| `requirements.txt` | Dependencies | Root directory |
| `start.bat` | Windows startup | Root directory |
| `install.bat` | Windows install | Root directory |
| `betting_system.log` | Application logs | Root directory |
| `api_sportmonks.py` | API client | `api/` directory |
| `telegram_bot.py` | Bot interface | `bot_interface/` directory |

## 🔄 Daily Workflow

### Morning Setup
1. Check system status: `python main.py`
2. Monitor Telegram for daily summary
3. Review value bets found

### Throughout the Day
1. Check Telegram for new value bets
2. Monitor system logs if needed
3. Adjust settings if required

### Evening Review
1. Check final results in Telegram
2. Review system performance
3. Plan adjustments for tomorrow

## 📈 Performance Monitoring

### Key Metrics to Watch
- **Value Bets Found**: Should be 1-5 per day
- **Average Edge**: Should be 5-20%
- **Confidence Levels**: Should be 60%+
- **API Response Time**: Should be <5 seconds
- **Error Rate**: Should be <5%

### Log Analysis
```bash
# Search for errors
findstr "ERROR" betting_system.log  # Windows
grep "ERROR" betting_system.log     # Linux/macOS

# Search for value bets
findstr "value bet" betting_system.log  # Windows
grep "value bet" betting_system.log     # Linux/macOS
```

## 🆘 Emergency Contacts

### System Issues
1. Check logs first
2. Restart system
3. Verify configuration
4. Check internet connection

### API Issues
1. Verify SportMonks account status
2. Check API token validity
3. Monitor rate limits
4. System will use mock data as fallback

---

**💡 Pro Tip**: Keep this guide handy for quick reference during daily operations!

**Happy betting with FIXORA PRO! 🚀⚽**
