# 🚀 FIXORA PRO - Unified API Football Betting Analysis System

A real-time football betting analysis system that combines **API-Football** (primary) and **SportMonks** (fallback) to provide comprehensive match analysis, odds, predictions, and value betting opportunities.

## ✨ Features

### 🔄 **Dual API System**
- **Primary**: API-Football (api-sports.io) - High-quality data, extensive coverage
- **Fallback**: SportMonks - Reliable backup when primary API is unavailable
- **Automatic Failover**: Seamless switching between APIs
- **Provider-Aware**: Each fixture knows its source for consistent data fetching

### 📊 **Real-Time Analysis**
- **Live Match Analysis**: Real-time updates during matches
- **Comprehensive Data**: Fixtures, odds, team form, predictions, expected goals
- **Quality Indicators**: Basic/Moderate/Comprehensive analysis based on available data
- **Graceful Degradation**: Works with both free and subscription plans

### 🤖 **Interactive Telegram Bot**
- **Multi-User Support**: Works for all users, not just specific chat IDs
- **Command Interface**: `/start`, `/help`, `/status`, `/analyze`, `/live`
- **Natural Language**: Responds to text messages and commands
- **Real-Time Updates**: Live match information and analysis

### 🎯 **Betting Analysis**
- **Value Betting**: Identify opportunities based on odds and predictions
- **Risk Assessment**: Evaluate match risk levels
- **Team Form Analysis**: Recent performance and consistency metrics
- **Market Coverage**: Support for various betting markets (Match Winner, BTTS, Over/Under)

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Windows 10/11 (optimized for Windows)
- Internet connection for API access

### 1. Clone the Repository
```bash
git clone <repository-url>
cd football-project
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Edit `config.py` and add your API keys:

```python
# Primary API: API-Football (api-sports.io)
API_FOOTBALL_API_KEY = "YOUR_API_FOOTBALL_KEY_HERE"
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
API_FOOTBALL_TIMEZONE = "UTC"

# Fallback API: SportMonks
SPORTMONKS_API_KEY = "YOUR_SPORTMONKS_KEY_HERE"
SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3/football"

# Telegram Bot
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
```

### 5. Get API Keys

#### API-Football (api-sports.io)
1. Visit [api-sports.io](https://api-sports.io)
2. Sign up for an account
3. Subscribe to Football API
4. Copy your API key from the dashboard

#### SportMonks
1. Visit [sportmonks.com](https://sportmonks.com)
2. Create an account
3. Get your API token from the dashboard

#### Telegram Bot
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token

## 🚀 Quick Start

### Option 1: Full System (Recommended)
```bash
# Windows
start_unified_system.bat

# Linux/Mac
python main_realtime.py
```

### Option 2: Interactive Bot Only
```bash
# Windows
start_interactive_bot.bat

# Linux/Mac
python bot_interface/telegram_bot.py
```

### Option 3: Test Individual Components
```bash
# Test unified API system
python test_unified_api.py

