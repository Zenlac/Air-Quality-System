# Air Pollution Forecasting System

A comprehensive Python-based system for air quality prediction using advanced machine learning models. This system combines Prophet and ARIMA models through ensemble methods to provide accurate air quality forecasts with comprehensive health analysis and standard ML metrics evaluation.

## 🌟 Features

### **Core Forecasting**
- **Advanced Time Series Forecasting**: Uses Prophet and ARIMA models optimized for air quality data
- **Ensemble Methods**: Combines multiple models for improved accuracy with dynamic weighting
- **ML Metrics Evaluation**: R², RMSE, MAE, MAPE for comprehensive model assessment
- **Confidence Intervals**: 80% confidence bounds for uncertainty quantification
- **Multiple Forecast Horizons**: Short to long-term forecasting (1-90+ days)

### **Data Processing**
- **Strict Format Validation**: Ensures data consistency with exact column requirements
- **Automated Data Cleaning**: Handles missing values and outliers
- **Feature Engineering**: Time-based and pollutant feature extraction
- **Data Quality Assessment**: Completeness and variation metrics
- **EMB Data Support**: Conversion scripts for EMB format data

### **Health Analysis**
- **AQI Categorization**: All 6 AQI categories with specific recommendations
- **Risk Period Analysis**: Identifies consecutive high-AQI days
- **Population Impact Assessment**: General vs sensitive groups analysis
- **Health Scoring**: Overall impact assessment (0-100 scale)
- **Actionable Recommendations**: Specific guidance for different scenarios

### **User Interface**
- **Comprehensive Web UI**: 4-tab interface with full functionality
- **Interactive Visualizations**: Plotly charts with hover details
- **Progress Tracking**: Real-time status updates and progress bars
- **Export Capabilities**: CSV, JSON, TXT format downloads
- **Responsive Design**: Works on all device sizes

### **Technical Features**
- **Performance Optimized**: Efficient processing with minimal memory usage
- **Configurable**: YAML-based configuration system
- **Modular Architecture**: Clean, maintainable code structure
- **Error Handling**: Multiple fallback mechanisms
- **Comprehensive Testing**: Verification scripts for all components

## 🚀 Quick Start

### 📋 Installation

**For complete installation instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

1. **Clone the repository**:
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

5. **Prepare your data**:
⚠️ **Important**: The system requires data files to exactly match the format of `sample_air_quality_data.csv`. See [STRICT_FORMAT_REQUIREMENTS.md](STRICT_FORMAT_REQUIREMENTS.md) for detailed specifications.

### Running the System

#### **Option 1: Web Interface (Recommended)**
```bash
python run_ui.py
```
The web interface will open at `http://localhost:8501` with:
- **Data Upload & Processing**: Upload and validate your data
- **Model Training**: Train Prophet and ARIMA models with ML metrics
- **Forecast Generation**: Generate forecasts with confidence intervals
- **Health Analysis**: Analyze health impacts and get recommendations

#### **Option 2: Command Line**
```bash
python main.py --data csv_files/data_files/sample_air_quality_data.csv --output outputs
```

### Data Format Requirements

The system **only accepts CSV files with this exact format**:

**Required Columns (14 total)**:
```
Timestamp,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene,Xylene
```

**Key Requirements**:
- `Timestamp` column must contain valid datetime values
- `AQI` column must have numeric values (cannot be empty)
- All 14 columns must be present with exact names
- No missing AQI values allowed

### EMB Data Support

For EMB format data:
1. **Convert EMB data**:
```bash
python convert_emb_data.py --input csv_files/data_files/EMB-CEPMOo1-year.csv --output csv_files/data_files/EMB_converted.csv
```

2. **Use converted file**: Upload `csv_files/data_files/EMB_converted.csv` (not original EMB file)

3. **Verify format**: Ensure all 14 required columns are present
- See `csv_files/data_files/sample_air_quality_data.csv` for reference format

### Basic Usage

```python
from src import AirPollutionSystem

# Initialize system
system = AirPollutionSystem(config_path='config.yaml')

# Load and process data (must match required format)
data = system.load_data('sample_air_quality_data.csv')
processed_data = system.process_data(data)

# Train models
models = system.train_models(processed_data)

# Generate forecasts
forecasts = system.generate_forecast(models, processed_data, horizon=31)

# Create visualizations
system.create_visualizations(processed_data, forecasts)
```

## 📊 System Architecture

The system is built with a modular architecture:

