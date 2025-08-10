# 🚀 FIXORA PRO - Complete Setup Guide

A step-by-step guide to get your football betting analysis system up and running.

## 📋 Prerequisites Checklist

Before you start, make sure you have:

- [ ] **Python 3.8 or higher** installed
- [ ] **Internet connection** for API access
- [ ] **SportMonks API account** (optional for testing)
- [ ] **Telegram account** for notifications
- [ ] **Basic command line knowledge**

## 🐍 Step 1: Install Python

### Windows Users:
1. Go to [python.org/downloads](https://python.org/downloads)
2. Download Python 3.8+ (latest stable version)
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```bash
   python --version
   ```

### macOS Users:
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
```

### Linux Users:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

## 📦 Step 2: Install Dependencies

### Option A: Using the Installation Script (Windows)
1. Double-click `install.bat`
2. Wait for installation to complete
3. Follow the on-screen instructions

### Option B: Manual Installation
```bash
# Navigate to project directory
cd football-project

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🔑 Step 3: Get API Keys

### SportMonks API (Optional for Testing)
1. Go to [my.sportmonks.com](https://my.sportmonks.com)
2. Create a free account
3. Get your API token from the dashboard
4. Note: Free tier has limited requests per day

### Telegram Bot Token
1. Open Telegram app
2. Search for "@BotFather"
3. Send `/newbot` command
4. Follow instructions to create your bot
5. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## ⚙️ Step 4: Configure the System

1. **Open `config.py`** in any text editor
2. **Update the configuration**:

```python
# API Configuration
SPORTMONKS_API_TOKEN = "your_sportmonks_token_here"
SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3"

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"

# Betting Parameters (adjust as needed)
VALUE_BET_THRESHOLD = 0.05  # 5% edge required
MIN_ODDS = 1.5               # Minimum odds to consider
MAX_ODDS = 10.0              # Maximum odds to consider
CONFIDENCE_THRESHOLD = 0.6   # Minimum confidence for bets
```

3. **Save the file**

## 🆔 Step 5: Get Your Telegram Chat ID

1. **Start a chat** with your bot in Telegram
2. **Send any message** to the bot
3. **Run this command** in your project directory:
   ```bash
   python -c "
   import requests
   bot_token = 'YOUR_BOT_TOKEN_HERE'
   response = requests.get(f'https://api.telegram.org/bot{bot_token}/getUpdates')
   updates = response.json()
   if updates['ok'] and updates['result']:
       chat_id = updates['result'][0]['message']['chat']['id']
       print(f'Your Chat ID is: {chat_id}')
   else:
       print('No messages found. Send a message to your bot first.')
   "
   ```
4. **Copy the Chat ID** and update `config.py`

## 🧪 Step 6: Test Your Setup

### Test API Connection:
```bash
python -c "
import requests
from config import SPORTMONKS_API_TOKEN, SPORTMONKS_BASE_URL

try:
    response = requests.get(f'{SPORTMONKS_BASE_URL}/core/countries', 
                           params={'api_token': SPORTMONKS_API_TOKEN})
    if response.status_code == 200:
        print('✅ SportMonks API connection successful!')
    else:
        print(f'❌ API Error: {response.status_code}')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### Test Telegram Bot:
```bash
python -c "
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

try:
    message = '🚀 FIXORA PRO is working!'
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print('✅ Telegram bot working! Check your Telegram.')
    else:
        print(f'❌ Telegram Error: {response.status_code}')
except Exception as e:
    print(f'❌ Telegram test failed: {e}')
"
```

## 🚀 Step 7: Run the System

### Option A: Using Startup Script (Windows)
1. Double-click `start.bat`
2. The system will start automatically
3. Press `Ctrl+C` to stop

### Option B: Manual Start
```bash
# Navigate to project directory
cd football-project

# Activate virtual environment (if using one)
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Start the system
python main.py
```

## 📱 Step 8: Telegram Bot Commands

Once running, interact with your bot:

- `/start` - Initialize the system
- `/status` - Check system status
- `/analyze` - Run manual analysis
- `/help` - Show available commands

## 🔍 Step 9: Verify Everything Works

### Expected Output:
```
🚀 FIXORA PRO - Football Betting Analysis System
================================================

📊 Starting daily analysis...
🔍 Fetching today's fixtures...
✅ Found 15 matches for analysis
📈 Generating predictions...
💰 Analyzing odds for value bets...
💎 Found 3 value bets
📱 Posted to Telegram successfully
✅ Daily analysis complete!
```

### Check Telegram:
You should receive messages like:
```
📊 Daily Betting Summary

🎯 Total Bets Analyzed: 15
💎 Value Bets Found: 3
📈 Average Edge: 12.5%
💰 Total ROI: 8.2%
```

## 🚨 Troubleshooting Common Issues

### ❌ "Module not found" Error
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install individually
pip install requests python-telegram-bot python-dotenv
```

### ❌ "API connection failed"
- Check your SportMonks API token
- Verify your account is active
- Check internet connection
- System will use mock data as fallback

### ❌ "Telegram bot not responding"
- Verify bot token is correct
- Check chat ID is set correctly
- Ensure bot has permission to send messages
- Try sending `/start` to your bot first

### ❌ "No matches found"
- This is normal - not all days have matches
- Check if your API account is active
- System will continue monitoring

## 📚 Next Steps

### Learn More:
- Read the main `README.md` for detailed information
- Check `config.py` for all available settings
- Explore the code structure in each directory

### Customization:
- Adjust betting parameters in `config.py`
- Modify prediction models in `models/` directory
- Customize risk management in `betting/` directory

### Advanced Features:
- Set up automated scheduling
- Configure multiple Telegram chats
- Add custom betting strategies
- Integrate with other data sources

## 🆘 Need Help?

If you encounter issues:

1. **Check the logs** in `betting_system.log`
2. **Verify configuration** in `config.py`
3. **Test individual components** using the test scripts above
4. **Check your API account status** on SportMonks
5. **Ensure all dependencies are installed**

---

**🎯 You're now ready to start analyzing football matches with AI!**

**Happy betting with FIXORA PRO! 🚀⚽**
