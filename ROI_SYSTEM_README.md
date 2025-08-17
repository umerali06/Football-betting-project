# FIXORA PRO ROI Betting System

## Overview
The FIXORA PRO ROI Betting System is a comprehensive, focused Telegram bot that provides advanced ROI analysis, unit-based betting recommendations, automatic morning updates, and performance tracking. Built with a streamlined architecture that prioritizes ROI-focused betting analysis.

## 🚀 Key Features

### 💰 Advanced ROI Analysis
- **Real-time Data**: Fetches live match data from API-Football and SportMonks
- **Smart Fallback**: Enhanced API client with multiple fallback strategies
- **League Filtering**: Focuses on top-tier European leagues for quality opportunities
- **ROI Rating System**: Calculates realistic ROI ratings based on actual odds data

### 💎 Intelligent Unit-Based Betting System
- **1st Place**: 3 units (highest confidence, top-rated opportunity)
- **2nd Place**: 2 units (high confidence, strong potential)
- **3rd Place**: 1 unit (medium confidence, good value)
- **4th & 5th**: 0.5 units (lower confidence, speculative plays)

### 🕗 Automatic Morning Updates
- **Precise Timing**: Daily ROI analysis at exactly 8:00 AM UK time
- **User-Specific**: Sends personalized updates to all active users
- **Complete Analysis**: Full ROI summary with unit recommendations
- **Independent Operation**: Runs separately from manual commands

### 📊 Comprehensive Performance Reports
- **PDF Generation**: Professional betting performance reports
- **Weekly Summaries**: Detailed weekly ROI performance analysis
- **Performance Tracking**: Unit-based profit/loss analysis
- **Historical Data**: Track betting trends and ROI patterns

### 🔧 Streamlined System Architecture
- **ROI-Only Mode**: Clean, focused system without unnecessary features
- **Enhanced API Integration**: Unified client for multiple data sources
- **Automatic Scheduling**: Built-in task scheduler for daily operations
- **User Session Management**: Track and manage active user sessions

## 📱 Available Commands

### `/start`
- Welcome message with system overview
- Explains ROI-focused features and unit system
- Sets up user session tracking

### `/help`
- Comprehensive help information
- Detailed command descriptions
- Feature explanations and usage tips

### `/status`
- Real-time bot status and health
- API connection information
- Active user session count
- System configuration details

### `/analyze_roi` ⭐ **MAIN COMMAND**
- **Real-time Analysis**: Analyzes today's matches using live API data
- **Top 5 Opportunities**: Shows highest-rated bets with detailed analysis
- **Unit Recommendations**: Provides specific unit allocations (3-2-1-0.5)
- **Match Details**: Status, scores, odds availability, and ROI ratings
- **League Breakdown**: Shows match distribution across target leagues

### `/report`
- **PDF Generation**: Creates comprehensive betting performance report
- **Performance Metrics**: Total bets, win rate, overall ROI, P&L
- **Unit Analysis**: Breakdown by unit allocation and confidence level
- **Historical Trends**: Performance tracking over time

### `/weekly_report`
- **Weekly Summary**: Generates weekly ROI performance PDF
- **Period Analysis**: Detailed breakdown of weekly performance
- **Insights**: Key performance indicators and trends
- **Recommendations**: Based on weekly performance data

## 🏗️ System Architecture

### Core Components
```
├── main.py                      # Main system with ROI-only mode
├── telegram_bot.py              # Enhanced Telegram bot with ROI commands
├── api/
│   ├── enhanced_api_client.py   # Unified API client with fallback strategies
│   ├── api_apifootball.py      # API-Football integration
│   ├── sportmonks_client.py    # SportMonks integration
│   └── league_filter.py        # League filtering and targeting
├── reports/
│   └── report_generator.py     # PDF report generation
└── start_roi_scheduler.py      # Automatic morning updates scheduler
```

### API Integration Strategy
- **Primary Source**: API-Football (api-sports.io) for real-time data
- **Fallback Source**: SportMonks for backup data
- **Enhanced Client**: Multiple fallback strategies with sample data generation
- **Real-time Odds**: Live odds fetching without "Sample:" prefixes
- **League Targeting**: Focus on top European leagues for quality opportunities

## 🚀 Getting Started

### 1. Start the Main System (ROI-Only Mode)
```bash
python main.py --roi-only
```
This starts the system in ROI-only mode, disabling unnecessary daily analysis features.

### 2. Start the Automatic ROI Scheduler
```bash
python start_roi_scheduler.py
```
This runs the automatic morning ROI updates at 8:00 AM UK time.

