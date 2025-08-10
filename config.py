import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_FOOTBALL_KEY = "376d3a099be68a055af2aca6e237bdd5"
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"

# Sportmonks API Configuration
SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY", "R2MI7yE4uEJdrFEjZW4ig5EG45orVa1Znx3U4RkpnOlcNRxuExpGCVs1YOkl")
SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3/football"
SPORTMONKS_ENABLED = True  # Enable/disable Sportmonks as data source

# API Priority Configuration
PRIMARY_API = "sportmonks"  # Options: "api_football", "sportmonks"
FALLBACK_API = "api_football"  # Fallback if primary fails

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8209018533:AAFFEFcJ0XDKKOFdNvalvtFoxvS0JHkeG0k")
TELEGRAM_CHAT_ID = None  # Will be set when bot starts

# Premium Betting Configuration
VALUE_BET_THRESHOLD = 0.08  # 8% edge required for premium analysis
MIN_ODDS = 1.8
MAX_ODDS = 8.0
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for premium bets
MIN_MATCHES_ANALYZED = 5  # Minimum matches for team analysis

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
