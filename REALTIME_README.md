# FIXORA PRO - Real-Time Football Betting System

## 🚀 Overview

FIXORA PRO is a real-time football betting analysis system that focuses on live data from the SportMonks API and delivers focused summaries directly to Telegram. The system is designed to provide real-time insights without any mock data, ensuring you get accurate, live information for your betting decisions.

## ✨ Key Features

### 🔥 Real-Time Data Focus
- **Live Match Monitoring**: Analyzes matches as they happen in real-time
- **Live Odds Tracking**: Monitors odds changes during matches
- **Live Score Updates**: Tracks live scores and match progress
- **Real-Time Analysis**: Provides instant analysis and recommendations

### 📊 Comprehensive Analysis
- **Team Form Analysis**: Recent performance and consistency metrics
- **Expected Goals (xG)**: Advanced statistical analysis
- **Value Bet Detection**: Identifies betting opportunities with positive expected value
- **Risk Assessment**: Evaluates betting risk levels
- **SportMonks Predictions**: Integrates official predictions from the API

### 📱 Telegram Integration
- **Real-Time Notifications**: Instant updates on live matches
- **Focused Summaries**: Concise, actionable information
- **Morning/Evening Reports**: Daily summaries and insights
- **Customizable Alerts**: Set your preferred notification frequency

## 🏗️ System Architecture

### Core Components

1. **RealTimeAnalyzer** (`realtime_analyzer.py`)
   - Handles live data analysis
   - Generates focused summaries
   - Manages analysis caching

2. **SportMonks API Client** (`api/api_sportmonks.py`)
   - Real-time data fetching
   - Live odds monitoring
   - Team form analysis

3. **Real-Time Main System** (`main_realtime.py`)
   - Orchestrates analysis tasks
   - Manages scheduling
   - Handles Telegram communication

4. **Telegram Bot Interface** (`bot_interface/telegram_bot.py`)
   - Sends real-time updates
   - Handles user interactions
   - Manages notifications

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- SportMonks API key (configured in `config.py`)
- Telegram bot token (configured in `config.py`)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd football-project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   - Edit `config.py` with your SportMonks API key
   - Add your Telegram bot token

4. **Start the system**
   ```bash
   # Windows
   start_realtime.bat
   
   # Linux/Mac
   python main_realtime.py
   ```

## 📋 API Endpoints Used

The system uses the following SportMonks v3 endpoints for real-time data:

### 🏟️ Fixtures & Matches
- `GET /fixtures?filters=todayDate` - Today's matches
- `GET /fixtures/{id}?include=participants;league;states;scores` - Match details
- `GET /fixtures?filters=live` - Live matches

### 🎯 Odds & Markets
- `GET /odds/pre-match/fixtures/{id}` - Match odds
- `GET /odds/pre-match/latest` - Latest odds updates
- `GET /odds/markets` - Available markets

### 📊 Team & Form Data
- `GET /teams/{id}?include=latest:5` - Team form (last 5 matches)
- `GET /teams/{id}?include=statistics.details.type` - Team statistics

### 🔮 Predictions & Analysis
- `GET /predictions/probabilities/fixtures/{id}` - Match probabilities
- `GET /predictions/value-bets/fixtures/{id}` - Value betting opportunities
- `GET /expected/fixtures/{id}` - Expected goals data

## ⏰ Analysis Schedule

### Real-Time Monitoring
- **Live Match Analysis**: Every 5 minutes
- **Daily Match Analysis**: Every 30 minutes
- **Morning Summary**: 09:00 daily
- **Evening Summary**: 18:00 daily

### Analysis Types
1. **Live Matches**: Real-time analysis of ongoing games
2. **Upcoming Matches**: Pre-match analysis and predictions
3. **Completed Matches**: Post-match analysis and insights

## 📱 Telegram Commands

### Available Commands
- `/start` - Initialize the bot
- `/setchat` - Set your chat ID for notifications
- `/status` - Check system status
- `/help` - Show available commands

### Notification Types
- **Live Match Updates**: Real-time match progress
- **Value Bet Alerts**: High-value betting opportunities
- **Risk Warnings**: High-risk match notifications
- **Daily Summaries**: Morning and evening reports

