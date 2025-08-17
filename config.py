
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
# Primary API: API-Football (api-sports.io)
API_FOOTBALL_API_KEY = "8e6fa3e25470765f5ca5f8031780069e"  # Add your API-Football key here
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
API_FOOTBALL_TIMEZONE = "Asia/Karachi"  # Use Asia/Karachi timezone for better date handling

# Fallback API: SportMonks
SPORTMONKS_API_KEY = "h9GMoaRrTilhjTWReVbVIofysrPRfkigyJ45IlCBhyp6x9EYu3Tqa5xqlUHC"
SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3/football"

# Enhanced API Keys for Better Real-Time Data
# FootyStats API for enhanced predictions
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", None)  # Add your FootyStats API key

# Odds API for enhanced odds data
ODDS_API_KEY = os.getenv("ODDS_API_KEY", None)  # Add your Odds API key

# Alternative Football APIs for redundancy
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", None)  # Add your Football-Data.org API key
LIVESCORE_API_KEY = os.getenv("LIVESCORE_API_KEY", None)  # Add your LiveScore API key

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8209018533:AAFDxZ0GujMc8dZ6HFVn0Lj3TDc3DrfQFCA"  # Your working token
# TELEGRAM_BOT_TOKEN = "8209018533:AAFFEFcJ0XDKKOFdNvalvtFoxvS0JHkeG0k"  # Your other token
TELEGRAM_CHAT_ID = None  # Will be set automatically when you send a message to the bot

# Premium Betting Configuration
VALUE_BET_THRESHOLD = 0.08  # 8% edge required for premium analysis
MIN_ODDS = 1.8
MAX_ODDS = 8.0
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for premium bets
MIN_MATCHES_ANALYZED = 5  # Minimum matches for team analysis

# Premium Analysis Settings
PREMIUM_ANALYSIS_ENABLED = True
AUTO_ANALYSIS_INTERVAL = 3600  # Check every hour (in seconds)
ANALYSIS_QUALITY_THRESHOLD = 0.6  # Minimum quality for premium analysis
MAX_ANALYSIS_MATCHES = 20  # Maximum matches to analyze per session

# Advanced Model Configuration
ELO_K_FACTOR = 24  # Reduced for more stable ratings
ELO_INITIAL_RATING = 1500
XG_WEIGHT = 0.5
ELO_WEIGHT = 0.3
CORNERS_WEIGHT = 0.2

# Machine Learning Parameters
ML_ENABLED = True
ML_CONFIDENCE_THRESHOLD = 0.75
ML_MIN_TRAINING_MATCHES = 50
ML_UPDATE_FREQUENCY = 7  # days

# Advanced Analysis Settings
FORM_WEIGHT_RECENT = 0.4  # Weight for last 5 matches
FORM_WEIGHT_MEDIUM = 0.3  # Weight for 6-15 matches
FORM_WEIGHT_OLD = 0.3     # Weight for 16+ matches
HOME_ADVANTAGE_BOOST = 0.15  # 15% boost for home teams
AWAY_PENALTY = 0.1        # 10% penalty for away teams

# Market-Specific Thresholds
MATCH_RESULT_THRESHOLD = 0.08
BTTS_THRESHOLD = 0.06
OVER_UNDER_THRESHOLD = 0.07
CORNERS_THRESHOLD = 0.05

# Value Bet Analysis Settings
VALUE_BET_THRESHOLD = 0.05  # Default threshold for value bets
MIN_ODDS = 1.5               # Minimum odds to consider
MAX_ODDS = 10.0              # Maximum odds to consider
CONFIDENCE_THRESHOLD = 0.6   # Minimum confidence for value bets

# Risk Management
MAX_BETS_PER_DAY = 10
MAX_BETS_PER_MATCH = 2
BANKROLL_PERCENTAGE = 0.02  # 2% of bankroll per bet
KELLY_CRITERION_ENABLED = True

# Advanced Statistics
INCLUDE_POSSESSION_ANALYSIS = True
INCLUDE_SHOTS_ANALYSIS = True
INCLUDE_CARDS_ANALYSIS = True
INCLUDE_WEATHER_ANALYSIS = True
INCLUDE_REFEREE_ANALYSIS = True

# Report Configuration
REPORT_OUTPUT_DIR = "reports"
WEEKLY_REPORT_FILENAME = "weekly_roi_report.pdf"
PREMIUM_REPORT_ENABLED = True

# Database Configuration
DATABASE_FILE = "betting_data.db"
CACHE_ENABLED = True
CACHE_DURATION = 3600  # 1 hour

# Supported Markets (Enhanced)
SUPPORTED_MARKETS = [
    "match_result",           # H2H Win/Draw/Win
    "both_teams_to_score",   # BTTS
    "over_under_goals",       # Over/Under Goals
    "corners",               # Total/Team Corners
    "double_chance",         # Double Chance
    "exact_goals",           # Exact Goals
    "first_half_result",     # First Half Result
    "clean_sheet",           # Clean Sheet
    "win_to_nil",            # Win to Nil
    "come_from_behind"       # Come from Behind
]

# Premium Bookmakers (Enhanced)
BOOKMAKERS = [
    "Bet365",
    "SkyBet", 
    "Paddy Power",
    "William Hill",
    "Ladbrokes",
    "Betfair",
    "Unibet",
    "Bwin"
]

# Advanced Filtering
MIN_LEAGUE_QUALITY = 0.6  # Minimum league quality score
MIN_TEAM_FORMS = 3        # Minimum recent matches for form analysis
EXCLUDE_FRIENDLIES = True
EXCLUDE_YOUTH_LEAGUES = True

# Performance Tracking
TRACK_ACCURACY = True
TRACK_PROFIT_LOSS = True
TRACK_BANKROLL = True
TRACK_STREAKS = True

# Alert Settings
ALERT_HIGH_EDGE = 0.15    # Alert for bets with 15%+ edge
ALERT_CONFIDENCE = 0.85   # Alert for bets with 85%+ confidence
ALERT_STREAK = 5          # Alert for 5+ consecutive wins/losses

# League Filtering Configuration
ENGLAND_LEAGUES = [
    39,  # Premier League
    40,  # Championship
    41,  # League One
    42,  # League Two
]

TOP_EUROPEAN_LEAGUES = [
    39,  # England - Premier League
    40,  # England - Championship
    41,  # England - League One
    42,  # England - League Two
    140, # Spain - La Liga
    135, # Italy - Serie A
    78,  # Germany - Bundesliga
    61,  # France - Ligue 1
    88,  # Netherlands - Eredivisie
    94,  # Portugal - Primeira Liga
    203, # Turkey - Super Lig
    119, # Poland - Ekstraklasa
    106, # Ukraine - Premier League
    113, # Belgium - Pro League
    197, # Czech Republic - First League
    39,  # England - Premier League (duplicate for clarity)
]

# ROI Tracking Configuration
ROI_TRACKING_ENABLED = True
ROI_TRACKING_INTERVAL = 3600  # Check every hour
WEEKLY_REPORT_DAY = "monday"  # Generate report every Monday
ROI_MIN_BETS_FOR_REPORT = 5   # Minimum bets required for meaningful ROI calculation

# Market ROI Thresholds
MARKET_ROI_THRESHOLDS = {
    "match_result": 0.01,      # 1% ROI threshold for H2H (lowered for testing)
    "both_teams_to_score": 0.01,  # 1% ROI threshold for BTTS (lowered for testing)
    "over_under_goals": 0.01,     # 1% ROI threshold for Over/Under (lowered for testing)
    "corners": 0.01,              # 1% ROI threshold for Corners (lowered for testing)
}