### 3. Use Commands in Telegram
- Send `/start` to initialize your session
- Use `/analyze_roi` for real-time ROI opportunities
- Use `/report` for performance reports
- Use `/weekly_report` for weekly summaries
- Receive automatic updates every morning at 8:00 AM UK time

## ⚙️ Configuration

### Required Environment Variables
```python
# config.py
TELEGRAM_BOT_TOKEN = "your_bot_token"
API_FOOTBALL_KEY = "your_api_football_key"
SPORTMONKS_TOKEN = "your_sportmonks_token"
```

### System Modes
- **ROI-Only Mode**: Clean, focused system (`--roi-only` flag)
- **Full Mode**: Complete system with all features (default)

## 🔍 How It Works

### ROI Analysis Process
1. **Data Fetching**: Retrieves match data from multiple API sources
2. **League Filtering**: Focuses on target European leagues
3. **Odds Analysis**: Processes real-time odds data
4. **ROI Calculation**: Computes realistic ROI ratings
5. **Unit Assignment**: Assigns units based on confidence ranking
6. **Result Formatting**: Creates comprehensive Telegram message

### Automatic Morning Updates
1. **Scheduled Execution**: Runs daily at 8:00 AM UK time
2. **User Iteration**: Processes all active user sessions
3. **ROI Analysis**: Performs complete analysis for each user
4. **Message Delivery**: Sends personalized updates via Telegram
5. **Error Handling**: Graceful fallback for failed deliveries

### Report Generation
1. **Data Collection**: Gathers betting performance data
2. **PDF Creation**: Generates professional PDF reports
3. **File Delivery**: Sends PDFs directly through Telegram
4. **Performance Tracking**: Maintains historical data

## 📊 Performance Features

### ROI Tracking
- **Real-time Analysis**: Live data from multiple API sources
- **Performance Metrics**: Win rate, ROI%, unit-based P&L
- **Historical Data**: Track performance over time
- **Trend Analysis**: Identify patterns and opportunities

### Unit System Benefits
- **Risk Management**: Diversified betting across confidence levels
- **Performance Tracking**: Monitor success by unit allocation
- **Bankroll Protection**: Limit exposure on lower-confidence bets
- **Scalable Strategy**: Adjust units based on performance

## 🛠️ Technical Details

### Dependencies
```
python-telegram-bot>=20.0
schedule>=1.2.0
pytz>=2023.3
asyncio
reportlab>=4.0.0
httpx>=0.24.0
```

### Scheduling System
- **Timezone Handling**: UK time (8:00 AM) for morning updates
- **Threading**: Separate thread for scheduler operations
- **Error Recovery**: Automatic retry mechanisms
- **User Management**: Track active sessions for updates

### API Fallback Strategy
1. **Primary**: API-Football with real-time data
2. **Secondary**: SportMonks with backup data
3. **Enhanced**: Sample data generation for testing
4. **Caching**: 5-minute TTL for performance optimization

## 🎯 Key Benefits

1. **Focused Functionality**: Only essential ROI betting commands
2. **Real-time Data**: Live odds and match information
3. **Intelligent Units**: Data-driven unit allocation system
4. **Automatic Updates**: Reliable morning ROI summaries
5. **Professional Reports**: PDF generation for performance tracking
6. **Scalable Architecture**: Clean, maintainable codebase
7. **API Reliability**: Multiple fallback strategies
8. **User Experience**: Intuitive commands and clear outputs

## 🔧 Troubleshooting

### Common Issues
- **API Connection**: Verify API keys in config.py
- **Scheduler Issues**: Check timezone settings and system time
- **PDF Generation**: Ensure reportlab is installed
- **Telegram Errors**: Verify bot token and permissions

### Log Files
- **Main System**: Check console output for errors
- **Scheduler**: Monitor start_roi_scheduler.py output
- **API Calls**: Review enhanced_api_client logs

## 📈 Future Enhancements

### Planned Features
- **Advanced Analytics**: Machine learning for ROI prediction
- **Custom Alerts**: User-defined notification preferences
- **Portfolio Management**: Track multiple betting strategies
- **Performance Dashboard**: Web-based analytics interface

### System Improvements
- **Enhanced Caching**: Optimize API response times
- **User Preferences**: Customizable update schedules
- **Multi-language**: Support for additional languages
- **Mobile App**: Native mobile application

---

## 🎉 System Status

**Current Version**: 2.0 - Enhanced ROI System  
**Last Updated**: August 2025  
**System Mode**: ROI-Only (Streamlined)  
**Automatic Updates**: 8:00 AM UK time daily  
**API Status**: Enhanced with fallback strategies  

**Note**: This system is specifically designed for ROI-focused betting analysis with automatic morning updates. All unnecessary features have been removed to focus on core ROI functionality and user experience.
