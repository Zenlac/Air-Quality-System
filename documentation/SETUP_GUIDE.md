# Complete Setup Guide for Air Pollution Forecasting System

**Last Updated:** 2026-03-11  
**System Version:** 1.0.0  
**Author:** Air Quality Commission

## 🎯 Overview

This guide provides step-by-step instructions for installing and configuring the Air Pollution Forecasting System on a new device. The system uses advanced machine learning models (Prophet and ARIMA) for air quality prediction.

## 📋 Prerequisites

### System Requirements
- **Operating System:** Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher (3.9+ recommended)
- **RAM:** 8GB minimum (4GB minimum for basic operations)
- **CPU:** 4+ cores recommended
- **Storage:** 2GB disk space minimum
- **Browser:** Chrome, Firefox, Safari, or Edge (for web UI)

### Required Software
1. **Python 3.8+** with pip
2. **Git** (for cloning repository)
3. **Text editor** (VS Code, PyCharm, or similar)

## 🚀 Installation Steps

### Step 1: Install Python

#### Windows
1. Download Python from [python.org](https://python.org)
2. Run installer and check "Add Python to PATH"
3. Verify installation:
```cmd
python --version
pip --version
```

#### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Step 2: Clone Repository

```bash
git clone https://github.com/airquality/air-pollution-forecasting.git
cd air-pollution-forecasting
```

### Step 3: Create Virtual Environment

#### Windows
```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r documentation/requirements.txt
```

### Step 5: Verify Installation

```bash
python test_imports.py
```

## ⚙️ Configuration

### Step 6: Configure System

1. **Review configuration file:**
```bash
cat config.yaml
```

2. **Modify settings if needed:**
- Data paths
- Model parameters
- Output directories
- Performance settings

### Step 7: Prepare Data

The system requires CSV files with **exact format**:

**Required Columns (14 total):**
```
Timestamp,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene,Xylene
```

**Sample data location:** `csv_files/data_files/sample_air_quality_data.csv`

## 🧪 Testing the Installation

### Test 1: Basic Functionality
```bash
python test_sample_data.py
```

### Test 2: ML Metrics
```bash
python test_metrics.py
```

### Test 3: UI Components
```bash
python test_ui_fix.py
```

## 🖥️ Running the System

### Option 1: Web Interface (Recommended)
```bash
python run_ui.py
```
Open: http://localhost:8501

### Option 2: Command Line
```bash
python main.py --data csv_files/data_files/sample_air_quality_data.csv --output outputs
```

## 🔧 Troubleshooting

### Common Issues

1. **Python Version Error**
```bash
# Check Python version
python --version
# If < 3.8, upgrade Python
```

2. **Memory Issues**
- Reduce forecast horizon in config.yaml
- Enable memory_optimization: true
- Use smaller dataset

3. **Import Errors**
```bash
# Reinstall dependencies
pip install -r documentation/requirements.txt --force-reinstall
```

4. **Permission Errors (Windows)**
```cmd
# Run as administrator or use user directory
```

5. **Port Already in Use**
```bash
# Kill existing process or change port
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

### Debug Mode
```bash
python main.py --verbose --config config.yaml
```

## 📁 Directory Structure

After installation, your directory should look like:

```
air-pollution-forecasting/
├── main.py                    # Main entry point
├── run_ui.py                  # Web interface launcher
├── config.yaml                # Configuration file
├── setup.py                   # Package setup
├── documentation/             # Documentation files
│   ├── README.md
│   ├── SETUP_GUIDE.md        # This guide
│   ├── USER_GUIDE.md
│   └── requirements.txt
├── src/                      # Source code
├── csv_files/                # Data directory
├── outputs/                  # Output directory
└── .venv/                    # Virtual environment
```

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
pip install --upgrade -r documentation/requirements.txt
```

### Updating System
```bash
git pull origin main
pip install -r documentation/requirements.txt
```

### System Health Check
```bash
python test_imports.py
python test_metrics.py
```

## 📞 Support

### Getting Help
1. **Documentation:** Check `documentation/` folder
2. **FAQ:** See `documentation/FAQ.md`
3. **Issues:** Report via GitHub Issues
4. **Email:** info@airquality.gov

### Common Commands Reference
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Run web interface
python run_ui.py

# Run command line
python main.py --data data.csv --output outputs

# Test system
python test_imports.py

# Convert EMB data
python convert_emb_data.py --input emb.csv --output converted.csv
```

## ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Configuration reviewed
- [ ] Test data validated
- [ ] Basic tests passed
- [ ] Web interface accessible
- [ ] Sample forecast generated

## 🎉 Next Steps

1. **Review USER_GUIDE.md** for detailed usage instructions
2. **Prepare your data** in the required CSV format
3. **Run your first forecast** using sample data
4. **Explore visualizations** and health analysis features
5. **Customize configuration** for your specific needs

---

**Installation Complete!** 🎉

You're ready to start using the Air Pollution Forecasting System. For detailed usage instructions, see the [USER_GUIDE.md](USER_GUIDE.md).

**Air Quality Commission**  
*Protecting public health through accurate air quality forecasting*
