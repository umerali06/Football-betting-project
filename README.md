# 🏈 FIXORA PRO - Football Betting Analysis System

A comprehensive AI-powered football betting analysis system that uses machine learning models to identify value bets and provide real-time insights.

## 🎯 What This System Does

**FIXORA PRO** is an intelligent football betting analysis platform that:

- **Analyzes football matches** using multiple prediction models (ELO, Expected Goals, Corners)
- **Identifies value bets** where bookmaker odds are higher than model predictions
- **Provides real-time updates** via Telegram bot
- **Manages betting risks** with sophisticated risk management algorithms
- **Integrates with SportMonks API** for live football data and odds

## 🏗️ System Architecture

```
FIXORA PRO/
├── 📊 Models/           # AI Prediction Models
├── 🎲 Betting/          # Value Bet Analysis & Risk Management
├── 🔌 API/              # External Data Integration
├── 🤖 Bot Interface/    # Telegram Bot & User Interface
├── 📈 Reports/          # Analysis Reports & Logs
└── ⚙️ Config/           # System Configuration
```

### Core Components

#### 🤖 **AI Prediction Models**
- **ELO Model**: Team strength ratings and match outcome predictions
- **Expected Goals (xG) Model**: Goal-scoring probability analysis
- **Corners Model**: Corner kick predictions and analysis
- **Machine Learning Model**: Advanced statistical predictions

#### 💰 **Value Bet Analyzer**
- Calculates implied probabilities from bookmaker odds
- Identifies value bets with positive expected value
- Applies Kelly Criterion for optimal bet sizing
- Filters bets by confidence thresholds and risk parameters

#### 🛡️ **Risk Management**
- Portfolio-level risk assessment
- Maximum bet size calculations
- Loss limit enforcement
- Correlation analysis between bets

#### 📡 **Data Integration**
- **SportMonks API**: Live football data, fixtures, and odds
- **Fallback System**: Mock data for testing and development
- **Real-time Updates**: Live match data and odds streaming

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ 
- SportMonks API subscription (optional for testing)
- Telegram Bot Token

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd football-project

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `config.py` with your settings:

```python
# API Configuration
SPORTMONKS_API_TOKEN = "your_api_token_here"
SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3"

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"

# Betting Parameters
VALUE_BET_THRESHOLD = 0.05  # 5% edge required
MIN_ODDS = 1.5               # Minimum odds to consider
MAX_ODDS = 10.0              # Maximum odds to consider
CONFIDENCE_THRESHOLD = 0.6   # Minimum confidence for bets
```

### 3. Run the System

```bash
# Start the main betting analysis system
python main.py

# The system will:
# 1. Fetch today's football fixtures
# 2. Generate predictions using AI models
# 3. Analyze odds for value bets
# 4. Send results to Telegram
# 5. Continue monitoring for updates
```

## 📱 Telegram Bot Commands

Once running, interact with your bot:

- `/start` - Initialize the system
- `/status` - Check system status
- `/analyze` - Run manual analysis
- `/odds <fixture_id>` - Get odds for specific match
- `/predictions <fixture_id>` - Get model predictions
- `/help` - Show available commands

## 🔧 How It Works

### 1. **Data Collection**
- Fetches daily football fixtures from SportMonks API
- Retrieves live odds data for each match
- Collects team form and historical data

### 2. **AI Predictions**
- **ELO Model**: Calculates team strength and win probabilities
- **xG Model**: Predicts goal-scoring patterns and totals
- **Corners Model**: Estimates corner kick frequencies
- **ML Model**: Combines all factors for final predictions

### 3. **Value Bet Analysis**
- Converts bookmaker odds to implied probabilities
- Compares with model predictions to find edges
- Applies risk filters and confidence thresholds
- Calculates optimal bet sizes using Kelly Criterion

### 4. **Risk Management**
- Monitors portfolio exposure
- Enforces maximum bet limits
- Tracks correlation between bets
- Implements stop-loss mechanisms

