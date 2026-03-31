# Air Pollution Forecasting System - User Guide

*Last Updated: 2026-03-11*

This comprehensive guide will help you effectively use the Air Pollution Forecasting System for accurate air quality predictions with comprehensive ML metrics evaluation and health impact analysis.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Installation & Setup](#installation--setup)
3. [Quick Start Guide](#quick-start-guide)
4. [Web Interface Guide](#web-interface-guide)
5. [Data Requirements](#data-requirements)
6. [Configuration](#configuration)
7. [Understanding ML Metrics](#understanding-ml-metrics)
8. [Health Analysis](#health-analysis)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

---

## 🎯 System Overview

The Air Pollution Forecasting System is a sophisticated machine learning tool that:

- **Predicts air quality** using Prophet and ARIMA models with ensemble methods
- **Evaluates models** with standard ML metrics (R², RMSE, MAE, MAPE)
- **Provides comprehensive health analysis** with risk period identification
- **Generates interactive visualizations** with confidence intervals
- **Offers web interface** for user-friendly operation
- **Supports multiple export formats** for further analysis

### Key Components

| Component | Purpose | Output |
|-----------|---------|--------|
| **Data Processor** | Validates and prepares data | Processed dataset |
| **Prophet Trainer** | Trains Prophet time series model | Prophet model + metrics |
| **ARIMA Trainer** | Trains ARIMA statistical model | ARIMA model + metrics |
| **Forecaster** | Generates ensemble predictions | Forecast with confidence intervals |
| **Health Analyzer** | Analyzes health impacts | Risk assessment + recommendations |
| **Web Interface** | Provides user-friendly UI | Interactive dashboards |

### New Features in Current Version

- ✅ **Standard ML Metrics**: R², RMSE, MAE, MAPE evaluation
- ✅ **Model Comparison**: Automatic quality assessment and ensemble logic
- ✅ **Health Impact Analysis**: Risk periods and population impact
- ✅ **Interactive Web UI**: 4-tab interface with comprehensive outputs
- ✅ **Data Requirements Warning**: Prominent guidance section for raw data users
- ✅ **Export Capabilities**: CSV, JSON, TXT format downloads
- ✅ **Strict Data Format**: Eliminates timestamp errors with validation

---

## 🚀 Installation & Setup

**📖 For complete installation instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

### Prerequisites

- **Python 3.8+** installed (3.9+ recommended)
- **8GB RAM** minimum (16GB recommended)
- **4+ CPU cores** recommended
- **2GB disk space** available
- **Git** for cloning repository

### Quick Installation Steps

1. **Clone repository**:
```bash
git clone https://github.com/airquality/air-pollution-forecasting.git
cd air-pollution-forecasting
```

2. **Create virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

3. **Install dependencies**:
```bash
pip install -r documentation/requirements.txt
```

4. **Verify installation**:
```bash
python test_imports.py
```

### Step-by-Step Setup

For detailed setup instructions including troubleshooting, virtual environment creation, and configuration, please refer to the **[SETUP_GUIDE.md](SETUP_GUIDE.md)** which provides:

- ✅ Complete installation for Windows, macOS, and Linux
- ✅ Virtual environment setup
- ✅ Dependency verification
- ✅ Configuration setup
- ✅ Troubleshooting common issues
- ✅ System health checks

---

## ⚡ Quick Start Guide

### Option 1: Command Line Usage

```bash
# Basic usage with default settings
python main.py

# Custom data file and output directory
python main.py --data data/my_air_quality.csv --output results

# 7-day forecast with verbose logging
python main.py --days 7 --verbose
```

### Option 2: Python Script Usage

```python
from src import AirPollutionSystem

# Initialize the system
system = AirPollutionSystem(config_path='config.yaml')

# Process your data
data = system.load_data('data/air_quality_data.csv')
processed_data = system.process_data(data)

# Train models and generate forecasts
models = system.train_models(processed_data)
forecasts = system.generate_forecast(models, processed_data, horizon=31)

# Create visualizations
system.create_visualizations(processed_data, forecasts)
```

### Option 3: Run Example Script

```bash
# Run comprehensive examples
python example_usage.py
```

---

## 🌐 Web Interface Guide

### Launching the Web Interface

The web interface provides the most user-friendly way to use the system:

```bash
python run_ui.py
```

The interface will open at `http://localhost:8501` with a prominent **Data Requirements Warning** section at the top, followed by four main tabs:

### **🚨 Important: Data Requirements Warning**

When you first open the web interface, you'll see an expanded warning section titled **"📋 Important: Data Requirements & Recommendations"**. This section provides critical guidance for raw data users:

#### **What's Included:**
- **Required Data Format**: Essential columns and accepted naming conventions
  - Timestamp columns: `Timestamp`, `Date`, `datetime`, `date`, `time`
  - AQI columns: `AQI`, `aqi`, `Air_Quality_Index`, `Air Quality Index`
  - Optional pollutants: PM2.5, PM10, NO2, CO, SO2, O3, NH3, NO, NOx, Benzene, Toluene, Xylene

- **Data Quality Recommendations**:
  - Minimum 30 days of historical data for reliable forecasting
  - Hourly or daily measurements (avoid gaps > 24 hours)
  - Consistent time intervals between measurements
  - Valid AQI values ranging from 0-500

- **Common Issues to Avoid**:
  - Missing timestamps or invalid date formats
  - AQI values outside 0-500 range
  - Large gaps in time series data
  - Non-numeric pollutant concentrations

- **Pro Tip**: Automatic AQI calculation from pollutant concentrations using US EPA standards

#### **Why This Matters:**
This warning section helps users:
- ✅ Avoid common data format errors that cause processing failures
- ✅ Understand minimum data requirements for accurate forecasting
- ✅ Save time by providing correct data format upfront
- ✅ Leverage automatic AQI calculation when AQI values are missing

**⚠️ Always review this section before uploading data to ensure successful processing!**

---

### **Tab 1: Data Upload & Processing**

#### Features:
- **File Upload**: Drag-and-drop CSV file upload
- **Data Validation**: Real-time format checking with error messages
- **Data Summary**: Dataset statistics and quality metrics
- **Processing Status**: Progress tracking with status messages

#### Steps:
1. **Upload Data**: Click "Browse files" or drag-and-drop your CSV
2. **Validate Format**: System checks for required columns and data types
3. **Review Summary**: See dataset statistics and quality indicators
4. **Process Data**: Click "Process Data" to clean and prepare data

#### Outputs:
- ✅ Data validation results
- ✅ Processing statistics
- ✅ Quality metrics (completeness, variation)
- ✅ Feature engineering summary

### **Tab 2: Model Training**

#### Features:
- **Model Selection**: Prophet and ARIMA model training
- **ML Metrics**: R², RMSE, MAE, MAPE evaluation
- **Model Comparison**: Side-by-side performance analysis
- **Quality Assessment**: Automatic model quality rating

#### Steps:
1. **Configure Models**: Adjust parameters if needed
2. **Train Models**: Click "Train Models" with progress tracking
3. **Review Metrics**: Examine R², RMSE, MAE, MAPE for each model
4. **Compare Performance**: See model comparison and ensemble recommendations

#### Outputs:
- ✅ Model performance metrics (R², RMSE, MAE, MAPE)
- ✅ Model quality assessment (Excellent/Good/Fair/Poor)
- ✅ Training configuration details
- ✅ Ensemble recommendations

### **Tab 3: Forecast Generation**

#### Features:
- **Forecast Configuration**: Set horizon and parameters
- **Interactive Visualization**: Plotly charts with confidence intervals
- **Comprehensive Analysis**: Trends, volatility, risk assessment
- **Export Options**: CSV, JSON, TXT downloads

#### Steps:
1. **Set Horizon**: Choose forecast duration (1-90 days)
2. **Generate Forecast**: Click "Generate Forecast" with progress tracking
3. **Review Results**: Examine interactive charts and analysis
4. **Export Data**: Download results in preferred format

#### Outputs:
- ✅ Interactive forecast visualization
- ✅ Comprehensive forecast analysis (trends, volatility)
- ✅ Confidence interval analysis
- ✅ Model contribution analysis
- ✅ Detailed forecast table with risk indicators
- ✅ Export capabilities

### **Tab 4: Health Analysis & Recommendations**

#### Features:
- **AQI Assessment**: Current air quality status
- **Risk Analysis**: Health impact evaluation
- **Population Impact**: General vs sensitive groups
- **Actionable Recommendations**: Specific health guidance

#### Steps:
1. **Review Current Status**: See current AQI and health recommendations
2. **Analyze Risks**: Examine risk periods and health impacts
3. **Assess Population Impact**: Review impacts on different groups
4. **Follow Recommendations**: Get actionable health guidance

#### Outputs:
- ✅ Current AQI status with recommendations
- ✅ Health impact analysis with scoring
- ✅ Category-specific health guidelines
- ✅ Risk period analysis with detailed breakdown
- ✅ Population impact assessment
- ✅ Actionable recommendations summary

### **Web Interface Features**

#### **Interactive Elements**
- **Progress Bars**: Real-time progress tracking
- **Status Messages**: Clear feedback on operations
- **Expandable Sections**: Detailed information on demand
- **Hover Details**: Interactive chart tooltips

#### **Visual Indicators**
- **Color-coded Risk Levels**: 🟢🟡🟠🔴🟣⚫
- **Quality Indicators**: Excellent/Good/Fair/Poor ratings
- **Status Icons**: ✅ success, ⚠️ warning, ❌ error

#### **Export Capabilities**
- **CSV**: Complete forecast data with all columns
- **JSON**: Machine-readable format for APIs
- **TXT**: Human-readable summary report
- **Timestamped Filenames**: Automatic organization

---

## 📊 Data Requirements

### Required Data Format

Your data must be a CSV file with the following structure:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| **Timestamp** | DateTime | ✅ | Date/time of measurement |
| **AQI** | Numeric | ✅ | Air Quality Index value |
| **PM2.5, PM10, NO2, etc.** | Numeric | ❌ | Pollutant measurements |

### Sample Data Format

```csv
Timestamp,AQI,PM2.5,PM10,NO2,CO,SO2,O3
2023-01-01,85,35.2,45.1,28.3,0.8,12.5,65.2
2023-01-02,92,38.7,48.9,31.2,0.9,14.1,68.7
2023-01-03,78,32.1,42.3,25.8,0.7,11.2,62.3
```

### Data Quality Guidelines

- **Minimum 30 days** of data for reliable forecasts
- **Daily measurements** recommended
- **Missing data** should be <30% of total
- **Outliers** will be automatically detected and handled

### Model Performance Expectations

#### Realistic MAPE Values
- **Excellent**: 5-15% (very accurate predictions)
- **Good**: 15-25% (accurate predictions)
- **Fair**: 25-40% (moderate accuracy)
- **Poor**: 40-100% (low accuracy)

#### Quality Assessment Standards
- **Excellent**: R² ≥ 0.7 AND Accuracy ≥ 80%
- **Good**: R² ≥ 0.5 AND Accuracy ≥ 75%
- **Fair**: R² ≥ 0.3 AND Accuracy ≥ 70%
- **Poor**: Below Fair thresholds

**Note**: Air quality data naturally has higher variability than other time series, so these thresholds are adjusted for realistic air quality forecasting standards.

---

## ⚙️ Configuration

### Understanding config.yaml

The system behavior is controlled through `config.yaml`. Here are the key sections:

#### Data Processing
```yaml
data:
  date_column: "Timestamp"        # Your date column name
  target_column: "AQI"           # Target variable for prediction
  missing_threshold: 0.3          # Max missing data ratio (30%)
  outlier_threshold: 3.0          # Standard deviation threshold
```

#### Model Parameters
```yaml
prophet:
  changepoint_prior_scale: 0.1    # Model flexibility (0.01-0.5)
  seasonality_mode: multiplicative # Seasonal pattern type
  
arima:
  max_p: 5                        # Maximum AR order
  max_q: 5                        # Maximum MA order
  seasonal: true                  # Enable seasonal components
```

#### Forecasting
```yaml
forecasting:
  default_horizon: 14             # Days to forecast
  prophet_weight: 0.7             # Ensemble weight for Prophet
  arima_weight: 0.3               # Ensemble weight for ARIMA
  confidence_level: 0.95          # Confidence interval (0.8-0.99)
```

### Custom Configuration

```python
from src.config import Config

# Load and modify configuration
config = Config('config.yaml')
config.set('forecasting.default_horizon', 30)
config.set('prophet.changepoint_prior_scale', 0.05)
config.save_config('custom_config.yaml')
```

---

## 💡 Usage Examples

### Example 1: Basic Forecasting

```python
from src import AirPollutionSystem

# Initialize with default config
system = AirPollutionSystem()

# Load your data
data = system.load_data('data/daily_aqi.csv')

# Run complete pipeline
results = system.run_complete_pipeline(
    data_file='data/daily_aqi.csv',
    forecast_horizon=14,
    output_dir='results'
)

print(f"Forecast generated for {len(results['forecasts'])} days")
```

### Example 2: Custom Model Parameters

```python
from src.config import Config
from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from src.forecaster import Forecaster

# Create custom configuration
config = Config()
config.set('prophet.changepoint_prior_scale', 0.05)  # More conservative
config.set('arima.max_p', 3)                         # Faster training
config.set('forecasting.prophet_weight', 0.8)       # Favor Prophet

# Process and train
processor = DataProcessor(config)
trainer = ModelTrainer(config)
forecaster = Forecaster(config)

# Execute pipeline
processed_data = processor.process_data(data)
prophet_model = trainer.train_prophet(processed_data)
arima_model = trainer.train_arima(processed_data)
forecasts = forecaster.generate_ensemble_forecast(
    prophet_model, arima_model, processed_data, horizon=21
)
```

### Example 3: Performance Monitoring

```python
from src.utils import PerformanceMonitor

# Monitor system performance
monitor = PerformanceMonitor()

with monitor.measure("total_pipeline"):
    # Your forecasting code here
    results = system.run_complete_pipeline(
        data_file='data/daily_aqi.csv',
        forecast_horizon=14
    )

# View performance metrics
summary = monitor.get_summary()
print(f"Total execution time: {summary['total_time']:.2f} seconds")
```

### Example 4: Custom Visualizations

```python
from src.visualizer import Visualizer

# Create custom visualizations
visualizer = Visualizer(config, 'custom_outputs')

# Generate specific plots
visualizer.plot_historical_data(processed_data, 'my_history')
visualizer.plot_ensemble_forecast(processed_data, forecasts, 'my_forecast')
visualizer.plot_aqi_categories(forecasts, 'my_categories')
visualizer.create_forecast_dashboard(processed_data, forecasts, 'my_dashboard')
```

---

## 📈 Understanding Results

### Forecast Output Structure

```python
forecasts = system.generate_forecast(models, data, horizon=14)

# Each forecast contains:
for forecast in forecasts:
    print(f"Date: {forecast['date']}")
    print(f"Predicted AQI: {forecast['forecast']:.2f}")
    print(f"Confidence Interval: {forecast['lower_bound']:.2f} - {forecast['upper_bound']:.2f}")
    print(f"AQI Category: {forecast['aqi_category']}")
    print(f"Health Recommendation: {forecast['health_recommendation']}")
```

### AQI Categories and Health Impact

| AQI Range | Category | Color | Health Impact |
|-----------|----------|-------|---------------|
| 0-50 | Good | Green | Enjoy outdoor activities |
| 51-100 | Moderate | Yellow | Sensitive groups should limit prolonged outdoor exertion |
| 101-150 | Unhealthy for Sensitive Groups | Orange | Reduce prolonged outdoor exertion |
| 151-200 | Unhealthy | Red | Everyone should reduce outdoor activities |
| 201-300 | Very Unhealthy | Purple | Avoid prolonged outdoor exertion |
| 301+ | Hazardous | Maroon | Avoid all outdoor activities |

### Performance Metrics

```python
# Get model performance summary
summary = forecaster.get_forecast_summary(forecasts)

print(f"Average AQI: {summary['aqi_statistics']['mean']:.2f}")
print(f"AQI Range: {summary['aqi_statistics']['min']:.2f} - {summary['aqi_statistics']['max']:.2f}")
print(f"Confidence Level: {summary['confidence_statistics']['mean_confidence']:.3f}")

# Category distribution
for category, count in summary['category_distribution'].items():
    percentage = (count / len(forecasts)) * 100
    print(f"{category}: {count} days ({percentage:.1f}%)")
```

---

## 🔧 Advanced Features

### 1. Ensemble Weight Optimization

```python
# Optimize ensemble weights based on historical performance
from src.forecaster import Forecaster

forecaster = Forecaster(config)
optimized_weights = forecaster.optimize_ensemble_weights(
    prophet_model, arima_model, validation_data
)

print(f"Optimized Prophet weight: {optimized_weights['prophet']:.3f}")
print(f"Optimized ARIMA weight: {optimized_weights['arima']:.3f}")
```

### 2. Critical Period Identification

```python
# Identify high-risk periods in forecasts
critical_periods = forecaster.identify_critical_periods(forecasts)

print("Critical Periods (AQI > 150):")
for date, info in critical_periods.iterrows():
    print(f"{date.strftime('%Y-%m-%d')}: AQI {info['Forecasted_AQI']:.1f} ({info['AQI_Category']})")
```

### 3. Custom Health Recommendations

```python
# Define custom health recommendations
custom_recommendations = {
    'Good': 'Perfect day for outdoor activities!',
    'Moderate': 'Sensitive individuals should consider limiting prolonged outdoor exertion.',
    'Unhealthy for Sensitive Groups': 'Children and elderly should avoid prolonged outdoor activities.',
    'Unhealthy': 'Everyone should avoid outdoor activities.',
    'Very Unhealthy': 'Stay indoors and avoid all outdoor activities.',
    'Hazardous': 'Emergency conditions - stay indoors and use air purifiers.'
}

# Apply custom recommendations
forecaster.set_health_recommendations(custom_recommendations)
```

### 4. Batch Processing

```python
# Process multiple data files
import glob
from src import AirPollutionSystem

system = AirPollutionSystem()

data_files = glob.glob('data/*.csv')
for data_file in data_files:
    print(f"Processing {data_file}...")
    results = system.run_complete_pipeline(
        data_file=data_file,
        output_dir=f"results/{data_file.split('/')[-1].replace('.csv', '')}"
    )
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Memory Errors
**Problem**: System runs out of memory during training
**Solutions**:
```yaml
# In config.yaml
performance:
  memory_optimization: true
  parallel_processing: false

# Reduce forecast horizon
forecasting:
  default_horizon: 7  # Instead of 30
```

#### 2. Slow Performance
**Problem**: Model training takes too long
**Solutions**:
```yaml
# Optimize ARIMA parameters
arima:
  max_p: 3  # Reduce from 5
  max_q: 3  # Reduce from 5
  stepwise: true  # Enable stepwise selection

# Reduce Prophet uncertainty samples
prophet:
  uncertainty_samples: 500  # Reduce from 1000
```

#### 3. Poor Forecast Accuracy
**Problem**: Forecasts are not accurate
**Solutions**:
- Check data quality and consistency
- Increase historical data length
- Adjust model parameters:
```yaml
prophet:
  changepoint_prior_scale: 0.05  # More flexible

forecasting:
  prophet_weight: 0.8  # Favor Prophet if it performs better
  arima_weight: 0.2
```

#### 4. Model Training Failures
**Problem**: Models fail to train
**Solutions**:
- Verify data format and column names
- Check for missing values in target column
- Ensure sufficient data (minimum 30 days)
- Review error logs with verbose mode:
```bash
python main.py --verbose
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use the built-in function
from src.utils import setup_logging
setup_logging(verbose=True)
```

---

## 📚 Best Practices

### Data Preparation
1. **Consistent Timestamps**: Use the same time format throughout
2. **Regular Measurements**: Daily data provides best results
3. **Quality Control**: Remove obvious errors before processing
4. **Sufficient History**: Minimum 30 days, ideally 6+ months

### Model Configuration
1. **Start with Defaults**: Use default parameters initially
2. **Validate Performance**: Test on holdout data when possible
3. **Monitor Confidence**: Check prediction intervals regularly
4. **Seasonal Awareness**: Consider seasonal patterns in your data

### Operational Guidelines
1. **Regular Updates**: Retrain models monthly with new data
2. **Performance Monitoring**: Track execution time and accuracy
3. **Result Validation**: Review forecasts before public release
4. **Backup Configuration**: Save working configurations

### Output Management
1. **Organized Storage**: Use date-stamped output directories
2. **Result Documentation**: Keep forecast reports for analysis
3. **Visualization Review**: Check plots for data quality issues
4. **Archive Old Results**: Maintain historical forecast records

---

## 📞 Getting Help

### Resources
- **Example Scripts**: See `example_usage.py` for detailed examples
- **Configuration Reference**: Review `config.yaml` for all options
- **API Documentation**: Check docstrings in source code
- **Performance Tips**: See `Basis files/optimization_documentation.txt`

### Support Channels
- **Documentation**: Review this guide and README.md
- **Examples**: Run `python example_usage.py` to see system in action
- **Configuration**: Modify `config.yaml` to customize behavior
- **Logging**: Use `--verbose` flag for detailed debugging information

---

## 🔄 Quick Reference

### Essential Commands
```bash
# Basic forecast
python main.py

# Custom configuration
python main.py --config custom_config.yaml

# Specific forecast horizon
python main.py --days 30

# Different data file
python main.py --data data/new_data.csv --output results

# Verbose output
python main.py --verbose
```

### Key Python Functions
```python
# Complete pipeline
system.run_complete_pipeline(data_file, forecast_horizon, output_dir)

# Individual steps
system.load_data(file_path)
system.process_data(data)
system.train_models(data)
system.generate_forecast(models, data, horizon)
system.create_visualizations(data, forecasts)
```

### Configuration Quick Edit
```python
from src.config import Config
config = Config('config.yaml')
config.set('forecasting.default_horizon', 21)  # 3 weeks
config.set('prophet.changepoint_prior_scale', 0.05)  # More conservative
config.save_config()
```


## 🔄 Changes - 2026-02-27 08:55:28

### Other
- Updated `guide_updater.py`


---

---

**Air Quality Commission**  
*Protecting public health through accurate air quality forecasting*

For the most up-to-date information and support, please refer to the system documentation and example files included with this distribution.