```
air-pollution-forecasting/
├── main.py                 # Main entry point
├── config.yaml            # Configuration file
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
├── src/                   # Source code
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── data_processor.py  # Data processing and cleaning
│   ├── model_trainer.py   # Model training (Prophet, ARIMA)
│   ├── forecaster.py      # Ensemble forecasting
│   ├── visualizer.py      # Visualization creation
│   └── utils.py           # Utility functions
├── data/                  # Data directory
├── outputs/               # Output directory
└── docs/                  # Documentation
```

## 🔧 Configuration

The system uses `config.yaml` for all configuration options:

### Data Processing
```yaml
data:
  date_column: "Timestamp"
  target_column: "AQI"
  pollutant_columns: ["PM2.5", "PM10", "NO", "NO2", ...]
  missing_threshold: 0.3
  outlier_threshold: 3.0
```

### Model Parameters
```yaml
prophet:
  yearly_seasonality: true
  weekly_seasonality: true
  seasonality_mode: "multiplicative"
  changepoint_prior_scale: 0.05

arima:
  max_p: 3
  max_q: 3
  seasonal: true
  m: 7
  stepwise: true
```

### Forecasting
```yaml
forecasting:
  default_horizon: 31
  prophet_weight: 0.6
  arima_weight: 0.4
  confidence_level: 0.95
```

## 📈 Models Used

### Prophet
- Optimized for time series with multiple seasonalities
- Handles holidays and special events
- Provides uncertainty intervals
- Configurable changepoint detection

### ARIMA
- Auto ARIMA with optimized parameter search
- Seasonal decomposition support
- Statistical model selection criteria
- Robust to non-stationary data

### Ensemble Method
- Weighted averaging of model predictions
- Confidence interval combination
- Performance-based weight optimization
- Robustness to individual model failures

## 🎨 Visualizations

The system generates comprehensive visualizations:

1. **Historical Data Analysis**
   - Time series plots
   - Monthly distributions
   - AQI histograms
   - Yearly comparisons

2. **Model Forecasts**
   - Prophet forecast plots
   - ARIMA predictions
   - Ensemble forecasts
   - Confidence intervals

3. **Model Comparison**
   - Performance metrics
   - Forecast differences
   - Confidence interval comparison
   - Accuracy analysis

4. **Health Impact Analysis**
   - AQI category distributions
   - Risk level timelines
   - Health recommendations
   - Critical period identification

5. **Comprehensive Dashboard**
   - Multi-panel overview
   - Key statistics
   - Recommendations
   - Performance summary

## 📊 Performance Metrics

The system provides comprehensive ML metrics for model evaluation:

### **Standard ML Metrics**
- **R² (R-squared)**: Coefficient of determination (0-1, higher is better)
- **RMSE**: Root Mean Square Error (lower is better)
- **MAE**: Mean Absolute Error (lower is better)
- **MAPE**: Mean Absolute Percentage Error (lower is better)
- **Accuracy**: Model accuracy percentage

### **Model Quality Assessment**
- **Excellent**: R² > 0.8 (85%+ accuracy)
- **Good**: R² 0.6-0.8 (70-85% accuracy)
- **Fair**: R² 0.4-0.6 (55-70% accuracy)
- **Poor**: R² < 0.4 (<55% accuracy)

### **Additional Metrics**
- **Coverage**: Confidence interval coverage
- **Execution Time**: Performance monitoring
- **Model Correlation**: Agreement between Prophet and ARIMA
- **Ensemble Weights**: Model contribution percentages

## 🏥 Health Analysis Features

The system provides comprehensive health impact analysis:

### **AQI Categorization**
- **Good (0-50)**: Normal outdoor activities
- **Moderate (51-100)**: Sensitive groups limit prolonged exertion
- **Unhealthy for Sensitive Groups (101-150)**: Reduce outdoor activities
- **Unhealthy (151-200)**: Everyone limit outdoor activities
- **Very Unhealthy (201-300)**: Avoid outdoor activities
- **Hazardous (301+)**: Stay indoors, use air purifiers

### **Risk Assessment**
- **Risk Period Analysis**: Consecutive high-AQI days
- **Population Impact**: General vs sensitive groups
- **Health Score**: Overall impact (0-100 scale)
- **Cumulative Exposure**: Total AQI exposure over time

### **Actionable Recommendations**
- **General Population**: Activity recommendations
- **Sensitive Groups**: Specific precautions
- **Protective Measures**: Indoor air quality guidance
- **Medical Help Indicators**: When to seek care