### 5. **Real-time Updates**
- Continuously monitors odds changes
- Sends alerts for new value bets
- Updates existing bet recommendations
- Provides daily summary reports

## 📊 Example Output

```
🎯 Generated predictions for fixture 216281:
   Match Result: {'home_win': 0.64, 'draw': 0.0, 'away_win': 0.36}
   Goals: {'over_25': 0.39, 'under_25': 0.61, 'btts': 0.45}
   Corners: {'over_65': 0.91, 'under_65': 0.09}

💰 Available odds:
   Match: {'home_win': 3.38, 'draw': 4.22, 'away_win': 3.14}
   Goals: {'over_total': 2.77, 'under_total': 2.3}
   Corners: {'over_corners': 1.87, 'under_corners': 2.38}

🔍 Found 3 value bets for this match
✅ Posted to Telegram successfully
```

## 🛠️ Development & Testing

### Project Structure
```
football-project/
├── main.py                 # Main application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── api/
│   ├── __init__.py
│   └── api_sportmonks.py  # SportMonks API client
├── betting/
│   ├── __init__.py
│   ├── value_bet_analyzer.py  # Value bet identification
│   └── risk_manager.py        # Risk management
├── models/
│   ├── __init__.py
│   ├── elo_model.py       # ELO rating system
│   ├── xg_model.py        # Expected goals model
│   ├── corners_model.py   # Corners prediction
│   └── ml_model.py        # Machine learning model
├── bot_interface/
│   ├── __init__.py
│   └── telegram_bot.py    # Telegram bot interface
└── reports/                # Generated reports and logs
```

### Testing Without API Access
The system includes a comprehensive fallback system:
- **Mock Data**: Generates realistic odds and match data
- **Placeholder IDs**: Uses generated team IDs for testing
- **Offline Mode**: Works completely without internet connection

### Adding New Models
1. Create new model file in `models/` directory
2. Implement `predict()` method returning probabilities
3. Add model to `generate_predictions()` in `main.py`
4. Update value bet analyzer to handle new markets

## 📈 Performance & Monitoring

### Logging
- **Application Logs**: `betting_system.log`
- **Real-time Logs**: `realtime_system.log`
- **Log Level**: Configurable (DEBUG, INFO, WARNING, ERROR)

### Metrics Tracked
- Number of fixtures analyzed
- Value bets identified
- Prediction accuracy
- API response times
- Error rates

## 🔒 Security & Best Practices

- **API Keys**: Store in environment variables, not in code
- **Rate Limiting**: Respects API rate limits
- **Error Handling**: Graceful fallbacks for API failures
- **Data Validation**: Input sanitization and validation
- **Logging**: Secure logging without sensitive data exposure

## 🚨 Troubleshooting

### Common Issues

**"No result(s) found" Error**
- Check SportMonks API subscription level
- Verify API token is valid
- System will use mock data as fallback

**Telegram Bot Not Responding**
- Verify bot token is correct
- Check chat ID configuration
- Ensure bot has permission to send messages

**Import Errors**
- Activate virtual environment
- Install missing dependencies: `pip install -r requirements.txt`
- Check Python version compatibility

### Debug Mode
Enable debug logging in `config.py`:
```python
LOG_LEVEL = "DEBUG"
```

## 📚 API Documentation

### SportMonks Integration
- **Base URL**: `https://api.sportmonks.com/v3`
- **Endpoints**: Fixtures, Odds, Teams, Form
- **Rate Limits**: Varies by subscription plan
- **Data Format**: JSON with nested structures

### Custom API Integration
To add new data sources:
1. Create new client class in `api/` directory
2. Implement standard interface methods
3. Update `main.py` to use new client
4. Add fallback handling

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request
5. Ensure code follows project standards

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For technical support or questions:
- Check the logs for error details
- Review configuration settings
- Ensure all dependencies are installed
- Verify API credentials and permissions

---

**FIXORA PRO** - Making Football Betting Smarter with AI 🚀⚽
