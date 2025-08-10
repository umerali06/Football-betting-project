# Sportmonks API Integration Guide

## ✅ Integration Status

Your Sportmonks API key has been successfully integrated into the football betting system!

**API Key**: `R2MI7yE4uEJdrFEjZW4ig5EG45orVa1Znx3U4RkpnOlcNRxuExpGCVs1YOkl`  
**Website**: [https://my.sportmonks.com/](https://my.sportmonks.com/)  
**Current Plan**: Football Free Plan  

## 🔧 Configuration Added

### Files Modified:
1. **`config.py`** - Added Sportmonks API configuration
2. **`api/sportmonks_client.py`** - New Sportmonks API client
3. **`api/unified_client.py`** - Unified client supporting both APIs
4. **`main.py`** - Updated to use unified client
5. **`.env.example`** - Added environment variable template

### Configuration Settings:
```python
# Sportmonks API Configuration
SPORTMONKS_API_KEY = "R2MI7yE4uEJdrFEjZW4ig5EG45orVa1Znx3U4RkpnOlcNRxuExpGCVs1YOkl"
SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3/football"
SPORTMONKS_ENABLED = True

# API Priority Configuration
PRIMARY_API = "sportmonks"        # Uses Sportmonks as primary
FALLBACK_API = "api_football"     # Falls back to API Football if needed
```

## 🚀 How to Use

### Option 1: Run with Sportmonks as Primary (Current Setup)
```bash
python3 main.py
```

### Option 2: Test Sportmonks Integration
```bash
python3 test_sportmonks.py
```

### Option 3: Validate API Key
```bash
python3 test_basic_sportmonks.py
```

## 📊 Current Status

✅ **API Key Valid**: Your Sportmonks API key is working  
✅ **Authentication Working**: API calls authenticate successfully  
⚠️ **Limited Access**: You're on the Football Free Plan with restricted data access  

### Free Plan Limitations:
- Limited number of endpoints available
- Reduced data access for fixtures, odds, and statistics
- May not have access to live/today's matches
- Rate limits apply (3000 requests remaining)

## 🎯 System Behavior

The system is configured with **intelligent fallback**:

1. **Primary**: Tries Sportmonks API first
2. **Fallback**: If Sportmonks fails or returns no data, automatically uses API Football
3. **Error Handling**: Graceful handling of subscription limitations

### Example Output:
```
🚀 Primary API: Sportmonks
🔄 Fallback API: API Football
⚠️ Sportmonks API: Limited access with current subscription
   Current plan: Football Free Plan
⚠️ Primary API returned empty result, trying fallback...
✅ Using API Football for match data
```

## 💡 Recommendations

### To Get Full Sportmonks Access:
1. **Upgrade Subscription**: Visit [my.sportmonks.com](https://my.sportmonks.com/)
2. **Choose Paid Plan**: Select a plan that includes fixtures, odds, and live data
3. **No Code Changes Needed**: System will automatically use full features

### Current Workaround:
- System automatically falls back to API Football when Sportmonks has limited data
- You get the best of both APIs
- No interruption to your betting analysis

## 🔧 Environment Variables (Optional)

For better security, you can use environment variables:

**Create `.env` file:**
```bash
SPORTMONKS_API_KEY=R2MI7yE4uEJdrFEjZW4ig5EG45orVa1Znx3U4RkpnOlcNRxuExpGCVs1YOkl
```

**Run with environment variables:**
```bash
export SPORTMONKS_API_KEY="R2MI7yE4uEJdrFEjZW4ig5EG45orVa1Znx3U4RkpnOlcNRxuExpGCVs1YOkl"
python3 main.py
```

## 🛠️ Technical Details

### API Endpoints Supported:
- `fixtures` - Match fixtures and results
- `odds` - Betting odds data
- `statistics` - Match statistics
- `standings` - League standings
- `teams` - Team information
- `players` - Player data

### Data Normalization:
- Sportmonks data is automatically converted to API Football format
- Seamless integration with existing betting models
- No changes needed to your analysis code

## 📈 Next Steps

1. **Test the System**: Run `python3 main.py --demo` to see it in action
2. **Monitor Performance**: Check which API provides better data
3. **Consider Upgrade**: If you need real-time data, upgrade your Sportmonks plan
4. **Customize**: Adjust `PRIMARY_API` and `FALLBACK_API` in `config.py` as needed

## 🔍 Troubleshooting

### If you get API errors:
1. Check your internet connection
2. Verify API key is correct at [my.sportmonks.com](https://my.sportmonks.com/)
3. Check rate limits (current: 3000 requests remaining)
4. Ensure your subscription is active

### Common Issues:
- **400 Bad Request**: Usually subscription limitations (handled automatically)
- **401 Unauthorized**: Invalid API key (check key in config.py)
- **429 Too Many Requests**: Rate limit exceeded (system waits automatically)

## ✅ Integration Complete!

Your Sportmonks API is now fully integrated and working. The system intelligently uses Sportmonks when possible and falls back to API Football when needed, giving you the best possible data coverage for your football betting analysis.

**Ready to run**: `python3 main.py`