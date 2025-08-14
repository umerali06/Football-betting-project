# 🚀 QUICK START GUIDE - FIXORA PRO

## ⚡ **Get Running in 5 Minutes!**

### 📋 **Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

### 🔑 **Step 2: Configure API Keys**
```bash
# Copy config template
cp config_template.py config.py

# Edit config.py with your keys:
# - SPORTMONKS_API_TOKEN
# - API_FOOTBALL_KEY  
# - TELEGRAM_BOT_TOKEN
```

### 🚀 **Step 3: Start the Bot**
```bash
# Start progressive analysis bot
python start_bot.py
```

### 📱 **Step 4: Use in Telegram**
- Find your bot in Telegram
- Send `/start` to begin
- Use `/analyze` for progressive match analysis
- Use `/live` for live match analysis

## 🎯 **What You'll Experience**

### ✨ **Progressive Results (NEW!)**
- **First batch (8 matches)**: Appears in ~30 seconds
- **Continuous updates**: Each batch as it's ready
- **Progress tracking**: Real-time completion status
- **Cool messages**: Interactive processing updates

### 📊 **Analysis Features**
- **H2H Predictions**: Win/Draw/Win using xG + Elo
- **BTTS Analysis**: Both teams to score predictions
- **Goals Analysis**: Over/Under 2.5, 3.5 goals
- **Corners Analysis**: Total corners predictions

## 🔧 **Troubleshooting**

### ❌ **Bot Not Working?**
```bash
# Test network connectivity
python test_network.py

# Test bot functionality  
python test_telegram_bot_comprehensive.py

# Check bot status
/status command in Telegram
```

### 🌐 **Network Issues?**
- Use `/network` command in bot
- Check firewall/proxy settings
- Try VPN if regional restrictions
- Verify internet connection

## 📚 **Need More Info?**

- **Full Documentation**: See `README.md`
- **Commands**: Use `/help` in bot
- **Status**: Use `/status` in bot
- **Support**: Check GitHub issues

---

**🎉 Ready to go? Run `python start_bot.py` and enjoy progressive football analysis!**