## 🛠️ Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --config PATH     Configuration file path (default: config.yaml)
  --data PATH       Data file path (default: data/air_quality_data.csv)
  --output PATH     Output directory (default: outputs)
  --days INTEGER    Forecast horizon in days (default: 31)
  --verbose         Enable verbose logging
```

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher (3.9+ recommended)
- **RAM**: 8GB minimum (4GB minimum for basic operations)
- **CPU**: 4+ cores recommended
- **Storage**: 2GB disk space minimum
- **Browser**: Chrome, Firefox, Safari, or Edge (for web UI)

### 📦 Installation Requirements
**For detailed installation steps, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

### Python Dependencies
See `documentation/requirements.txt` for complete list:

**Core Dependencies**:
- `pandas >= 2.0.0` - Data processing
- `numpy >= 1.24.0` - Numerical operations
- `scipy >= 1.10.0` - Scientific computing

**Machine Learning**:
- `scikit-learn >= 1.3.0` - ML metrics
- `prophet >= 1.1.0` - Time series forecasting
- `pmdarima >= 2.0.0` - ARIMA modeling
- `statsmodels >= 0.14.0` - Statistical models

**Visualization**:
- `matplotlib >= 3.7.0` - Plotting
- `seaborn >= 0.12.0` - Statistical visualization
- `plotly >= 5.15.0` - Interactive charts

**Web Interface**:
- `streamlit >= 1.28.0` - Web UI framework

**Utilities**:
- `PyYAML >= 6.0` - Configuration
- `psutil >= 5.9.0` - System monitoring
- `loguru >= 0.7.0` - Logging

## 🧪 Testing & Verification

### **System Tests**
```bash
# Test ML metrics implementation
python test_metrics.py

# Test UI timestamp handling
python test_ui_fix.py

# Compare EMB data formats
python compare_emb_data.py

# Test sample data validation
python test_sample_data.py
```

### **Validation Scripts**
- `test_metrics.py` - Verifies R², RMSE, MAE, MAPE calculations
- `test_ui_fix.py` - Tests timestamp handling in web interface
- `diagnose_timestamp_error.py` - Diagnoses data format issues
- `convert_emb_data.py` - Converts EMB format to strict format

### **Data Validation**
```bash
# Validate data format
python -c "
from src.data_processor import DataProcessor
from src.config import Config
processor = DataProcessor(Config('config.yaml'))
try:
    data = processor.load_data('sample_air_quality_data.csv')
    print('✅ Data validation passed')
except Exception as e:
    print(f'❌ Validation failed: {e}')
"
```

## 📚 API Reference

### DataProcessor
```python
processor = DataProcessor(config)
df = processor.load_data('data.csv')
processed = processor.process_data(df)
```

### ModelTrainer
```python
trainer = ModelTrainer(config)
prophet_model = trainer.train_prophet(data)
arima_model = trainer.train_arima(data)
```

### Forecaster
```python
forecaster = Forecaster(config)
forecasts = forecaster.generate_ensemble_forecast(
    prophet_model, arima_model, data, horizon=31
)
```

### Visualizer
```python
visualizer = Visualizer(config, 'outputs')
visualizer.create_all_visualizations(data, forecasts, prophet_model, arima_model)
```

## 🔍 Troubleshooting

### Common Issues

1. **Memory Errors**
   - Reduce forecast horizon
   - Enable memory optimization in config
   - Use smaller dataset for testing

2. **Slow Performance**
   - Enable performance monitoring
   - Check ARIMA parameter limits
   - Reduce Prophet uncertainty samples

3. **Model Training Failures**
   - Check data quality and format
   - Verify configuration parameters
   - Review error logs

### Debug Mode

Enable verbose logging for debugging:

```bash
python main.py --verbose --config debug_config.yaml
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Email: info@airquality.gov
- Issues: [GitHub Issues](https://github.com/airquality/air-pollution-forecasting/issues)
- Documentation: [ReadTheDocs](https://air-pollution-forecasting.readthedocs.io/)

## 🗺️ Roadmap

- [ ] Add support for additional ML models (LSTM, XGBoost)
- [ ] Implement real-time data processing
- [ ] Add geographic location support
- [ ] Create web interface
- [ ] Add API endpoints
- [ ] Implement model versioning
- [ ] Add automated model retraining
- [ ] Support for multiple pollutants forecasting

## 📈 Version History

### v1.0.0 (2026-02-25)
- Initial release
- Prophet and ARIMA model integration
- Ensemble forecasting
- Comprehensive visualizations
- Performance optimization
- Health recommendations
- Configuration management

---

**Air Quality Commission**  
*Protecting public health through accurate air quality forecasting*
