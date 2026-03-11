# Frequently Asked Questions (FAQ)

## 📋 **Table of Contents**
1. [General Questions](#general-questions)
2. [Data Requirements](#data-requirements)
3. [Model Training](#model-training)
4. [Forecasting](#forecasting)
5. [Metrics & Performance](#metrics--performance)
6. [Health Analysis](#health-analysis)
7. [Technical Issues](#technical-issues)
8. [Troubleshooting](#troubleshooting)

---

## 🤔 **General Questions**

### **Q1: What is the Air Pollution Forecasting System?**
**A:** The system is a comprehensive web-based platform that forecasts air quality using machine learning models (Prophet and ARIMA). It processes historical air quality data, trains predictive models, generates forecasts, and provides health impact analysis with actionable recommendations.

### **Q2: Who is this system for?**
**A:** The system is designed for:
- **Environmental agencies** monitoring air quality
- **Public health officials** assessing health impacts
- **Researchers** studying air pollution patterns
- **General public** interested in air quality forecasts
- **Policy makers** making environmental decisions

### **Q3: What air quality parameters does the system support?**
**A:** The system supports exactly 13 parameters in this specific format:
- **AQI** (Air Quality Index) - Primary target (required, no missing values)
- **PM2.5, PM10** (Particulate Matter)
- **NO2, NO, NOx** (Nitrogen Oxides)
- **CO** (Carbon Monoxide)
- **NH3** (Ammonia)
- **SO2** (Sulfur Dioxide)
- **O3** (Ozone)
- **Benzene, Toluene, Xylene** (Volatile Organic Compounds)
- **Timestamp** - Required date column (exact name required)

### **Q3a: Why does the system require strict data format?**
**A:** The system implements strict format requirements to:
- **Eliminate "Timestamp" errors** that occurred with flexible formats
- **Ensure consistency** across all users and deployments
- **Improve reliability** and predictable behavior
- **Reduce edge cases** and maintenance complexity
- **Provide clear error messages** with specific guidance

### **Q3b: What exactly are the strict format requirements?**
**A:** The system requires:
- **Exact column names**: No alternative names accepted
- **All 14 columns present**: Missing columns cause rejection
- **Timestamp column**: Must be named 'Timestamp' (not 'Date', 'date', etc.)
- **AQI column**: Must contain numeric data with no missing values
- **CSV format**: Standard comma-separated values
- **Valid dates**: Timestamp must be in datetime format

### **Q3c: Can I use EMB data with the system?**
**A:** EMB data must be converted first:
1. **Original EMB data is rejected**: Has 'Date' column, not 'Timestamp'
2. **Use conversion script**: `convert_emb_data.py` provided
3. **Convert to strict format**: Follow `sample_air_quality_data.csv`
4. **Verify conversion**: Check all 14 columns are present
5. **Upload converted file**: Not the original EMB file

### **Q4: How accurate are the forecasts?**
**A:** Forecast accuracy depends on:
- **Data quality**: Higher quality data = better accuracy
- **Data quantity**: More historical data = better accuracy
- **Model performance**: Measured by R², RMSE, MAE, MAPE
- **Environmental factors**: Weather, events, seasonal changes

Typical accuracy ranges:
- **Excellent**: R² > 0.8 (85%+ accuracy)
- **Good**: R² 0.6-0.8 (70-85% accuracy)
- **Fair**: R² 0.4-0.6 (55-70% accuracy)
- **Poor**: R² < 0.4 (<55% accuracy)

### **Q5: What are the system requirements?**
**A:** System requirements include:

**Hardware Requirements:**
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (4GB minimum for basic operations)
- **CPU**: 4+ cores recommended
- **Storage**: 2GB disk space minimum
- **Processor**: Any modern CPU

**Software Requirements:**
- **Operating System**: Windows, macOS, or Linux
- **Browser**: Chrome, Firefox, Safari, or Edge
- **Python packages**: All listed in `requirements.txt`

**Data Requirements:**
- **Format**: CSV with strict format
- **Minimum data**: 30 days (10 rows minimum for training)
- **Recommended data**: 180+ days for reliable forecasts
- **Required columns**: All 14 columns with exact names

### **Q6: What Python packages are required?**
**A:** Required packages (see `documentation/requirements.txt`):

**Core Dependencies:**
- `pandas>=2.0.0` - Data processing
- `numpy>=1.24.0` - Numerical operations
- `scipy>=1.10.0` - Scientific computing

**Machine Learning:**
- `scikit-learn>=1.3.0` - ML metrics
- `prophet>=1.1.0` - Time series forecasting
- `pmdarima>=2.0.0` - ARIMA modeling
- `statsmodels>=0.14.0` - Statistical models

**Visualization:**
- `matplotlib>=3.7.0` - Plotting
- `seaborn>=0.12.0` - Statistical visualization
- `plotly>=5.15.0` - Interactive charts

**Web Interface:**
- `streamlit>=1.28.0` - Web UI framework

**Utilities:**
- `PyYAML>=6.0` - Configuration
- `psutil>=5.9.0` - System monitoring
- `tqdm>=4.65.0` - Progress bars
- `loguru>=0.7.0` - Logging

### **Q7: What are the key features of the system?**
**A:** Key features include:

**Data Processing:**
- ✅ **Strict format validation** with clear error messages
- ✅ **Automated data cleaning** and preprocessing
- ✅ **Feature engineering** for time-based and pollutant features
- ✅ **Data quality assessment** and reporting

**Model Training:**
- ✅ **Prophet model** with seasonality handling
- ✅ **ARIMA model** with automatic parameter selection
- ✅ **Cross-validation** for robust evaluation
- ✅ **ML metrics** (R², RMSE, MAE, MAPE)
- ✅ **Model comparison** and quality assessment

**Forecasting:**
- ✅ **Ensemble methods** combining Prophet and ARIMA
- ✅ **Confidence intervals** for uncertainty quantification
- ✅ **Multiple forecast horizons** (short to long-term)
- ✅ **Export capabilities** (CSV, JSON, TXT)

**Health Analysis:**
- ✅ **AQI categorization** with health recommendations
- ✅ **Risk period analysis** for consecutive high-AQI days
- ✅ **Population impact assessment** (general vs sensitive groups)
- ✅ **Actionable recommendations** for different scenarios

**User Interface:**
- ✅ **Comprehensive web interface** with 4 main tabs
- ✅ **Interactive visualizations** with Plotly charts
- ✅ **Progress tracking** and status messages
- ✅ **Error handling** with fallback options

### **Q8: How does the system ensure data quality?**
**A:** Data quality measures include:

**Validation:**
- **Column validation**: All 14 required columns must exist
- **Name validation**: Exact column names required
- **Data type validation**: Timestamp must be datetime, AQI must be numeric
- **Completeness validation**: No missing AQI values allowed

**Quality Metrics:**
- **Data completeness**: Percentage of valid values
- **AQI variation**: Standard deviation assessment
- **Date range**: Time span coverage analysis
- **Quality indicators**: Good/Fair/Poor classification

**Error Handling:**
- **Immediate failure** on format violations
- **Specific error messages** identifying exact issues
- **Helpful guidance** for data correction
- **Reference to sample file** for format guidance

---

## 📊 **Data Requirements**

### **Q9: What data format is required?**
**A:** The system requires a **strict CSV format** with:
- **Timestamp column**: Must be named 'Timestamp'
- **AQI column**: Must be named 'AQI' with no missing values
- **12 pollutant columns**: PM2.5, PM10, NO2, CO, NO, NOx, NH3, SO2, O3, Benzene, Toluene, Xylene
- **Date format**: YYYY-MM-DD or standard datetime format
- **No missing AQI values**: All AQI values must be present

### **Q10: How much data do I need?**
**A:** Recommended data requirements:
- **Minimum**: 30 days (1 month) for basic forecasting
- **Good**: 180 days (6 months) for reliable forecasts
- **Excellent**: 365+ days (1+ year) for best accuracy
- **Optimal**: 730+ days (2+ years) for seasonal patterns

### **Q11: What if my data doesn't meet requirements?**
**A:** The system will:
- **Reject data** with missing required columns
- **Reject data** with missing AQI values
- **Reject data** with wrong column names
- **Provide error messages** explaining issues
- **Suggest solutions** for data preparation

---

## 🤖 **Model Training**

### **Q12: What models does system use?**
**A:** The system uses two main models:
- **Prophet**: Facebook's time series forecasting model
  - Handles seasonality and trends
  - Good with holiday effects
  - Robust to missing data
- **ARIMA**: Auto-regressive Integrated Moving Average
  - Good for stationary time series
  - Handles autocorrelation
  - Statistical rigor

### **Q13: How long does training take?**
**A:** Training time varies:
- **Small datasets** (< 100 rows): 10-30 seconds
- **Medium datasets** (100-500 rows): 30-60 seconds
- **Large datasets** (500+ rows): 1-3 minutes
- **Very large datasets** (1000+ rows): 3-5 minutes

### **Q14: What if model training fails?**
**A:** The system has multiple fallbacks:
- **Simplified Prophet**: Reduced complexity for small data
- **Emergency Prophet**: Minimal model for very small data
- **Prophet-only**: If ARIMA fails
- **Default metrics**: If evaluation fails

### **Q15: Can I customize model parameters?**
**A:** Yes, through `config.yaml` file:
- **Prophet parameters**: seasonality, changepoints, holidays
- **ARIMA parameters**: orders, seasonal components
- **Training parameters**: cross-validation, evaluation periods
- **Forecast parameters**: horizon, confidence intervals

---

## 📈 **Forecasting**

### **Q16: How far ahead can the system forecast?**
**A:** Forecast horizons:
- **Short-term**: 1-7 days (high accuracy)
- **Medium-term**: 8-30 days (moderate accuracy)
- **Long-term**: 31-90 days (lower accuracy)
- **Very long-term**: 90+ days (low accuracy, trend only)

### **Q17: What do the confidence intervals mean?**
**A:** Confidence intervals show:
- **80% confidence**: 80% chance actual value falls in range
- **Upper bound**: Best-case scenario
- **Lower bound**: Worst-case scenario
- **Width**: Uncertainty level (wider = more uncertainty)

### **Q18: How are ensemble forecasts created?**
**A:** Ensemble methods:
- **Prophet + ARIMA**: Weighted average of both models
- **Prophet-only**: If ARIMA unavailable or unreliable
- **Model weights**: Based on individual model performance
- **Dynamic weighting**: Adjusts based on accuracy

### **Q19: Can I export forecast data?**
**A:** Yes, multiple export formats:
- **CSV**: Complete forecast data with all columns
- **JSON**: Machine-readable format for APIs
- **TXT**: Human-readable summary report
- **Timestamped filenames**: Automatic organization

---

## 📊 **Metrics & Performance**

### **Q20: What do R², RMSE, MAE, MAPE metrics mean?**
**A:** 

**R² (R-squared)**:
- Range: 0 to 1 (higher is better)
- Meaning: Proportion of variance explained
- 0.8 = 80% of variance explained

**RMSE (Root Mean Square Error)**:
- Range: 0 to ∞ (lower is better)
- Meaning: Typical prediction error magnitude
- Units: Same as AQI

**MAE (Mean Absolute Error)**:
- Range: 0 to ∞ (lower is better)
- Meaning: Average prediction error
- Units: Same as AQI

**MAPE (Mean Absolute Percentage Error)**:
- Range: 0% to ∞ (lower is better)
- Meaning: Average percentage error
- Units: Percentage

### **Q21: How do I interpret model quality?**
**A:** Quality assessment based on R²:
- **🌟 Excellent**: R² > 0.8 (85%+ accuracy)
- **👍 Good**: R² 0.6-0.8 (70-85% accuracy)
- **⚠️ Fair**: R² 0.4-0.6 (55-70% accuracy)
- **❌ Poor**: R² < 0.4 (<55% accuracy)

### **Q22: What if my models have low accuracy?**
**A:** Improvement strategies:
- **Collect more data**: Longer historical periods
- **Improve data quality**: Remove outliers, fill gaps
- **Add features**: Weather data, events, holidays
- **Adjust parameters**: Optimize model configuration
- **Ensemble methods**: Combine multiple models

### **Q23: How are model weights determined?**
**A:** Weight determination:
- **Performance-based**: Higher accuracy = higher weight
- **R² comparison**: Better R² gets more weight
- **Ensemble logic**: Automatic optimization
- **Fallback weights**: Default if evaluation fails

---

## 🏥 **Health Analysis**

### **Q24: What health recommendations are provided?**
**A:** Health recommendations by AQI category:
- **Good (0-50)**: Normal outdoor activities
- **Moderate (51-100)**: Sensitive groups limit prolonged exertion
- **Unhealthy for Sensitive (101-150)**: Sensitive groups reduce outdoor activities
- **Unhealthy (151-200)**: Everyone limit outdoor activities
- **Very Unhealthy (201-300)**: Avoid outdoor activities
- **Hazardous (301+)**: Stay indoors, use air purifiers

### **Q25: Who are "sensitive groups"?**
**A:** Sensitive groups include:
- **Children**: Under 18 years old
- **Elderly**: Over 65 years old
- **Pregnant women**: Maternal and fetal health
- **People with respiratory conditions**: Asthma, COPD
- **People with heart disease**: Cardiovascular conditions
- **People with compromised immunity**: Various conditions

### **Q26: What is the health score?**
**A:** Health score calculation:
- **Range**: 0 to 100 (higher is better)
- **Formula**: `100 - (average_AQI / 500) * 100`
- **Meaning**: Overall health impact assessment
- **Usage**: Quick health impact indicator

### **Q27: How are risk periods identified?**
**A:** Risk period analysis:
- **Consecutive days**: Groups of high-AQI days
- **AQI thresholds**: Days with AQI > 100
- **Duration**: Length of risk periods
- **Severity**: Maximum AQI in period
- **Recommendations**: Specific actions for each period

---

## 🔧 **Technical Issues**

### **Q25: What are the system requirements?**
**A:** Minimum requirements:
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum
- **Storage**: 1GB free space
- **Processor**: Modern CPU (any modern processor)
- **Browser**: Chrome, Firefox, Safari, Edge

### **Q26: What Python packages are needed?**
**A:** Required packages (see `requirements.txt`):
- **streamlit**: Web interface
- **pandas**: Data processing
- **numpy**: Numerical operations
- **prophet**: Time series forecasting
- **pmdarima**: ARIMA modeling
- **plotly**: Interactive charts
- **scikit-learn**: Machine learning metrics
- **cmdstanpy**: Prophet backend

### **Q27: Can the system run offline?**
**A:** Yes, with limitations:
- **Full offline**: All features work except updates
- **Data processing**: Complete functionality
- **Model training**: Complete functionality
- **Web interface**: Local access only
- **Dependencies**: Must be pre-installed

### **Q28: How much data can the system handle?**
**A:** Data capacity limits:
- **Rows**: Up to 10,000 rows per dataset
- **File size**: Up to 50MB CSV files
- **Memory usage**: Scales with data size
- **Processing time**: Increases with data size
- **Recommendation**: Split very large datasets

---

## 🛠️ **Troubleshooting**

### **Q29: Common Error Messages**

#### **"Timestamp column not found"**
**Solution**: 
- Ensure 'Timestamp' column exists
- Check exact spelling and capitalization
- Verify column is not in index

#### **"Missing AQI values"**
**Solution**:
- Fill missing AQI values
- Remove rows with missing AQI
- Use data imputation methods

#### **"Model training failed"**
**Solution**:
- Check data quality and quantity
- Verify data format requirements
- Try with more data
- Check system resources

#### **"Cross-validation failed"**
**Solution**:
- Dataset too small for cross-validation
- System uses default metrics
- Collect more data for better evaluation

### **Q30: Performance Issues**

#### **Slow training**
**Solutions**:
- Reduce dataset size
- Simplify model parameters
- Close other applications
- Check system resources

#### **Memory errors**
**Solutions**:
- Use smaller datasets
- Clear Python cache
- Restart application
- Increase system memory

#### **Web interface issues**
**Solutions**:
- Refresh browser
- Clear browser cache
- Check browser compatibility
- Restart Streamlit

### **Q31: Data Issues**

#### **Wrong date format**
**Solutions**:
- Use YYYY-MM-DD format
- Check for mixed date formats
- Ensure consistent datetime format
- Use date conversion tools

#### **Outlier values**
**Solutions**:
- Identify and remove outliers
- Use data cleaning methods
- Verify measurement accuracy
- Consider robust models

#### **Missing pollutant data**
**Solutions**:
- Fill missing values with means/medians
- Use interpolation methods
- Remove problematic columns
- Document data limitations

---

## 📞 **Support & Resources**

### **Q32: Where can I get help?**
**A:** Support resources:
- **Documentation**: `/documentation/` folder
- **User guides**: `USER_GUIDE.md`
- **Technical docs**: `METRICS_IMPLEMENTATION.md`
- **Test scripts**: `test_metrics.py`, `test_ui_fix.py`
- **Configuration**: `config.yaml` with comments

### **Q33: How do I report issues?**
**A:** Issue reporting:
- **Error messages**: Include full error text
- **Data samples**: Provide sample data
- **System info**: Python version, OS, browser
- **Steps to reproduce**: Detailed reproduction steps
- **Expected vs actual**: What you expected vs what happened

### **Q34: How can I contribute?**
**A:** Contribution opportunities:
- **Code improvements**: Better algorithms, optimizations
- **Documentation**: Better guides, examples
- **Testing**: More test cases, edge cases
- **Features**: New functionality, UI improvements
- **Bug fixes**: Identify and fix issues

---

## 🚀 **Best Practices**

### **Q35: Data Preparation Best Practices**
**A:** Recommended practices:
- **Consistent formatting**: Standard date/time formats
- **Quality checks**: Remove outliers, fill gaps
- **Documentation**: Record data sources and changes
- **Backup**: Keep original data safe
- **Validation**: Test with sample data first

### **Q36: Model Training Best Practices**
**A:** Training recommendations:
- **Sufficient data**: At least 6 months of data
- **Regular updates**: Retrain with new data
- **Parameter tuning**: Optimize for your data
- **Validation**: Always check model metrics
- **Ensemble methods**: Use both models when possible

### **Q37: Forecast Usage Best Practices**
**A:** Forecast guidelines:
- **Short-term focus**: Most reliable forecasts
- **Confidence intervals**: Consider uncertainty
- **Regular updates**: Refresh forecasts regularly
- **Context awareness**: Consider external factors
- **Health recommendations**: Follow health guidelines

---

## 📚 **Additional Resources**

### **Documentation Files**
- `USER_GUIDE.md`: Comprehensive user manual
- `METRICS_IMPLEMENTATION.md`: Technical metrics details
- `COMPREHENSIVE_OUTPUTS_GUIDE.md`: All system outputs
- `STRICT_FORMAT_REQUIREMENTS.md`: Data format specifications

### **Test Scripts**
- `test_metrics.py`: Verify ML metrics work correctly
- `test_ui_fix.py`: Test UI timestamp handling
- `compare_emb_data.py`: Compare EMB data formats

### **Configuration**
- `config.yaml`: All system parameters
- Comments explain each parameter
- Customize for your specific needs

---

**Last Updated**: 2026-03-05  
**Version**: 1.0  
**Contact**: Air Quality Commission  

For additional questions, refer to the documentation files or test scripts provided with the system.