## 🔍 Analysis Features

### Match Analysis
- **Team Form Scoring**: Weighted analysis of recent performance
- **Head-to-Head Comparison**: Team matchup analysis
- **Home/Away Performance**: Location-based analysis
- **League Context**: Competition level assessment

### Betting Analysis
- **Value Bet Detection**: Odds vs. probability analysis
- **Risk Assessment**: Match risk level evaluation
- **Market Analysis**: Multiple betting market coverage
- **Bookmaker Comparison**: Best odds identification

### Statistical Analysis
- **Expected Goals (xG)**: Advanced goal prediction
- **Form Consistency**: Team performance stability
- **Historical Performance**: Past matchup analysis
- **Trend Analysis**: Performance pattern recognition

## 🛠️ Configuration

### Environment Variables
```python
# config.py
SPORTMONKS_API_KEY = "your_api_key_here"
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = None  # Set via /setchat command
```

### Analysis Settings
```python
# Analysis intervals
LIVE_ANALYSIS_INTERVAL = 300  # 5 minutes
DAILY_ANALYSIS_INTERVAL = 1800  # 30 minutes

# Risk thresholds
VALUE_BET_THRESHOLD = 0.08  # 8% edge required
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence
```

## 📊 Output Examples

### Live Match Summary
```
🔥 **LIVE MATCHES**

⚽ Manchester United vs Liverpool
📊 ⚽ Manchester United vs Liverpool
📊 Status: LIVE
🏠 Manchester United Form: 2.4
✈️ Liverpool Form: 3.2
💰 Value Bets: 2 found
⚠️ Risk: MEDIUM
```

### Daily Summary
```
🌅 **FIXORA PRO - Morning Summary**
📅 Monday, January 15, 2024
⏰ Good Morning! Starting analysis for today's matches...

⏳ **Upcoming Matches Today: 12**

🔍 **Analysis Status:**
• Real-time monitoring enabled
• Live odds tracking active
• Value bet detection running
• Risk assessment enabled
```

## 🚨 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check your SportMonks API key
   - Verify internet connectivity
   - Check API rate limits

2. **Telegram Bot Issues**
   - Verify bot token is correct
   - Ensure bot has permission to send messages
   - Check chat ID configuration

3. **Analysis Failures**
   - Check log files for detailed error messages
   - Verify API endpoint availability
   - Check data format compatibility

### Log Files
- **Main System**: `realtime_betting_system.log`
- **API Client**: `api_client.log`
- **Telegram Bot**: `telegram_bot.log`

## 🔄 Updates & Maintenance

### Regular Updates
- **API Endpoint Updates**: SportMonks API changes
- **Analysis Algorithm Improvements**: Better prediction models
- **New Market Support**: Additional betting markets
- **Performance Optimizations**: Faster analysis and updates

### System Monitoring
- **Performance Metrics**: Analysis speed and accuracy
- **API Usage**: Rate limit monitoring
- **Error Tracking**: Issue identification and resolution
- **User Feedback**: Continuous improvement

## 📈 Performance Metrics

### Analysis Speed
- **Live Match Analysis**: < 30 seconds per match
- **Daily Analysis**: < 5 minutes for 20+ matches
- **Telegram Delivery**: < 10 seconds after analysis

### Accuracy Targets
- **Value Bet Detection**: > 70% accuracy
- **Risk Assessment**: > 80% accuracy
- **Form Analysis**: > 85% accuracy

## 🤝 Support & Community

### Getting Help
- **Documentation**: Check this README first
- **Logs**: Review log files for error details
- **Issues**: Report bugs via GitHub issues
- **Community**: Join our discussion forum

### Contributing
- **Code Improvements**: Submit pull requests
- **Bug Reports**: Help identify and fix issues
- **Feature Requests**: Suggest new capabilities
- **Documentation**: Help improve guides and examples

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **SportMonks**: For providing comprehensive football data APIs
- **Telegram**: For the excellent bot platform
- **Open Source Community**: For the tools and libraries used

---

**FIXORA PRO** - Making football betting analysis real-time, accurate, and accessible! ⚽🎯
