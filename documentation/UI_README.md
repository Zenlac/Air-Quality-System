# Air Pollution Forecasting System - Web UI

A user-friendly web interface for the Air Pollution Forecasting System built with Streamlit.

## 🌟 Features

### 📊 Data Management
- **File Upload**: Easy CSV file upload with drag-and-drop support
- **Data Preview**: Instant preview of uploaded data with statistics
- **Data Processing**: Automated data cleaning and preprocessing
- **Format Validation**: Checks for required columns (Timestamp, AQI)
- **Data Requirements Warning**: Prominent guidance for raw data users with format specifications

### 🤖 Model Training
- **One-Click Training**: Train Prophet and ARIMA models with a single click
- **Progress Tracking**: Real-time progress indicators during training
- **Model Configuration**: Adjustable model parameters via sidebar
- **Performance Metrics**: Automatic model evaluation and display

### 📈 Forecasting
- **Interactive Forecasts**: Generate forecasts for 1-90 days
- **Confidence Intervals**: Visualize prediction uncertainty
- **Ensemble Methods**: Combined Prophet + ARIMA predictions
- **Model Comparison**: Compare individual model performances

### 🏥 Health Analysis
- **AQI Categories**: Real-time AQI categorization (Good to Hazardous)
- **Health Recommendations**: Personalized health advice based on AQI
- **Risk Timeline**: Visual timeline of health risk periods
- **Alert System**: Automatic alerts for unhealthy air quality periods

### 📊 Visualizations
- **Interactive Charts**: Plotly-based interactive visualizations
- **AQI Gauge**: Real-time AQI gauge with color coding
- **Forecast Plots**: Detailed forecast with confidence bands
- **Health Impact Timeline**: Color-coded health risk visualization

### 💾 Export & Download
- **CSV Export**: Download forecast results in CSV format
- **Detailed Reports**: Comprehensive forecast reports with health recommendations
- **Data Preservation**: Save processed data and model outputs

## 🚀 Quick Start

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Launch the web interface**:
```bash
python run_ui.py
```

Or run directly with Streamlit:
```bash
streamlit run app.py
```

3. **Open your browser**:
   - The interface will automatically open at `http://localhost:8501`
   - If not opened automatically, visit the URL manually

## 📋 Usage Guide

### Important: Data Requirements Notice
When you first open the web interface, you'll see a prominent **"📋 Important: Data Requirements & Recommendations"** section at the top. This expandable warning provides:

- **Required Data Format**: Essential columns (Timestamp, AQI) and accepted naming conventions
- **Data Quality Recommendations**: Minimum data requirements (30+ days, consistent intervals)
- **Common Issues to Avoid**: Format problems that cause errors
- **Pro Tip**: Information about automatic AQI calculation from pollutant data

**⚠️ Always review this section before uploading data to avoid processing errors!**

### Step 1: Upload Data
1. Click the "📊 Data Upload" tab
2. Upload your CSV file using the file uploader in the sidebar
3. Review the data preview and statistics
4. Click "🔄 Process Data" to prepare the data

**Expected CSV Format**:
- `Timestamp`: Date/time column (format: YYYY-MM-DD HH:MM:SS)
- `AQI`: Air Quality Index values
- Optional: PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, Xylene

### Step 2: Train Models
1. Navigate to the "🤖 Model Training" tab
2. Adjust model parameters in the sidebar if needed:
   - **Forecast Horizon**: Number of days to forecast (1-90)
   - **Prophet Weight**: Weight for Prophet model (0.0-1.0)
   - **Confidence Level**: Prediction confidence (80%-99%)
3. Click "🚀 Train Models" to start training
4. Monitor progress and wait for completion

### Step 3: Generate Forecasts
1. Go to the "📈 Forecasts" tab
2. Click "🔮 Generate Forecasts" to create predictions
3. View interactive forecast visualizations
4. Review forecast summary statistics
5. Examine detailed forecast table

### Step 4: Health Analysis
1. Navigate to the "🏥 Health Analysis" tab
2. View current AQI gauge and health recommendations
3. Review health impact timeline
4. Check for high-risk periods
5. Download results if needed

## ⚙️ Configuration Options

### Model Parameters
- **Forecast Horizon**: 1-90 days (default: 14)
- **Prophet Weight**: 0.0-1.0 (default: 0.7)
- **ARIMA Weight**: Automatically calculated (1.0 - Prophet Weight)
- **Confidence Level**: 80%, 85%, 90%, 95%, 99% (default: 95%)

### Data Requirements
- **Format**: CSV file
- **Required Columns**: Timestamp, AQI
- **Optional Columns**: PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, Xylene
- **Date Format**: YYYY-MM-DD HH:MM:SS (auto-detected)

## 🎨 UI Features

### Responsive Design
- **Wide Layout**: Optimized for desktop and tablet viewing
- **Sidebar Navigation**: Easy access to configuration options
- **Tabbed Interface**: Organized workflow with clear sections
- **Progress Indicators**: Real-time feedback during operations

### Interactive Elements
- **File Upload**: Drag-and-drop CSV upload
- **Sliders**: Adjustable model parameters
- **Buttons**: One-click operations
- **Charts**: Interactive Plotly visualizations
- **Tables**: Sortable and scrollable data tables

### Visual Feedback
- **Success Messages**: Green notifications for successful operations
- **Error Messages**: Red alerts for issues and errors
- **Warnings**: Yellow cautions for missing requirements
- **Progress Bars**: Visual progress tracking

## 📊 AQI Categories

| AQI Range | Category | Color | Health Recommendation |
|-----------|----------|-------|----------------------|
| 0-50 | Good | Green | Enjoy outdoor activities |
| 51-100 | Moderate | Yellow | Sensitive groups should take precautions |
| 101-150 | Unhealthy for Sensitive Groups | Orange | Reduce prolonged outdoor exertion |
| 151-200 | Unhealthy | Red | Everyone should reduce outdoor activities |
| 201-300 | Very Unhealthy | Purple | Avoid prolonged outdoor exertion |
| 301+ | Hazardous | Maroon | Avoid all outdoor activities |

## 🔧 Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file format (must be CSV)
   - Verify required columns (Timestamp, AQI)
   - Ensure file size is reasonable (<100MB)

2. **Model Training Errors**
   - Check data quality and completeness
   - Ensure sufficient historical data (>30 days recommended)
   - Verify date format consistency

3. **Forecast Generation Fails**
   - Ensure models are trained successfully
   - Check forecast horizon (1-90 days)
   - Verify data processing completed

4. **Visualization Issues**
   - Refresh the browser page
   - Check browser console for errors
   - Ensure Plotly is loaded correctly

### Performance Tips

- **Large Datasets**: Process in chunks for better performance
- **Memory Usage**: Close other applications if memory is limited
- **Training Time**: Reduce forecast horizon for faster results
- **Browser**: Use modern browsers (Chrome, Firefox, Safari, Edge)

## 📱 Browser Compatibility

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## 🛠️ Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Visualizations**: Plotly interactive charts
- **Backend**: Python-based forecasting engine
- **Models**: Prophet and ARIMA time series models

### Dependencies
- `streamlit>=1.28.0`: Web interface framework
- `plotly>=5.15.0`: Interactive visualizations
- `pandas>=2.0.0`: Data processing
- `prophet>=1.1.0`: Time series forecasting
- `pmdarima>=2.0.0`: ARIMA modeling

## 📞 Support

For issues and support:
- **Documentation**: Check this README and system documentation
- **Issues**: Report bugs and feature requests
- **Email**: Contact system administrators

---

**Air Quality Commission**  
*Making air quality forecasting accessible to everyone*
