# 🚀 FIXORA PRO - Pipeline Architecture

## 📋 **Overview**

The FIXORA PRO system now implements a complete data processing pipeline that aligns with the system architecture diagram:

```
APIs → ETL → Modelling → Value Engine → Reporting/Storage
```

## 🏗️ **Architecture Components**

### **1. Data Sources (APIs)**
- **API-Football**: Primary data source for match statistics and odds
- **SportMonks**: Fallback data source for fixtures and lineups
- **PlayerStats**: Additional player and team performance data

### **2. ETL (Extract, Transform, Load)**
- **Data Ingestion**: Collects data from multiple API sources
- **Data Cleaning**: Standardizes formats, handles missing data, validates integrity
- **Data Storage**: Stores cleaned data in SQLite database with proper schema

### **3. Modelling**
- **Goal Prediction Model**: Poisson-based statistical model for match outcomes
- **Team Strength Analysis**: Calculates home/away performance factors
- **Probability Generation**: Converts model outputs to betting probabilities

### **4. Value Engine**
- **Odds Validation**: Centralized filtering (≥1.8 odds requirement)
- **Edge Calculation**: Compares model probabilities with market odds
- **Kelly Criterion**: Mathematical validation for optimal stake sizing
- **Risk Management**: Configurable thresholds and daily limits

### **5. Reporting & Storage**
- **ROI Tracking**: Comprehensive performance monitoring
- **PDF Reports**: Weekly and daily performance summaries
- **Telegram Integration**: Automated notifications and updates
- **Data Persistence**: Historical data storage and analysis

## 📁 **File Structure**

```
football-project/
├── etl/                          # Data ingestion and processing
│   ├── __init__.py
│   └── ingest.py                 # Main ETL logic
├── models/                       # Statistical models
│   ├── __init__.py
│   └── goal_model.py            # Poisson goal prediction model
├── pipeline/                     # Pipeline orchestration
│   ├── __init__.py
│   └── run_daily.py             # Daily pipeline runner
├── scripts/                      # Development utilities
│   └── dev_seed.py              # Database seeding script
├── tests/                        # Test suite
│   ├── test_roi_contract.py     # ROI consistency tests
│   ├── test_value_engine.py     # Value engine tests
│   └── test_pipeline_shapes.py  # Pipeline structure tests
└── settings.local.example.env    # Configuration template
```

## 🔄 **Pipeline Flow**

### **Daily Execution (08:00 UK Time)**

1. **ETL Process** (`etl.ingest.py`)
   - Load data from APIs (currently sample data)
   - Clean and validate data
   - Store in `cleaned_*` tables

2. **Modelling Process** (`models.goal_model.py`)
   - Calculate team strengths
   - Generate match predictions
   - Store in `model_predictions` table

3. **Value Engine Analysis**
   - Filter odds using centralized validation
   - Calculate betting edges
   - Apply Kelly criterion
   - Identify value bets

4. **Reporting & Storage**
   - Generate performance reports
   - Update ROI tracking
   - Send Telegram notifications

## 🗄️ **Database Schema**

### **ETL Tables**

#### `cleaned_match_data`
- Match statistics (possession, shots, goals, etc.)
- Weather and referee information
- Performance metrics and analytics

#### `cleaned_odds_data`
- Betting odds from multiple bookmakers
- Market types and selections
- Line movements and updates

#### `cleaned_fixtures`
- Match scheduling information
- Team lineups and formations
- Venue and kickoff details

### **Model Tables**

#### `model_predictions`
- Team strength calculations
- Match outcome probabilities
- Over/under goal predictions
- Model confidence scores

### **ROI Tables** (Existing)

#### `roi_tracking`
- Individual bet records
- Performance metrics
- Profit/loss calculations

#### `market_performance`
- Market-level statistics
- ROI and win rate tracking

#### `league_performance`
- League-level analysis
- Performance comparisons

## 🧪 **Testing**

### **Running Tests**

```bash
# Run all tests
python run_tests.py

# Run specific test suites
python -m unittest tests.test_roi_contract
python -m unittest tests.test_value_engine
python -m unittest tests.test_pipeline_shapes

# Run with coverage (if pytest-cov installed)
pytest --cov=. tests/
```

### **Test Coverage**

- **ROI Contract**: Field mapping consistency and percent values
- **Value Engine**: Odds validation and Kelly criterion
- **Pipeline Shapes**: Table creation and data flow
- **Integration**: End-to-end pipeline execution