# Test bot interface
python test_bot.py
```

## 📱 Using the Telegram Bot

### Commands
- `/start` - Initialize the bot and get welcome message
- `/help` - Show available commands and features
- `/status` - Check system status and uptime
- `/analyze` - Get today's match analysis
- `/live` - Get current live matches

### Natural Language
The bot understands natural language queries like:
- "Show me today's matches"
- "What are the live games?"
- "Analyze Manchester United vs Liverpool"
- "Give me betting tips"

## 🔧 System Architecture

### Core Components
```
├── main_realtime.py          # Main system orchestrator
├── realtime_analyzer.py      # Match analysis engine
├── api/
│   ├── unified_api_client.py # Dual API manager
│   ├── api_apifootball.py    # API-Football client
│   └── api_sportmonks.py    # SportMonks client
├── bot_interface/
│   └── telegram_bot.py      # Interactive Telegram bot
└── config.py                # Configuration and API keys
```

### Data Flow
1. **Fetch Fixtures** → API-Football (primary) → SportMonks (fallback)
2. **Provider Tagging** → Each fixture gets `_provider` tag
3. **Consistent Fetching** → Use same provider for related data
4. **Analysis** → Process data and generate insights
5. **Telegram** → Send results to users via bot

## 📊 API Coverage

### API-Football (Primary)
- ✅ **Fixtures**: Today's matches, live scores, fixture details
- ✅ **Odds**: Pre-match and live odds
- ✅ **Predictions**: Match outcome probabilities
- ✅ **Team Form**: Recent performance data
- ❌ **Expected Goals (xG)**: Not available in free plan

### SportMonks (Fallback)
- ✅ **Fixtures**: Comprehensive match data
- ✅ **Odds**: Various betting markets
- ✅ **Team Form**: Historical performance
- ⚠️ **Expected Goals**: Requires subscription
- ⚠️ **Predictions**: Requires subscription

## 🎯 Betting Analysis Features

### Value Betting
- Compare bookmaker odds with model predictions
- Identify discrepancies and opportunities
- Risk assessment and recommendations

### Team Analysis
- Recent form and consistency
- Head-to-head statistics
- Home/away performance
- Goal scoring patterns

### Market Analysis
- Available betting markets
- Odds movement tracking
- Market liquidity assessment

## 🔍 Troubleshooting

### Common Issues

#### 1. "API access denied" Messages
- **Cause**: Subscription plan limitations
- **Solution**: Upgrade your API plan or use available data
- **Note**: System continues working with available data

#### 2. Empty Results
- **Cause**: No matches for the specified date/league
- **Solution**: Check if there are matches today or try different parameters
- **Note**: Normal for many fixtures, especially lower leagues

#### 3. Telegram Bot Not Responding
- **Cause**: Bot token invalid or network issues
- **Solution**: Verify bot token and internet connection
- **Note**: Bot runs independently of main system

#### 4. "Cannot run event loop" Error
- **Cause**: Multiple async operations conflict
- **Solution**: Use the provided batch files or restart system
- **Note**: Fixed in latest version

### Log Levels
- **INFO**: Normal system operation
- **WARNING**: Non-critical issues
- **DEBUG**: Detailed debugging information
- **ERROR**: Critical errors requiring attention

## 📈 Performance & Monitoring

### System Statistics
- **Total Analyses**: Number of matches analyzed
- **Success Rate**: Percentage of successful API calls
- **API Usage**: Primary vs fallback API usage
- **Uptime**: System running time

### Rate Limiting
- **API-Football**: 150ms between requests (free plan)
- **SportMonks**: 100ms between requests
- **Automatic**: Built-in rate limiting and retry logic

## 🔒 Security & Privacy

### API Key Security
- Store API keys in `config.py` (not in version control)
- Use environment variables for production
- Rotate keys regularly

### Data Privacy
- No user data stored permanently
- All analysis data is temporary
- Telegram chat IDs are not logged

## 🚀 Advanced Usage

### Custom Analysis
```python
from realtime_analyzer import RealTimeAnalyzer

analyzer = RealTimeAnalyzer()
results = await analyzer.analyze_today_matches()
```

### API Client Usage
```python
from api.unified_api_client import UnifiedAPIClient

client = UnifiedAPIClient()
matches = await client.get_today_matches()
```

### Bot Integration
```python
from bot_interface.telegram_bot import TelegramBot

bot = TelegramBot()
await bot.start()
```

## 📝 Configuration Options

### Environment Variables
```bash
# Optional: Use environment variables instead of config.py
export API_FOOTBALL_API_KEY="your_key"
export SPORTMONKS_API_KEY="your_key"
export TELEGRAM_BOT_TOKEN="your_token"
```

### Custom Settings
```python
# In config.py
ANALYSIS_INTERVAL = 5  # Minutes between live analysis
DAILY_ANALYSIS_TIME = "09:00"  # Daily analysis time
LOG_LEVEL = "INFO"  # Logging level
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Include error handling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **API-Football**: For providing comprehensive football data
- **SportMonks**: For reliable fallback API service
- **python-telegram-bot**: For excellent Telegram bot framework
- **aiohttp**: For efficient async HTTP requests

## 📞 Support

### Getting Help
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Test individual components
4. Open an issue on GitHub

### Community
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and help
- **Wiki**: Additional documentation and examples

---

## 🎉 Quick Success Checklist

- [ ] API keys configured in `config.py`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Virtual environment activated
- [ ] System starts without errors (`python main_realtime.py`)
- [ ] Telegram bot responds to commands
- [ ] API connections working (test with `python test_unified_api.py`)

**Happy Betting Analysis! 🚀⚽**
