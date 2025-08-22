from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Timezone constants
LONDON = ZoneInfo("Europe/London")
UTC = ZoneInfo("UTC")

def now_london():
    """Get current time in Europe/London timezone"""
    return datetime.now(LONDON)

def now_utc():
    """Get current time in UTC timezone"""
    return datetime.now(UTC)

def to_utc(dt):
    """Convert datetime to UTC timezone"""
    if dt.tzinfo is None:
        # If naive datetime, assume it's in London time
        dt = dt.replace(tzinfo=LONDON)
    return dt.astimezone(UTC)

def to_london(dt):
    """Convert datetime to Europe/London timezone"""
    if dt.tzinfo is None:
        # If naive datetime, assume it's in UTC
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(LONDON)

def is_future_match(kickoff_time, cutoff_minutes=0):
    """Check if match kickoff is in the future (with optional cutoff)"""
    if kickoff_time.tzinfo is None:
        # If naive datetime, assume it's in UTC
        kickoff_time = kickoff_time.replace(tzinfo=UTC)
    
    cutoff_time = now_london() + timedelta(minutes=cutoff_minutes)
    cutoff_utc = to_utc(cutoff_time)
    
    return kickoff_time >= cutoff_utc

def format_london_time(dt):
    """Format datetime in London timezone for display"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    london_time = to_london(dt)
    return london_time.strftime("%H:%M")

def get_next_8am_london():
    """Get next 8:00 AM London time"""
    now = now_london()
    next_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
    
    if now.hour >= 8:
        # If it's past 8 AM today, get tomorrow's 8 AM
        next_8am = next_8am + timedelta(days=1)
    
    return next_8am