## 🚀 **Quick Start**

### **1. Setup Environment**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### **2. Seed Development Data**

```bash
# Populate database with sample data
python scripts/dev_seed.py
```

### **3. Run Pipeline**

```bash
# Execute complete daily pipeline
python pipeline/run_daily.py
```

### **4. Generate Reports**

```bash
# Generate weekly ROI report
python reports/roi_weekly_report.py
```

## ⚙️ **Configuration**

### **Environment Variables**

Copy `settings.local.example.env` to `settings.local.env` and modify:

```bash
# Odds Filtering
MIN_ODDS=1.8
MAX_ODDS=10.0

# Value Bet Analysis
VALUE_BET_THRESHOLD=0.05
CONFIDENCE_THRESHOLD=0.6

# Risk Management
MAX_BETS_PER_DAY=10
BANKROLL_PERCENTAGE=0.02
```

### **Database Configuration**

```python
# config.py
DATABASE_FILE = "betting_data.db"
CACHE_ENABLED = True
CACHE_DURATION = 3600
```

## 📊 **Monitoring & Debugging**

### **Pipeline Status**

```python
from pipeline.run_daily import DailyPipeline

pipeline = DailyPipeline()
status = pipeline.get_pipeline_status()

print(f"ETL Status: {status['etl_status']}")
print(f"Model Status: {status['model_status']}")
print(f"Table Counts: {status['table_counts']}")
```

### **Logging**

Pipeline execution is logged to `pipeline.log` with detailed information about each step.

### **Database Inspection**

```bash
# SQLite command line
sqlite3 betting_data.db

# Check table structure
.schema cleaned_match_data
.schema model_predictions

# View sample data
SELECT * FROM cleaned_match_data LIMIT 5;
SELECT * FROM model_predictions LIMIT 5;
```

## 🔧 **Development**

### **Adding New Data Sources**

1. **Extend ETL Package**
   ```python
   # etl/ingest.py
   def load_new_api_data(self):
       # Implement new API integration
       pass
   ```

2. **Update Database Schema**
   ```sql
   CREATE TABLE new_data_table (
       id INTEGER PRIMARY KEY,
       -- Add new fields
   );
   ```

3. **Add to Pipeline**
   ```python
   # pipeline/run_daily.py
   def run_new_etl(self):
       # Integrate new data source
       pass
   ```

### **Adding New Models**

1. **Create Model Class**
   ```python
   # models/new_model.py
   class NewModel:
       def fit_predict(self, data):
           # Implement model logic
           pass
   ```

2. **Update Pipeline**
   ```python
   # pipeline/run_daily.py
   def run_modelling(self):
       # Add new model execution
       pass
   ```

## 📈 **Performance Considerations**

### **Database Optimization**

- **Indexing**: Add indexes on frequently queried fields
- **Partitioning**: Consider table partitioning for large datasets
- **Cleanup**: Implement data retention policies

### **API Rate Limiting**

- **Throttling**: Implement rate limiting for external APIs
- **Caching**: Cache API responses to reduce calls
- **Fallbacks**: Use multiple data sources for redundancy

### **Memory Management**

- **Batch Processing**: Process data in chunks
- **Streaming**: Use generators for large datasets
- **Cleanup**: Release memory after processing

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Database Connection Errors**
   - Check file permissions
   - Verify database path in config
   - Ensure SQLite is available

2. **Import Errors**
   - Verify Python path
   - Check package installation
   - Validate import statements

3. **Data Quality Issues**
   - Review sample data structure
   - Check API response formats
   - Validate data validation logic

### **Debug Mode**

Enable debug logging in `settings.local.env`:

```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

## 🔮 **Future Enhancements**

### **Planned Features**

- **Real-time Processing**: Stream processing for live matches
- **Machine Learning**: Advanced ML models for prediction
- **Cloud Integration**: AWS/Azure deployment options
- **API Gateway**: Centralized API management
- **Monitoring Dashboard**: Web-based monitoring interface

### **Scalability Improvements**

- **Database Migration**: PostgreSQL/MySQL for production
- **Message Queues**: Redis/RabbitMQ for async processing
- **Microservices**: Service-oriented architecture
- **Containerization**: Docker deployment support

## 📚 **Additional Resources**

- **System Diagram**: See project documentation
- **API Documentation**: External API references
- **Testing Guide**: Comprehensive testing documentation
- **Deployment Guide**: Production deployment instructions

---

*For technical support or questions, refer to the main project documentation or create an issue in the project repository.*
