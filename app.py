#!/usr/bin/env python3
"""
Air Pollution Forecasting System - Web UI
A user-friendly Streamlit interface for air quality prediction

Author: Air Quality Commission
Created: 2026-02-27
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yaml
import io
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import base64

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config import Config
    from src.data_processor import DataProcessor
    from src.model_trainer import ModelTrainer
    from src.prophet_trainer import ProphetTrainer
    from src.arima_trainer import ARIMATrainer
    from src.forecaster import Forecaster
    from src.visualizer import Visualizer
    from src.utils import PerformanceMonitor
except ImportError:
    from config import Config
    from data_processor import DataProcessor
    from model_trainer import ModelTrainer
    try:
        from prophet_trainer import ProphetTrainer
        from arima_trainer import ARIMATrainer
        from forecaster import Forecaster
    except ImportError:
        # Fallback: create trainer classes if modules don't exist
        class ProphetTrainer:
            def __init__(self, config):
                self.config = config
            def train(self, data):
                from prophet import Prophet
                # Ensure data has correct column names for Prophet
                if 'ds' not in data.columns or 'y' not in data.columns:
                    # Try to rename columns if they don't exist
                    if 'Timestamp' in data.columns and 'AQI' in data.columns:
                        data = data.rename(columns={'Timestamp': 'ds', 'AQI': 'y'})
                    else:
                        raise ValueError("Data must have 'ds' and 'y' columns, or 'Timestamp' and 'AQI' columns")
                # Remove any NaN values
                data = data.dropna(subset=['ds', 'y'])
                if len(data) < 2:
                    raise ValueError(f"Insufficient data for Prophet: Only {len(data)} valid rows")
                model = Prophet(
                    changepoint_prior_scale=0.1,
                    seasonality_mode='multiplicative',
                    weekly_seasonality=True,
                    yearly_seasonality=True,
                    daily_seasonality=False
                )
                model.fit(data)
                return model
        
        class ARIMATrainer:
            def __init__(self, config):
                self.config = config
            def train(self, data):
                from statsmodels.tsa.arima.model import ARIMA
                model = ARIMA(data['AQI'], order=(1,1,1))
                return model.fit()
        
        class Forecaster:
            """Fallback forecaster for when main forecaster is not available"""
            def __init__(self, config):
                self.config = config
                self.prophet_weight = 0.6
                self.arima_weight = 0.4
            
            def generate_ensemble_forecast(self, prophet_model, arima_model, df, horizon=31):
                """Generate simple ensemble forecast"""
                try:
                    # Generate Prophet forecast
                    future = prophet_model.make_future_dataframe(periods=horizon, include_history=False)
                    prophet_forecast = prophet_model.predict(future)
                    
                    # Generate ARIMA forecast (simplified)
                    try:
                        arima_forecast = arima_model.forecast(steps=horizon)
                        if isinstance(arima_forecast, np.ndarray):
                            arima_forecast = arima_forecast
                        else:
                            arima_forecast = arima_forecast.values
                    except:
                        # If ARIMA fails, use Prophet values
                        arima_forecast = prophet_forecast['yhat'].values
                    
                    # Create ensemble
                    ensemble_values = (self.prophet_weight * prophet_forecast['yhat'].values + 
                                     self.arima_weight * arima_forecast)
                    
                    # Create forecast DataFrame
                    dates = prophet_forecast['ds']
                    forecasts = pd.DataFrame({
                        'Forecasted_AQI': ensemble_values,
                        'Lower_Bound': prophet_forecast['yhat_lower'].values,
                        'Upper_Bound': prophet_forecast['yhat_upper'].values,
                        'Prophet_Forecast': prophet_forecast['yhat'].values,
                        'ARIMA_Forecast': arima_forecast
                    }, index=dates)
                    
                    # Add AQI categories
                    def get_simple_aqi_category(aqi):
                        if aqi <= 50:
                            return "Good"
                        elif aqi <= 100:
                            return "Moderate"
                        elif aqi <= 150:
                            return "Unhealthy for Sensitive Groups"
                        elif aqi <= 200:
                            return "Unhealthy"
                        elif aqi <= 300:
                            return "Very Unhealthy"
                        else:
                            return "Hazardous"
                    
                    forecasts['AQI_Category'] = forecasts['Forecasted_AQI'].apply(get_simple_aqi_category)
                    forecasts['Health_Recommendation'] = forecasts['AQI_Category'].apply(lambda x: 
                        "Enjoy outdoor activities!" if x == "Good" else
                        "Sensitive groups should take precautions" if x == "Moderate" else
                        "Reduce prolonged outdoor exertion" if x == "Unhealthy for Sensitive Groups" else
                        "Everyone should reduce outdoor activities" if x == "Unhealthy" else
                        "Avoid prolonged outdoor exertion" if x == "Very Unhealthy" else
                        "Avoid all outdoor activities"
                    )
                    
                    return forecasts
                    
                except Exception as e:
                    # If everything fails, raise the error to be handled by UI
                    raise Exception(f"Fallback forecaster failed: {str(e)}")
    
    from visualizer import Visualizer
    from utils import PerformanceMonitor

# Page configuration
st.set_page_config(
    page_title="Air Pollution Forecasting System",
    page_icon="Globe",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .health-good { border-left-color: #00ff00; }
    .health-moderate { border-left-color: #ffff00; }
    .health-unhealthy-sensitive { border-left-color: #ff9900; }
    .health-unhealthy { border-left-color: #ff0000; }
    .health-very-unhealthy { border-left-color: #99004c; }
    .health-hazardous { border-left-color: #7e0023; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'models_trained' not in st.session_state:
    st.session_state.models_trained = False
if 'forecasts_generated' not in st.session_state:
    st.session_state.forecasts_generated = False
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'forecasts' not in st.session_state:
    st.session_state.forecasts = None
if 'prophet_model' not in st.session_state:
    st.session_state.prophet_model = None
if 'arima_model' not in st.session_state:
    st.session_state.arima_model = None
# Add additional tracking variables
if 'training_in_progress' not in st.session_state:
    st.session_state.training_in_progress = False
if 'model_training_time' not in st.session_state:
    st.session_state.model_training_time = None
if 'last_data_hash' not in st.session_state:
    st.session_state.last_data_hash = None

def calculate_data_hash(df):
    """Calculate a hash of the data to detect changes"""
    try:
        import hashlib
        # Create a string representation of key data properties
        data_str = f"{len(df)}_{df.columns.tolist()}_{df.index.min()}_{df.index.max()}"
        if 'AQI' in df.columns:
            data_str += f"_{df['AQI'].mean():.2f}_{df['AQI'].std():.2f}"
        return hashlib.md5(data_str.encode()).hexdigest()
    except:
        return None

def calculate_trend_stability(data):
    """Calculate trend stability for model quality assessment"""
    try:
        if len(data) < 10:
            return 0.5  # Default for small datasets
        
        # Calculate rolling means
        window = min(len(data) // 4, 30)
        rolling_std = data['AQI'].rolling(window=window).std().dropna()
        
        # Stability based on rolling standard deviation consistency
        stability_score = 1 - (rolling_std.std() / rolling_std.mean()) if rolling_std.mean() > 0 else 0.5
        
        return max(0, min(1, stability_score))
    except:
        return 0.5

def calculate_improved_mape(actual, predicted):
    """Improved MAPE calculation with robust handling"""
    import numpy as np
    
    try:
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # Handle zero and near-zero actual values
        mask = np.abs(actual) > 0.1  # Avoid division by very small numbers
        if not np.any(mask):
            return 100.0  # Return high MAPE if all actuals are near zero
        
        # Calculate percentage errors only for valid actual values
        percentage_errors = np.abs((actual[mask] - predicted[mask]) / actual[mask]) * 100
        
        # Remove outliers (errors > 200%)
        percentage_errors = percentage_errors[percentage_errors < 200]
        
        if len(percentage_errors) == 0:
            return 100.0
        
        # Calculate MAPE
        mape = np.mean(percentage_errors)
        
        # Apply reasonable bounds
        return min(max(mape, 0), 200)
    except:
        return 50.0  # Reasonable default

def are_models_valid():
    """Check if models are still valid for current data"""
    if not st.session_state.models_trained:
        return False
    
    if st.session_state.prophet_model is None and st.session_state.arima_model is None:
        return False
    
    # Check if data has changed
    current_data = st.session_state.processed_data
    if current_data is not None:
        current_hash = calculate_data_hash(current_data)
        if current_hash != st.session_state.last_data_hash:
            return False
    
    return True

def auto_reformat_data(df):
    """
    Automatically reformat raw data into the expected format for the forecasting system.
    Handles various input formats and standardizes them.
    """
    try:
        # Create a copy to avoid modifying the original
        reformatted_df = df.copy()
        
        # Step 1: Standardize column names
        reformatted_df = standardize_column_names(reformatted_df)
        
        # Step 2: Ensure required columns exist
        reformatted_df = ensure_required_columns(reformatted_df)
        
        # Step 3: Standardize date format
        reformatted_df = standardize_date_column(reformatted_df)
        
        # Step 4: Clean and validate data
        reformatted_df = clean_and_validate_data(reformatted_df)
        
        # Step 5: Calculate AQI from pollutants if AQI is missing or invalid
        reformatted_df = calculate_aqi_in_reformatting(reformatted_df)
        
        # Step 6: Calculate AQI buckets/categories
        reformatted_df = calculate_aqi_buckets(reformatted_df)
        
        # Step 7: Reorder columns to expected format
        reformatted_df = reorder_columns_with_aqi(reformatted_df)
        
        return reformatted_df
        
    except Exception as e:
        raise Exception(f"Data reformatting failed: {str(e)}")

def standardize_column_names(df):
    """Standardize column names to match expected format"""
    # Column name mapping for common variations
    column_mapping = {
        # Date columns
        'date': 'Timestamp',
        'datetime': 'Timestamp',
        'time': 'Timestamp',
        'Date': 'Timestamp',
        'DateTime': 'Timestamp',
        'TIME': 'Timestamp',
        'timestamp': 'Timestamp',
        
        # AQI columns
        'aqi': 'AQI',
        'air_quality_index': 'AQI',
        'Air_Quality_Index': 'AQI',
        'AIR_QUALITY_INDEX': 'AQI',
        'Air Quality': 'AQI',
        
        # Pollutant columns
        'pm2.5': 'PM2.5',
        'pm25': 'PM2.5',
        'PM2_5': 'PM2.5',
        'pm10': 'PM10',
        'PM_10': 'PM10',
        'no2': 'NO2',
        'NO_2': 'NO2',
        'nox': 'NOx',
        'NO_X': 'NOx',
        'nh3': 'NH3',
        'NH_3': 'NH3',
        'so2': 'SO2',
        'SO_2': 'SO2',
        'o3': 'O3',
        'O_3': 'O3',
        'co': 'CO',
        'C_O': 'CO',
        'benzene': 'Benzene',
        'toluene': 'Toluene',
        'xylene': 'Xylene'
    }
    
    # Apply column mapping
    df = df.rename(columns=column_mapping)
    
    return df

def ensure_required_columns(df):
    """Ensure all required columns exist, create missing ones with default values"""
    required_columns = {
        'Timestamp': None,  # Will be filled later
        'AQI': 0,  # Default to 0 if missing
        'PM2.5': 0,
        'PM10': 0,
        'NO': 0,
        'NO2': 0,
        'NOx': 0,
        'NH3': 0,
        'CO': 0,
        'SO2': 0,
        'O3': 0,
        'Benzene': 0,
        'Toluene': 0,
        'Xylene': 0
    }
    
    # Add missing columns with default values
    for col, default_val in required_columns.items():
        if col not in df.columns:
            if col == 'Timestamp':
                # Create a default timestamp column if missing
                df[col] = pd.date_range(start='2023-01-01', periods=len(df), freq='H')
            else:
                df[col] = default_val
    
    return df

def standardize_date_column(df):
    """Standardize the date column to datetime format"""
    if 'Timestamp' in df.columns:
        try:
            # Try to convert to datetime
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            
            # Handle any conversion failures
            if df['Timestamp'].isnull().any():
                # Fill missing dates with sequential dates
                null_count = df['Timestamp'].isnull().sum()
                if null_count > 0:
                    st.warning(f"Found {null_count} invalid date values. Filling with sequential dates.")
                    # Create a sequential date range
                    start_date = pd.Timestamp.now().normalize()
                    df.loc[df['Timestamp'].isnull(), 'Timestamp'] = pd.date_range(
                        start=start_date, periods=null_count, freq='H'
                    )
            
            # Sort by timestamp
            df = df.sort_values('Timestamp').reset_index(drop=True)
            
        except Exception as e:
            st.warning(f"Date standardization failed: {str(e)}. Creating default timestamps.")
            df['Timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='H')
    
    return df

def clean_and_validate_data(df):
    """Clean and validate the data while preserving actual measurements"""
    # Clean numeric columns but preserve actual values
    numeric_columns = ['AQI', 'PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']
    
    for col in numeric_columns:
        if col in df.columns:
            # Convert to numeric, preserving actual values
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # For AQI, only fill extreme missing values
            if col == 'AQI':
                # Don't fill AQI values - let the calculation handle it
                pass  # Keep NaN values as they will be calculated
            else:
                # For pollutants, only fill truly missing values with small values
                # This preserves the actual measurements in the CSV
                missing_mask = df[col].isna()
                if missing_mask.any():
                    # Use a very small value instead of 0 to indicate detection limit
                    df.loc[missing_mask, col] = 0.001  # Detection limit placeholder
            
            # Remove negative values (except for NO and NOx which can be negative)
            if col not in ['NO', 'NOx']:
                df[col] = df[col].clip(lower=0)
    
    # Don't validate AQI range here - let AQI calculation handle it
    # This preserves the actual pollutant measurements
    
    return df

def calculate_aqi_in_reformatting(df):
    """Calculate AQI from actual pollutant concentrations in the CSV data"""
    try:
        # Check if AQI calculation is needed
        should_calculate = (
            'AQI' not in df.columns or 
            df['AQI'].isna().all() or 
            (df['AQI'] == 0).all() or
            df['AQI'].std() == 0  # All values are the same
        )
        
        if should_calculate:
            st.info("🔍 Calculating AQI from actual pollutant concentrations in your data...")
            
            # Import AQI calculator
            from src.aqi_calculator import create_aqi_calculator
            aqi_calc = create_aqi_calculator('US_EPA')
            
            # Calculate AQI for each row using actual pollutant values
            aqi_values = []
            calculation_count = 0
            
            for idx, row in df.iterrows():
                concentrations = {}
                pollutant_cols = ['PM2.5', 'PM10', 'NO2', 'CO', 'SO2', 'O3', 'NH3', 'NO', 'NOx', 'Benzene', 'Toluene', 'Xylene']
                
                # Use actual values from CSV
                for col in pollutant_cols:
                    if col in df.columns:
                        value = row[col]
                        # Only include if we have a valid, non-zero measurement
                        if not pd.isna(value) and value > 0:
                            concentrations[col] = float(value)
                
                if concentrations:
                    aqi = aqi_calc.calculate_aqi(concentrations)
                    aqi_values.append(aqi)
                    calculation_count += 1
                else:
                    # If no pollutant data available, use a conservative estimate
                    aqi_values.append(50.0)  # Moderate air quality as default
            
            # Update AQI column
            df['AQI'] = aqi_values
            
            # Log calculation summary
            st.success(f"✅ Calculated AQI for {calculation_count} out of {len(df)} records using actual pollutant data")
            
            # Show calculation summary
            if calculation_count > 0:
                valid_aqi = [aqi for aqi in aqi_values if aqi != 50.0]
                if valid_aqi:
                    st.info(f"📊 AQI Range from calculation: {min(valid_aqi):.1f} - {max(valid_aqi):.1f}")
        
        return df
        
    except Exception as e:
        st.error(f"❌ AQI calculation failed: {str(e)}")
        # Ensure AQI column exists with conservative default
        if 'AQI' not in df.columns:
            df['AQI'] = 50.0
        return df

def calculate_aqi_buckets(df):
    """Calculate AQI buckets/categories with detailed analysis using real data"""
    try:
        # Calculate AQI categories and related information
        categories = []
        colors = []
        health_messages = []
        dominant_pollutants = []
        sub_indices = []  # Track individual pollutant contributions
        
        # Import AQI calculator
        from src.aqi_calculator import create_aqi_calculator
        aqi_calc = create_aqi_calculator('US_EPA')
        
        st.info("🏷️ Calculating AQI categories and health impacts...")
        
        for idx, row in df.iterrows():
            aqi_value = row['AQI']
            
            # Get AQI bucket information
            category, color, health_message = get_aqi_category(aqi_value)
            categories.append(category)
            colors.append(color)
            health_messages.append(health_message)
            
            # Find dominant pollutant using actual concentrations
            concentrations = {}
            pollutant_cols = ['PM2.5', 'PM10', 'NO2', 'CO', 'SO2', 'O3', 'NH3', 'NO', 'NOx', 'Benzene', 'Toluene', 'Xylene']
            
            for col in pollutant_cols:
                if col in df.columns:
                    value = row[col]
                    # Use actual values from CSV, ignore detection limit placeholders
                    if not pd.isna(value) and value > 0.01:  # Above detection limit
                        concentrations[col] = float(value)
            
            if concentrations:
                dominant_pollutant, sub_index = aqi_calc.get_dominant_pollutant(concentrations)
                dominant_pollutants.append(dominant_pollutant)
                sub_indices.append(sub_index)
            else:
                dominant_pollutants.append('Unknown')
                sub_indices.append(0.0)
        
        # Add new columns to DataFrame
        df['AQI_Category'] = categories
        df['AQI_Color'] = colors
        df['Health_Message'] = health_messages
        df['Dominant_Pollutant'] = dominant_pollutants
        df['Dominant_Pollutant_SubIndex'] = sub_indices
        
        # Provide summary statistics
        if concentrations:  # If we had real pollutant data
            category_dist = pd.Series(categories).value_counts()
            pollutant_dist = pd.Series(dominant_pollutants).value_counts()
            
            st.success(f"✅ AQI categorization completed using real pollutant measurements")
            st.info(f"📊 Most common category: {category_dist.index[0]} ({category_dist.iloc[0]} records)")
            st.info(f"🔬 Most dominant pollutant: {pollutant_dist.index[0]} ({pollutant_dist.iloc[0]} records)")
        
        return df
        
    except Exception as e:
        st.error(f"❌ AQI bucket calculation failed: {str(e)}")
        # Add default columns if calculation fails
        df['AQI_Category'] = 'Moderate'
        df['AQI_Color'] = '#ffff00'
        df['Health_Message'] = 'Air quality is acceptable'
        df['Dominant_Pollutant'] = 'Unknown'
        df['Dominant_Pollutant_SubIndex'] = 0.0
        return df

def reorder_columns_with_aqi(df):
    """Reorder columns to match expected format including AQI bucket columns"""
    # Core columns first
    core_order = [
        'Timestamp', 'AQI', 'PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 
        'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'
    ]
    
    # AQI analysis columns next
    aqi_analysis_order = [
        'AQI_Category', 'AQI_Color', 'Health_Message', 'Dominant_Pollutant', 'Dominant_Pollutant_SubIndex'
    ]
    
    # Get existing columns in expected order
    ordered_columns = [col for col in core_order if col in df.columns]
    ordered_columns += [col for col in aqi_analysis_order if col in df.columns]
    
    # Add any remaining columns that weren't in the expected order
    remaining_columns = [col for col in df.columns if col not in ordered_columns]
    final_order = ordered_columns + remaining_columns
    
    return df[final_order]

def get_aqi_category(aqi_value):
    """Get AQI category and color based on AQI value"""
    if aqi_value <= 50:
        return "Good", "#00ff00", "Enjoy outdoor activities!"
    elif aqi_value <= 100:
        return "Moderate", "#ffff00", "Sensitive groups should take precautions"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive Groups", "#ff9900", "Reduce prolonged outdoor exertion"
    elif aqi_value <= 200:
        return "Unhealthy", "#ff0000", "Everyone should reduce outdoor activities"
    elif aqi_value <= 300:
        return "Very Unhealthy", "#99004c", "Avoid prolonged outdoor exertion"
    else:
        return "Hazardous", "#7e0023", "Avoid all outdoor activities"

def create_forecast_plot(forecasts, title="Air Quality Forecast"):
    """Create interactive forecast plot"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Forecast with Confidence Intervals', 'Forecast Components'),
        vertical_spacing=0.1
    )
    
    # Main forecast
    fig.add_trace(
        go.Scatter(
            x=forecasts.index,
            y=forecasts['Forecasted_AQI'],
            mode='lines+markers',
            name='Ensemble Forecast',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    # Confidence intervals
    fig.add_trace(
        go.Scatter(
            x=forecasts.index,
            y=forecasts['Lower_Bound'],
            mode='lines',
            name='Lower Bound',
            line=dict(color='lightblue', width=1),
            fill=None
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=forecasts.index,
            y=forecasts['Upper_Bound'],
            mode='lines',
            name='Upper Bound',
            line=dict(color='lightblue', width=1),
            fill='tonexty',
            fillcolor='rgba(173, 216, 230, 0.3)'
        ),
        row=1, col=1
    )
    
    # Individual model forecasts
    if 'Prophet_Forecast' in forecasts.columns:
        fig.add_trace(
            go.Scatter(
                x=forecasts.index,
                y=forecasts['Prophet_Forecast'],
                mode='lines',
                name='Prophet Forecast',
                line=dict(color='green', width=1, dash='dash')
            ),
            row=2, col=1
        )
    
    if 'ARIMA_Forecast' in forecasts.columns:
        fig.add_trace(
            go.Scatter(
                x=forecasts.index,
                y=forecasts['ARIMA_Forecast'],
                mode='lines',
                name='ARIMA Forecast',
                line=dict(color='red', width=1, dash='dash')
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        title=title,
        height=600,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_aqi_gauge(current_aqi):
    """Create AQI gauge chart"""
    category, color, _ = get_aqi_category(current_aqi)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_aqi,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Current AQI<br><span style='color: {color}'>{category}</span>"},
        gauge = {
            'axis': {'range': [None, 500]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "lightgreen"},
                {'range': [50, 100], 'color': "lightyellow"},
                {'range': [100, 150], 'color': "lightcoral"},
                {'range': [150, 200], 'color': "lightsalmon"},
                {'range': [200, 300], 'color': "lightpink"},
                {'range': [300, 500], 'color': "lavender"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': current_aqi
            }
        }
    ))
    
    fig.update_layout(height=400)
    return fig

def main():
    """Main application"""
    # Header
    st.markdown('<h1 class="main-header">Air Pollution Forecasting System</h1>', unsafe_allow_html=True)
    
    # Data Requirements Warning for Raw Data Users
    with st.expander("📋 Important: Data Requirements & Recommendations", expanded=True):
        st.markdown("""
        ### 🚨 For Raw Data Users - Please Read Before Uploading
        
        **Required Data Format:**
        - **Timestamp Column**: Must contain date/time information (column names: `Timestamp`, `Date`, `datetime`, `date`, `time`)
        - **AQI Column**: Air Quality Index values (column names: `AQI`, `aqi`, `Air_Quality_Index`, `Air Quality Index`)
        - **Pollutant Data** (Optional but 
        Recommended): PM2.5, PM10, NO2, CO, SO2, O3, NH3, NO, NOx, Benzene, Toluene, Xylene
        
        **Data Quality Recommendations:**
        - ✅ **Minimum 30 days** of historical data for reliable forecasting
        - ✅ **Hourly or daily** measurements (avoid gaps longer than 24 hours)
        - ✅ **Consistent time intervals** between measurements
        - ✅ **Valid AQI values** ranging from 0-500
        
        **Common Issues to Avoid:**
        - ❌ Missing timestamps or invalid date formats
        - ❌ AQI values outside 0-500 range
        - ❌ Large gaps in time series data
        - ❌ Non-numeric pollutant concentrations
        
        **Pro Tip**: If you only have pollutant concentrations (PM2.5, PM10, etc.) but no AQI values, 
        the system will automatically calculate AQI using US EPA standards!
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("📖 **Need sample data?** Check the `csv_files/data_files/` directory for example formats")
        with col2:
            st.warning("⚠️ **Poor data quality will affect forecast accuracy**")
    
    st.markdown("---")  # Separator line
    
    # Sidebar
    st.sidebar.title("Configuration")
    
    # File upload section
    st.sidebar.subheader("Data Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload your air quality data (CSV)",
        type=['csv'],
        help="Upload a CSV file with Timestamp and AQI columns"
    )
    
    # Model parameters
    st.sidebar.subheader("Model Parameters")
    
    forecast_days = st.sidebar.slider(
        "Forecast Horizon (days)",
        min_value=1,
        max_value=90,
        value=14
    )
    
    prophet_weight = st.sidebar.slider(
        "Prophet Model Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )
    
    arima_weight = 1.0 - prophet_weight
    
    confidence_level = st.sidebar.selectbox(
        "Confidence Level",
        [0.80, 0.85, 0.90, 0.95, 0.99],
        index=3
    )
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["Data Upload", "Model Training", "Forecasts", "Health Analysis"])
    
    with tab1:
        st.header("Data Upload & Processing")
        
        if uploaded_file is not None:
            # Load and display data
            try:
                # Read CSV file with comprehensive error handling
                df = None
                parse_method = "standard"
                
                try:
                    # First attempt: standard parsing
                    df = pd.read_csv(uploaded_file)
                    st.info(f"Loaded with standard parsing. Columns: {len(df.columns)}")
                except Exception as e:
                    st.warning(f"Standard parsing failed: {str(e)}")
                    parse_method = "robust"
                    
                    try:
                        # Second attempt: skip bad lines
                        df = pd.read_csv(uploaded_file, on_bad_lines='skip')
                        st.info(f"Loaded with skip-bad-lines. Columns: {len(df.columns)}")
                    except Exception as e2:
                        st.warning(f"Skip-bad-lines failed: {str(e2)}")
                        parse_method = "manual"
                        
                        try:
                            # Third attempt: manual parsing with different parameters
                            df = pd.read_csv(uploaded_file, 
                                           encoding='utf-8',
                                           quotechar='"',
                                           escapechar='\\',
                                           skipinitialspace=True)
                            st.info(f"Loaded with manual parsing. Columns: {len(df.columns)}")
                        except Exception as e3:
                            st.error(f"All parsing methods failed. Last error: {str(e3)}")
                            st.error("Please check your CSV file format and try again.")
                            return
                
                if df is None or df.empty:
                    st.error("Failed to load any data from the CSV file.")
                    return
                
                st.success(f"Data loaded successfully! Shape: {df.shape} (Method: {parse_method})")
                
                # Debug: Show raw column names
                st.subheader("Debug Information")
                st.write("Raw column names:", df.columns.tolist())
                st.write("First few rows:")
                st.dataframe(df.head(2))
                
                # Check for common CSV issues
                if len(df.columns) == 1:
                    st.warning("Only 1 column detected - likely a CSV formatting issue.")
                    # Try to split the single column
                    first_col = df.columns[0]
                    if ',' in first_col:
                        st.info("Attempting to fix malformed header...")
                        # Read as raw text and fix
                        content = uploaded_file.read().decode('utf-8')
                        lines = content.strip().split('\n')
                        
                        if len(lines) > 1:
                            # Parse first line as header
                            header = lines[0].strip()
                            # Fix common issues
                            header = header.replace('AQI,', 'AQI,')  # Ensure proper separation
                            header = header.replace('TimestampAQI', 'Timestamp,AQI')  # Fix merged columns
                            
                            # Re-parse with fixed header
                            fixed_content = header + '\n' + '\n'.join(lines[1:])
                            from io import StringIO
                            df = pd.read_csv(StringIO(fixed_content))
                            st.success("CSV header fixed successfully!")
                            st.write("Fixed columns:", df.columns.tolist())
                
                # Display data preview
                st.subheader("Data Preview")
                st.dataframe(df.head())
                
                # Display available columns
                st.subheader("Available Columns")
                st.write("Columns found:", df.columns.tolist())
                
                # Full Dataset Viewer Section
                st.markdown("---")
                st.subheader("📊 Full Dataset Viewer")
                
                # Data viewing options - better layout for readability
                st.write("**Viewing Controls:**")
                
                # Row 1: Row display and pagination
                col1, col2 = st.columns(2)
                
                with col1:
                    # Number of rows to display
                    rows_to_show = st.selectbox(
                        "📊 Rows to display",
                        options=[10, 25, 50, 100, 500, 1000, "All"],
                        index=1,
                        help="Choose how many rows to display at once"
                    )
                
                with col2:
                    # Start row for pagination
                    if rows_to_show != "All":
                        max_start = max(0, len(df) - int(rows_to_show))
                        start_row = st.number_input(
                            "📍 Start from row",
                            min_value=0,
                            max_value=max_start,
                            value=0,
                            step=int(rows_to_show) if rows_to_show != "All" else 1,
                            help="Starting row number (0-based)"
                        )
                    else:
                        start_row = 0
                
                # Row 2: Column filtering and search
                col3, col4 = st.columns(2)
                
                with col3:
                    # Column filtering
                    available_columns = ["All Columns"] + list(df.columns)
                    selected_column = st.selectbox(
                        "🔍 Filter by column (optional)",
                        options=available_columns,
                        index=0,
                        help="Show data for specific column only"
                    )
                
                with col4:
                    # Search functionality
                    search_term = st.text_input(
                        "🔎 Search data",
                        placeholder="Enter search term...",
                        help="Search across all columns"
                    )
                
                # Apply filters and display data
                display_df = df.copy()
                
                # Apply column filter
                if selected_column != "All Columns":
                    display_df = display_df[[selected_column]]
                
                # Apply search filter
                if search_term:
                    mask = display_df.astype(str).apply(
                        lambda x: x.str.contains(search_term, case=False, na=False)
                    ).any(axis=1)
                    display_df = display_df[mask]
                    if len(display_df) == 0:
                        st.warning(f"No results found for '{search_term}'")
                        display_df = df.head(0)  # Show empty dataframe
                
                # Show dataset info with filters
                st.info(f"📈 Showing {len(display_df)} of {len(df)} total records")
                
                # Display the data with pagination
                if rows_to_show != "All":
                    end_row = min(start_row + int(rows_to_show), len(display_df))
                    paginated_df = display_df.iloc[start_row:end_row]
                else:
                    paginated_df = display_df
                
                # Display data with better formatting
                if len(paginated_df) > 0:
                    # Main data display
                    st.dataframe(paginated_df, use_container_width=True)
                    
                    # Download options in a separate section for better layout
                    st.markdown("---")
                    st.write("**📥 Download Options:**")
                    
                    # Create download buttons in a cleaner layout
                    dl_col1, dl_col2 = st.columns(2)
                    
                    with dl_col1:
                        # Download filtered data
                        csv_data = paginated_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Filtered Data",
                            data=csv_data,
                            file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            help="Download currently displayed data",
                            use_container_width=True
                        )
                    
                    with dl_col2:
                        # Download full dataset
                        full_csv_data = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Full Dataset",
                            data=full_csv_data,
                            file_name=f"full_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            help="Download complete uploaded dataset",
                            use_container_width=True
                        )
                else:
                    st.warning("No data to display with current filters")
                
                # Data statistics section
                if len(display_df) > 0:
                    st.markdown("---")
                    st.subheader("📋 Data Statistics")
                    
                    # Create statistics columns with better spacing
                    if selected_column == "All Columns":
                        # Show statistics for all numeric columns
                        numeric_cols = display_df.select_dtypes(include=[np.number]).columns.tolist()
                        if numeric_cols:
                            st.write("**📊 Numeric Columns Overview:**")
                            
                            # Use tabs for better organization
                            stats_tab1, stats_tab2, stats_tab3 = st.tabs(["Basic Stats", "Range Info", "Missing Values"])
                            
                            with stats_tab1:
                                st.write("**Basic Statistics:**")
                                for i, col in enumerate(numeric_cols[:6]):  # Show first 6 numeric columns
                                    col_name = str(col)
                                    if len(col_name) > 20:
                                        col_name = col_name[:17] + "..."
                                    st.write(f"**{i+1}. {col_name}:**")
                                    st.write(f"   • Mean: {display_df[col].mean():.2f}")
                                    st.write(f"   • Std Dev: {display_df[col].std():.2f}")
                                    st.write(f"   • Median: {display_df[col].median():.2f}")
                                    st.write(f"   • Variance: {display_df[col].var():.2f}")
                                    st.write("")  # Add spacing
                            
                            with stats_tab2:
                                st.write("**Range Information:**")
                                for i, col in enumerate(numeric_cols[:6]):
                                    col_name = str(col)
                                    if len(col_name) > 20:
                                        col_name = col_name[:17] + "..."
                                    st.write(f"**{i+1}. {col_name}:**")
                                    st.write(f"   • Min: {display_df[col].min():.2f}")
                                    st.write(f"   • Max: {display_df[col].max():.2f}")
                                    st.write(f"   • Range: {display_df[col].max() - display_df[col].min():.2f}")
                                    st.write(f"   • 25th Percentile: {display_df[col].quantile(0.25):.2f}")
                                    st.write(f"   • 75th Percentile: {display_df[col].quantile(0.75):.2f}")
                                    st.write("")  # Add spacing
                            
                            with stats_tab3:
                                st.write("**Missing Values & Data Types:**")
                                for i, col in enumerate(display_df.columns[:8]):  # Show first 8 columns
                                    col_name = str(col)
                                    if len(col_name) > 20:
                                        col_name = col_name[:17] + "..."
                                    missing_count = display_df[col].isna().sum()
                                    missing_pct = (missing_count / len(display_df)) * 100
                                    st.write(f"**{i+1}. {col_name}:**")
                                    st.write(f"   • Missing Count: {missing_count}")
                                    st.write(f"   • Missing Percentage: {missing_pct:.1f}%")
                                    st.write(f"   • Data Type: {display_df[col].dtype}")
                                    st.write("")  # Add spacing
                    else:
                        # Show detailed statistics for selected column
                        st.write(f"**📊 Detailed Analysis for: {selected_column}**")
                        
                        if pd.api.types.is_numeric_dtype(display_df[selected_column]):
                            # Use columns for numeric stats
                            stat_col1, stat_col2 = st.columns(2)
                            
                            with stat_col1:
                                st.metric("Count", display_df[selected_column].count())
                                st.metric("Mean", f"{display_df[selected_column].mean():.2f}")
                                st.metric("Median", f"{display_df[selected_column].median():.2f}")
                                st.metric("Std Dev", f"{display_df[selected_column].std():.2f}")
                                st.metric("Variance", f"{display_df[selected_column].var():.2f}")
                            
                            with stat_col2:
                                st.metric("Min", f"{display_df[selected_column].min():.2f}")
                                st.metric("Max", f"{display_df[selected_column].max():.2f}")
                                st.metric("Range", f"{display_df[selected_column].max() - display_df[selected_column].min():.2f}")
                                st.metric("25th Percentile", f"{display_df[selected_column].quantile(0.25):.2f}")
                                st.metric("75th Percentile", f"{display_df[selected_column].quantile(0.75):.2f}")
                        else:
                            # Non-numeric column statistics
                            col_stat1, col_stat2 = st.columns(2)
                            
                            with col_stat1:
                                st.metric("Count", display_df[selected_column].count())
                                st.metric("Unique Values", display_df[selected_column].nunique())
                                st.metric("Missing Values", display_df[selected_column].isna().sum())
                            
                            with col_stat2:
                                # Show value counts for categorical data with limited unique values
                                if display_df[selected_column].nunique() <= 20:
                                    st.write("**📋 Value Distribution:**")
                                    value_counts = display_df[selected_column].value_counts().head(10)
                                    for val, count in value_counts.items():
                                        val_str = str(val)
                                        if len(val_str) > 30:
                                            val_str = val_str[:27] + "..."
                                        st.write(f"• {val_str}: {count}")
                                else:
                                    st.info(f"Too many unique values ({display_df[selected_column].nunique()}) to display distribution")
                
                # Data info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Records", len(df))
                    st.metric("Columns", len(df.columns))
                
                with col2:
                    # Try to find date column
                    date_column = None
                    possible_date_columns = ['Timestamp', 'Date', 'datetime', 'date', 'time']
                    for col in possible_date_columns:
                        if col in df.columns:
                            date_column = col
                            break
                    
                    if date_column:
                        try:
                            df[date_column] = pd.to_datetime(df[date_column])
                            st.metric("Date Range", f"{df[date_column].min().date()} to {df[date_column].max().date()}")
                        except Exception as e:
                            st.warning(f"Could not parse date column '{date_column}': {str(e)}")
                    else:
                        st.warning("No date column found. Please ensure your data has a 'Timestamp', 'Date', or 'datetime' column.")
                    
                    # Try to find AQI column
                    aqi_column = None
                    possible_aqi_columns = ['AQI', 'aqi', 'Air_Quality_Index', 'Air Quality Index']
                    for col in possible_aqi_columns:
                        if col in df.columns:
                            aqi_column = col
                            break
                    
                    if aqi_column:
                        try:
                            # Check if AQI column is numeric
                            if not pd.api.types.is_numeric_dtype(df[aqi_column]):
                                df[aqi_column] = pd.to_numeric(df[aqi_column], errors='coerce')
                            st.metric("AQI Range", f"{df[aqi_column].min():.1f} - {df[aqi_column].max():.1f}")
                        except Exception as e:
                            st.warning(f"Could not parse AQI column '{aqi_column}': {str(e)}")
                    else:
                        st.warning("No AQI column found. Please ensure your data has an 'AQI' column.")
                
                # Process data button
                if st.button("Process Data", type="primary"):
                    with st.spinner("Processing data..."):
                        try:
                            # Step 1: Auto-reformat the data
                            st.info("Step 1: Auto-reformatting data to standard format...")
                            try:
                                reformatted_df = auto_reformat_data(df)
                                st.success("✓ Data reformatted successfully!")
                                
                                # Show reformatting summary
                                st.subheader("Reformatting Summary")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Original Columns", len(df.columns))
                                    st.metric("Final Columns", len(reformatted_df.columns))
                                with col2:
                                    st.metric("Original Records", len(df))
                                    st.metric("Final Records", len(reformatted_df))
                                
                                # Show sample of reformatted data with AQI results
                                st.subheader("📊 Reformatted Data Preview with AQI Analysis")
                                
                                # Create tabs for different views
                                preview_tab1, preview_tab2, preview_tab3 = st.tabs(["Data Sample", "AQI Statistics", "AQI Distribution"])
                                
                                with preview_tab1:
                                    # Show first 10 rows with AQI information highlighted
                                    sample_df = reformatted_df.head(10)
                                    st.dataframe(sample_df, use_container_width=True)
                                    
                                    # Show column information
                                    st.subheader("📋 Column Information")
                                    col_info_cols = st.columns(2)
                                    with col_info_cols[0]:
                                        st.write("**Core Columns:**")
                                        core_cols = ['Timestamp', 'AQI', 'PM2.5', 'PM10', 'NO2', 'CO', 'SO2', 'O3']
                                        for col in core_cols:
                                            if col in reformatted_df.columns:
                                                st.write(f"• {col}: ✅ Available")
                                    
                                    with col_info_cols[1]:
                                        st.write("**AQI Analysis Columns:**")
                                        aqi_cols = ['AQI_Category', 'AQI_Color', 'Health_Message', 'Dominant_Pollutant', 'Dominant_Pollutant_SubIndex']
                                        for col in aqi_cols:
                                            if col in reformatted_df.columns:
                                                st.write(f"• {col}: ✅ Calculated")
                                
                                with preview_tab2:
                                    # Show AQI statistics
                                    if 'AQI' in reformatted_df.columns:
                                        st.subheader("📈 AQI Statistics")
                                        
                                        aqi_stats_cols = st.columns(4)
                                        with aqi_stats_cols[0]:
                                            st.metric("Mean AQI", f"{reformatted_df['AQI'].mean():.1f}")
                                        with aqi_stats_cols[1]:
                                            st.metric("Median AQI", f"{reformatted_df['AQI'].median():.1f}")
                                        with aqi_stats_cols[2]:
                                            st.metric("Min AQI", f"{reformatted_df['AQI'].min():.1f}")
                                        with aqi_stats_cols[3]:
                                            st.metric("Max AQI", f"{reformatted_df['AQI'].max():.1f}")
                                        
                                        # Show AQI category distribution
                                        if 'AQI_Category' in reformatted_df.columns:
                                            st.subheader("🏷️ AQI Category Distribution")
                                            category_counts = reformatted_df['AQI_Category'].value_counts()
                                            category_df = pd.DataFrame({
                                                'Category': category_counts.index,
                                                'Count': category_counts.values,
                                                'Percentage': (category_counts.values / len(reformatted_df) * 100).round(1)
                                            })
                                            st.dataframe(category_df, use_container_width=True)
                                        
                                        # Show dominant pollutant distribution
                                        if 'Dominant_Pollutant' in reformatted_df.columns:
                                            st.subheader("🔬 Dominant Pollutant Distribution")
                                            pollutant_counts = reformatted_df['Dominant_Pollutant'].value_counts()
                                            pollutant_df = pd.DataFrame({
                                                'Pollutant': pollutant_counts.index,
                                                'Count': pollutant_counts.values,
                                                'Percentage': (pollutant_counts.values / len(reformatted_df) * 100).round(1)
                                            })
                                            st.dataframe(pollutant_df.head(10), use_container_width=True)
                                
                                with preview_tab3:
                                    # Show AQI distribution visualization
                                    if 'AQI_Category' in reformatted_df.columns:
                                        st.subheader("📊 AQI Distribution Overview")
                                        
                                        # Create summary statistics
                                        dist_cols = st.columns(3)
                                        with dist_cols[0]:
                                            good_count = (reformatted_df['AQI_Category'] == 'Good').sum()
                                            st.metric("Good Days", good_count, f"{good_count/len(reformatted_df)*100:.1f}%")
                                        
                                        with dist_cols[1]:
                                            moderate_count = (reformatted_df['AQI_Category'] == 'Moderate').sum()
                                            st.metric("Moderate Days", moderate_count, f"{moderate_count/len(reformatted_df)*100:.1f}%")
                                        
                                        with dist_cols[2]:
                                            unhealthy_count = reformatted_df['AQI_Category'].str.contains('Unhealthy').sum()
                                            st.metric("Unhealthy Days", unhealthy_count, f"{unhealthy_count/len(reformatted_df)*100:.1f}%")
                                        
                                        # Show sample health messages
                                        st.subheader("💬 Health Recommendations Sample")
                                        if 'Health_Message' in reformatted_df.columns:
                                            sample_messages = reformatted_df['Health_Message'].dropna().unique()[:5]
                                            for i, message in enumerate(sample_messages, 1):
                                                st.write(f"{i}. {message}")
                                
                                # Show column mapping
                                st.subheader("🔄 Column Standardization")
                                original_cols = df.columns.tolist()
                                final_cols = reformatted_df.columns.tolist()
                                mapping_info = []
                                for orig, final in zip(original_cols[:14], final_cols[:14]):  # Show first 14
                                    if orig != final:
                                        mapping_info.append(f"• {orig} → {final}")
                                    else:
                                        mapping_info.append(f"• {orig} (unchanged)")
                                
                                if mapping_info:
                                    st.markdown("\n".join(mapping_info))
                                
                            except Exception as e:
                                st.error(f"Data reformatting failed: {str(e)}")
                                st.info("Attempting to continue with original data...")
                                reformatted_df = df
                            
                            # Step 2: Continue with standard processing using reformatted data
                            st.info("Step 2: Processing data for forecasting...")
                            
                            # Data validation before processing
                            st.subheader("Data Validation")
                            validation_passed = True
                            validation_messages = []
                            
                            # Check minimum data requirements
                            min_rows_required = 10  # Minimum rows for basic modeling
                            ideal_rows_required = 50  # Ideal rows for good modeling
                            
                            if len(reformatted_df) < min_rows_required:
                                validation_passed = False
                                validation_messages.append(f"❌ Insufficient data: Only {len(reformatted_df)} rows (minimum {min_rows_required} required)")
                            elif len(reformatted_df) < ideal_rows_required:
                                validation_messages.append(f"⚠️ Limited data: {len(reformatted_df)} rows (ideal: {ideal_rows_required}+ for better accuracy)")
                            else:
                                validation_messages.append(f"✅ Sufficient data: {len(reformatted_df)} rows")
                            
                            # Check AQI data quality
                            if 'AQI' in reformatted_df.columns:
                                valid_aqi = reformatted_df['AQI'].notna().sum()
                                if valid_aqi < min_rows_required:
                                    validation_passed = False
                                    validation_messages.append(f"❌ Insufficient AQI data: Only {valid_aqi} valid AQI values")
                                else:
                                    validation_messages.append(f"✅ Sufficient AQI data: {valid_aqi} valid values")
                                    
                                # Check AQI variation
                                aqi_std = reformatted_df['AQI'].std()
                                if aqi_std < 1:
                                    validation_messages.append(f"⚠️ Low AQI variation: {aqi_std:.2f} (may affect model quality)")
                                else:
                                    validation_messages.append(f"✅ Good AQI variation: {aqi_std:.2f}")
                            
                            # Check date range
                            if 'Timestamp' in reformatted_df.columns:
                                date_range = (reformatted_df['Timestamp'].max() - reformatted_df['Timestamp'].min()).days
                                if date_range < 1:
                                    validation_messages.append(f"⚠️ Limited time range: {date_range} days")
                                else:
                                    validation_messages.append(f"✅ Good time range: {date_range} days")
                            
                            # Display validation results
                            for message in validation_messages:
                                st.write(message)
                            
                            if not validation_passed:
                                st.error("Data validation failed. Please provide more or better quality data.")
                                st.info("Recommendations:")
                                st.write("• Ensure your CSV has at least 10 rows of data")
                                st.write("• Check that AQI values are present and numeric")
                                st.write("• Verify date column is properly formatted")
                                st.write("• Remove rows with missing critical values")
                                return
                            
                            # Create temporary config with standardized column names
                            config_data = {
                                'data': {
                                    'date_column': 'Timestamp',
                                    'target_column': 'AQI',
                                    'pollutant_columns': ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'],
                                    'missing_threshold': 0.5,  # Increased tolerance for small datasets
                                    'outlier_threshold': 3.0
                                },
                                'prophet': {
                                    'changepoint_prior_scale': 0.1,
                                    'seasonality_mode': 'multiplicative',
                                    'weekly_seasonality': True,
                                    'yearly_seasonality': True,
                                    'daily_seasonality': False,
                                    'uncertainty_samples': 1000,
                                    'interval_width': confidence_level
                                },
                                'arima': {
                                    'max_p': 5, 'max_q': 5, 'max_order': 6,
                                    'seasonal': True, 'm': 7, 'stepwise': True,
                                    'alpha': 1 - confidence_level
                                },
                                'forecasting': {
                                    'prophet_weight': prophet_weight,
                                    'arima_weight': arima_weight,
                                    'confidence_level': confidence_level
                                }
                            }
                            
                            # Save temporary config
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                                yaml.dump(config_data, f)
                                temp_config_path = f.name
                            
                            # Initialize components
                            config = Config(temp_config_path)
                            processor = DataProcessor(config)
                            
                            # Process data with error handling
                            try:
                                processed_data = processor.process_data(reformatted_df)
                                
                                # Validate processed data
                                if processed_data is None or len(processed_data) == 0:
                                    raise ValueError("Data processing returned empty dataset")
                                
                                if len(processed_data) < 2:
                                    raise ValueError(f"Processed data has only {len(processed_data)} rows (minimum 2 required)")
                                
                                # Check for NaN values in critical columns
                                if 'AQI' in processed_data.columns:
                                    valid_aqi_count = processed_data['AQI'].notna().sum()
                                    if valid_aqi_count < 2:
                                        raise ValueError(f"Only {valid_aqi_count} valid AQI values in processed data")
                                
                                st.success("✓ Data processing completed successfully!")
                                
                            except Exception as processing_error:
                                st.error(f"Data processing failed: {str(processing_error)}")
                                st.info("Attempting to use simplified processing...")
                                
                                # Fallback: minimal processing
                                try:
                                    processed_data = reformatted_df.copy()
                                    
                                    # Basic cleaning only
                                    if 'AQI' in processed_data.columns:
                                        processed_data['AQI'] = pd.to_numeric(processed_data['AQI'], errors='coerce')
                                        processed_data = processed_data.dropna(subset=['AQI'])
                                    
                                    if 'Timestamp' in processed_data.columns:
                                        processed_data['Timestamp'] = pd.to_datetime(processed_data['Timestamp'], errors='coerce')
                                        processed_data = processed_data.dropna(subset=['Timestamp'])
                                        processed_data = processed_data.sort_values('Timestamp')
                                    
                                    if len(processed_data) < 2:
                                        raise ValueError(f"Even simplified processing resulted in only {len(processed_data)} rows")
                                    
                                    st.success("✓ Simplified data processing completed!")
                                    
                                except Exception as fallback_error:
                                    st.error(f"All processing methods failed: {str(fallback_error)}")
                                    return
                            
                            # Store in session state
                            st.session_state.processed_data = processed_data
                            st.session_state.data_loaded = True
                            
                            # Calculate and store data hash
                            current_hash = calculate_data_hash(processed_data)
                            if current_hash != st.session_state.last_data_hash:
                                # Data changed, reset models and forecasts
                                st.session_state.last_data_hash = current_hash
                                st.session_state.models_trained = False
                                st.session_state.forecasts_generated = False
                                st.session_state.prophet_model = None
                                st.session_state.arima_model = None
                                st.session_state.training_in_progress = False
                                st.info("📊 Data changed - models will need to be retrained")
                            
                            st.success("✓ Data processing completed successfully!")
                            
                            # Display processed data info
                            st.subheader("Final Processed Data Summary")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Processed Records", len(processed_data))
                            with col2:
                                if 'AQI' in processed_data.columns:
                                    st.metric("Mean AQI", f"{processed_data['AQI'].mean():.1f}")
                            with col3:
                                if 'AQI' in processed_data.columns:
                                    st.metric("Std Dev AQI", f"{processed_data['AQI'].std():.1f}")
                            
                            # Show data quality metrics
                            st.subheader("Data Quality Metrics")
                            quality_metrics = []
                            
                            # Check for missing values
                            missing_pct = (processed_data.isnull().sum() / len(processed_data)) * 100
                            high_missing = missing_pct[missing_pct > 5]
                            if not high_missing.empty:
                                quality_metrics.append(f"⚠️ High missing values in: {', '.join(high_missing.index)}")
                            else:
                                quality_metrics.append("✅ Low missing values (<5%)")
                            
                            # Check data range
                            if 'AQI' in processed_data.columns:
                                aqi_range = processed_data['AQI'].max() - processed_data['AQI'].min()
                                if aqi_range > 100:
                                    quality_metrics.append(f"✅ Good AQI variation: {aqi_range:.1f}")
                                else:
                                    quality_metrics.append(f"⚠️ Low AQI variation: {aqi_range:.1f}")
                            
                            # Check date range
                            if 'Timestamp' in processed_data.columns:
                                date_range = (processed_data['Timestamp'].max() - processed_data['Timestamp'].min()).days
                                quality_metrics.append(f"✅ Date range: {date_range} days")
                            elif hasattr(processed_data.index, 'date'):
                                date_range = (processed_data.index.max() - processed_data.index.min()).days
                                quality_metrics.append(f"✅ Date range: {date_range} days")
                            
                            for metric in quality_metrics:
                                st.write(metric)
                            
                        except Exception as e:
                            st.error(f"Error processing data: {str(e)}")
                            st.session_state.data_loaded = False
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
        else:
            st.info("Please upload a CSV file to get started")
            
            # Show sample data format
            st.subheader("Expected Data Format")
            sample_data = pd.DataFrame({
                'Timestamp': ['2024-01-01 00:00:00', '2024-01-01 01:00:00', '2024-01-01 02:00:00'],
                'AQI': [45, 52, 48],
                'PM2.5': [12.5, 15.2, 13.8],
                'PM10': [25.3, 28.1, 26.7]
            })
            st.dataframe(sample_data)
    
    with tab2:
        st.header("Model Training")
        
        if not st.session_state.data_loaded:
            st.warning("Please upload and process data first")
        else:
            # Check if models are already trained and valid
            if are_models_valid():
                # Compact status header
                st.success("✅ Models are already trained and ready to use!")
                
                # Efficient status display in a single row
                status_col1, status_col2, status_col3, status_col4 = st.columns(4)
                with status_col1:
                    st.metric("Prophet", "✅ Trained" if st.session_state.prophet_model else "❌ Not Available")
                with status_col2:
                    st.metric("ARIMA", "✅ Trained" if st.session_state.arima_model else "❌ Not Available")
                with status_col3:
                    if st.session_state.model_training_time:
                        st.metric("Last Trained", st.session_state.model_training_time.strftime("%H:%M:%S"))
                with status_col4:
                    data = st.session_state.processed_data
                    st.metric("Data Points", f"{len(data):,}")
                
                # Retrain options in a compact row
                st.markdown("---")
                st.write("**🔄 Model Management:**")
                
                retrain_col1, retrain_col2 = st.columns(2)
                with retrain_col1:
                    if st.button("🔄 Retrain Models", type="secondary", use_container_width=True):
                        st.session_state.models_trained = False
                        st.session_state.forecasts_generated = False
                        st.session_state.prophet_model = None
                        st.session_state.arima_model = None
                        st.session_state.training_in_progress = False
                        st.rerun()
                
                with retrain_col2:
                    if st.button("🗑️ Clear All Models", type="secondary", use_container_width=True):
                        st.session_state.models_trained = False
                        st.session_state.forecasts_generated = False
                        st.session_state.prophet_model = None
                        st.session_state.arima_model = None
                        st.session_state.training_in_progress = False
                        st.session_state.last_data_hash = None
                        st.rerun()
                        
            else:
                # Training section
                st.info("🚀 Ready to train forecasting models on your data")
                
                # Training button with full width
                if st.button("🤖 Train Models", type="primary", use_container_width=True):
                    st.session_state.training_in_progress = True
                    st.rerun()
                    
                if st.session_state.training_in_progress:
                    with st.spinner("Training models... This may take a few minutes..."):
                        try:
                            # Validate data before training
                            if st.session_state.processed_data is None:
                                st.error("No processed data available. Please process data first.")
                                st.session_state.training_in_progress = False
                                return
                            
                            data = st.session_state.processed_data
                            data_rows = len(data)
                            
                            # Check minimum requirements for training
                            if data_rows < 2:
                                st.error(f"Insufficient data for training: Only {data_rows} rows available (minimum 2 required).")
                                st.session_state.training_in_progress = False
                                return
                            
                            # Adjust model parameters based on data size
                            if data_rows < 10:
                                st.warning("Limited data detected. Using simplified model parameters...")
                                prophet_seasonality = False
                                arima_seasonality = False
                            elif data_rows < 30:
                                st.warning("Small dataset detected. Using conservative model parameters...")
                                prophet_seasonality = True
                                arima_seasonality = False
                            else:
                                prophet_seasonality = True
                                arima_seasonality = True
                            
                            # Create temporary config with adjusted parameters
                            config_data = {
                                'data': {
                                    'date_column': 'Timestamp',
                                    'target_column': 'AQI',
                                    'pollutant_columns': ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'],
                                    'missing_threshold': 0.5,
                                    'outlier_threshold': 3.0
                                },
                                'prophet': {
                                    'changepoint_prior_scale': 0.5 if data_rows < 10 else 0.1,
                                    'seasonality_mode': 'multiplicative',
                                    'weekly_seasonality': prophet_seasonality,
                                    'yearly_seasonality': prophet_seasonality and data_rows >= 365,
                                    'daily_seasonality': False,
                                    'uncertainty_samples': 1000,
                                    'interval_width': confidence_level
                                },
                                'arima': {
                                    'max_p': min(3, data_rows // 3),
                                    'max_q': min(3, data_rows // 3),
                                    'max_order': min(4, data_rows // 2),
                                    'seasonal': arima_seasonality,
                                    'stepwise': True,
                                    'suppress_warnings': True
                                },
                                'forecasting': {
                                    'prophet_weight': prophet_weight,
                                    'arima_weight': arima_weight,
                                    'confidence_level': confidence_level
                                }
                            }
                        
                        # Save temporary config
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                                yaml.dump(config_data, f)
                                temp_config_path = f.name
                            
                            # Initialize components
                            config = Config(temp_config_path)
                            processor = DataProcessor(config)
                            model_trainer = ModelTrainer(config)
                            prophet_trainer = ProphetTrainer(config)
                            arima_trainer = ARIMATrainer(config)
                            forecaster = Forecaster(config)
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Train Prophet model
                            status_text.text("Training Prophet model...")
                            progress_bar.progress(20)
                            
                            try:
                                # Use the optimized ModelTrainer class
                                prophet_model = model_trainer.train_prophet(data)
                                progress_bar.progress(40)
                                status_text.text("Prophet model trained successfully!")
                                st.success("Prophet model created successfully!")
                            except Exception as prophet_error:
                                st.error(f"Prophet training failed: {str(prophet_error)}")
                                prophet_model = None
                            
                            # Train ARIMA model
                            status_text.text("Training ARIMA model...")
                            progress_bar.progress(60)
                            
                            try:
                                arima_model = model_trainer.train_arima(data)
                                progress_bar.progress(80)
                                status_text.text("ARIMA model trained successfully!")
                                st.success("ARIMA model trained successfully!")
                            except Exception as arima_error:
                                st.warning(f"ARIMA training failed: {str(arima_error)}")
                                arima_model = None
                            
                            # Final progress update
                            progress_bar.progress(90)
                            status_text.text("Finalizing models...")
                            
                            # Store models in session state
                            st.session_state.prophet_model = prophet_model
                            st.session_state.arima_model = arima_model
                            st.session_state.models_trained = True
                            st.session_state.training_in_progress = False
                            st.session_state.model_training_time = datetime.now()
                            st.session_state.last_data_hash = calculate_data_hash(data)
                            
                            progress_bar.progress(100)
                            status_text.text("Models trained successfully!")
                            
                            st.success("Models trained successfully!")
                            
                            # Compact evaluation metrics display
                            st.markdown("---")
                            st.subheader("📊 Model Performance")
                            
                            # Create tabs for organized model evaluation
                            eval_tab1, eval_tab2, eval_tab3 = st.tabs(["Prophet", "ARIMA", "Comparison"])
                            
                            with eval_tab1:
                                st.write("**Prophet Model Performance**")
                                try:
                                    prophet_metrics = prophet_trainer.evaluate_prophet(prophet_model, data)
                                    
                                    # Metrics in a grid
                                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                                    with metric_col1:
                                        st.metric("R²", f"{prophet_metrics.get('r2', 0):.3f}")
                                        st.metric("RMSE", f"{prophet_metrics.get('rmse', 0):.2f}")
                                    with metric_col2:
                                        st.metric("MAE", f"{prophet_metrics.get('mae', 0):.2f}")
                                        st.metric("MAPE", f"{prophet_metrics.get('mape', 0):.2%}")
                                    with metric_col3:
                                        st.metric("Accuracy", f"{prophet_metrics.get('accuracy', 0):.1f}%")
                                        # Quality based on actual performance (adjusted for air quality forecasting)
                                        r2_score = prophet_metrics.get('r2', 0)
                                        accuracy = prophet_metrics.get('accuracy', 0)
                                        if r2_score >= 0.7 and accuracy >= 80:
                                            data_quality = "Excellent"
                                        elif r2_score >= 0.5 and accuracy >= 75:
                                            data_quality = "Good"
                                        elif r2_score >= 0.3 and accuracy >= 70:
                                            data_quality = "Fair"
                                        else:
                                            data_quality = "Poor"
                                        st.metric("Quality", data_quality)
                                except Exception as eval_error:
                                    st.warning(f"Prophet evaluation failed: {str(eval_error)}")
                                    st.metric("Status", "❌ Evaluation Failed")
                            
                            with eval_tab2:
                                st.write("**ARIMA Model Performance**")
                                if arima_model is not None:
                                    try:
                                        arima_metrics = arima_trainer.evaluate_arima(arima_model, data)
                                        
                                        # Metrics in a grid
                                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                                        with metric_col1:
                                            st.metric("R²", f"{arima_metrics.get('r2', 0):.3f}")
                                            st.metric("RMSE", f"{arima_metrics.get('rmse', 0):.2f}")
                                        with metric_col2:
                                            st.metric("MAE", f"{arima_metrics.get('mae', 0):.2f}")
                                            st.metric("MAPE", f"{arima_metrics.get('mape', 0):.2%}")
                                        with metric_col3:
                                            st.metric("Accuracy", f"{arima_metrics.get('accuracy', 0):.1f}%")
                                            # Quality based on actual performance (adjusted for air quality forecasting)
                                            r2_score = arima_metrics.get('r2', 0)
                                            accuracy = arima_metrics.get('accuracy', 0)
                                            if r2_score >= 0.7 and accuracy >= 80:
                                                data_quality = "Excellent"
                                            elif r2_score >= 0.5 and accuracy >= 75:
                                                data_quality = "Good"
                                            elif r2_score >= 0.3 and accuracy >= 70:
                                                data_quality = "Fair"
                                            else:
                                                data_quality = "Poor"
                                            st.metric("Quality", data_quality)
                                    except Exception as eval_error:
                                        st.warning(f"ARIMA evaluation failed: {str(eval_error)}")
                                        st.metric("Status", "❌ Evaluation Failed")
                                else:
                                    st.warning("ARIMA model not available for evaluation")
                                    st.metric("Status", "❌ Model Not Trained")
                            
                            with eval_tab3:
                                st.write("**Model Comparison & Quality Assessment**")
                                
                                if arima_model is not None:
                                    try:
                                        prophet_metrics = prophet_trainer.evaluate_prophet(prophet_model, data)
                                        arima_metrics = arima_trainer.evaluate_arima(arima_model, data)
                                        
                                        prophet_r2 = prophet_metrics.get('r2', 0)
                                        arima_r2 = arima_metrics.get('r2', 0)
                                        
                                        # Comparison metrics
                                        comp_col1, comp_col2, comp_col3 = st.columns(3)
                                        with comp_col1:
                                            if prophet_r2 > arima_r2:
                                                st.success("🏆 Prophet performs better")
                                            elif arima_r2 > prophet_r2:
                                                st.success("🏆 ARIMA performs better")
                                            else:
                                                st.info("⚖️ Both models perform similarly")
                                            
                                            ensemble_recommendation = "Prophet + ARIMA" if prophet_r2 > 0.7 and arima_r2 > 0.7 else "Prophet-weighted" if prophet_r2 > 0.7 else "ARIMA-weighted" if arima_r2 > 0.7 else "Ensemble not\nrecommended"
                                            st.metric("Ensemble", ensemble_recommendation)
                                        
                                        with comp_col2:
                                            avg_r2 = (prophet_r2 + arima_r2) / 2
                                            avg_accuracy = (prophet_metrics.get('accuracy', 0) + arima_metrics.get('accuracy', 0)) / 2
                                            
                                            # Use same quality assessment as comprehensive evaluation
                                            if avg_r2 >= 0.7 and avg_accuracy >= 80:
                                                overall_quality = "Excellent"
                                            elif avg_r2 >= 0.5 and avg_accuracy >= 75:
                                                overall_quality = "Good"
                                            elif avg_r2 >= 0.3 and avg_accuracy >= 70:
                                                overall_quality = "Fair"
                                            else:
                                                overall_quality = "Poor"
                                            
                                            st.metric("Overall Quality", overall_quality)
                                            st.metric("Average R²", f"{avg_r2:.3f}")
                                            st.metric("Average Accuracy", f"{avg_accuracy:.1f}%")
                                        
                                        with comp_col3:
                                            # Calculate comprehensive quality score based on actual model performance
                                            prophet_r2 = prophet_metrics.get('r2', 0)
                                            prophet_mape = prophet_metrics.get('mape', 100)
                                            prophet_accuracy = prophet_metrics.get('accuracy', 0)
                                            
                                            arima_r2 = arima_metrics.get('r2', 0)
                                            arima_mape = arima_metrics.get('mape', 100)
                                            arima_accuracy = arima_metrics.get('accuracy', 0)
                                            
                                            # Quality based on actual model performance metrics
                                            avg_r2 = (prophet_r2 + arima_r2) / 2
                                            avg_mape = (prophet_mape + arima_mape) / 2
                                            avg_accuracy = (prophet_accuracy + arima_accuracy) / 2
                                            
                                            # Calculate quality score based on performance only
                                            quality_score = (
                                                (avg_r2 * 0.4) +                    # R² score (40% weight)
                                                ((100 - avg_mape) / 100 * 0.3) +     # MAPE converted to accuracy (30% weight)
                                                (avg_accuracy / 100 * 0.3)          # Direct accuracy (30% weight)
                                            )
                                            
                                            # Determine quality level based on actual performance (adjusted for air quality forecasting)
                                            if avg_r2 >= 0.7 and avg_accuracy >= 80:
                                                quality_level = "Excellent"
                                                reliability = "Very High"
                                            elif avg_r2 >= 0.5 and avg_accuracy >= 75:
                                                quality_level = "Good"
                                                reliability = "High"
                                            elif avg_r2 >= 0.3 and avg_accuracy >= 70:
                                                quality_level = "Fair"
                                                reliability = "Medium"
                                            else:
                                                quality_level = "Poor"
                                                reliability = "Low"
                                            
                                            st.metric("Quality Score", f"{quality_score:.3f}")
                                            st.metric("Quality Level", quality_level)
                                            st.metric("Reliability", reliability)
                                            
                                            # Add explanation for quality assessment
                                            with st.expander("📊 Quality Assessment Details", expanded=False):
                                                st.write("### Performance-Based Quality Factors")
                                                st.write("")
                                                st.write(f"**R² Score**: {avg_r2:.3f}")
                                                st.write("Weight: 40%")
                                                st.write("")
                                                st.write(f"**MAPE**: {avg_mape:.1f}%")
                                                st.write(f"Accuracy: {(100-avg_mape):.1f}%")
                                                st.write("Weight: 30%")
                                                st.write("")
                                                st.write(f"**Model Accuracy**: {avg_accuracy:.1f}%")
                                                st.write("Weight: 30%")
                                                st.write("")
                                                st.write(f"**Final Quality Score**: {quality_score:.3f}")
                                                st.write("")
                                                st.write("### Quality Thresholds")
                                                st.write("*Adjusted for Air Quality Forecasting*")
                                                st.write("")
                                                st.write("**Excellent**")
                                                st.write("• R² ≥ 0.7")
                                                st.write("• Accuracy ≥ 80%")
                                                st.write("")
                                                st.write("**Good**")
                                                st.write("• R² ≥ 0.5")
                                                st.write("• Accuracy ≥ 75%")
                                                st.write("")
                                                st.write("**Fair**")
                                                st.write("• R² ≥ 0.3")
                                                st.write("• Accuracy ≥ 70%")
                                                st.write("")
                                                st.write("**Poor**")
                                                st.write("• Below Fair thresholds")
                                                st.write("")
                                                st.info("💡 Note: Thresholds adjusted for air quality forecasting where R² values are naturally lower due to data variability")
                                    except:
                                        st.info("Comparison not available")
                                else:
                                    st.info("ARIMA model not available for comparison")
                            
                            # Compact model info
                            st.markdown("---")
                            st.subheader("🔧 Model Information")
                            
                            info_tab1, info_tab2 = st.tabs(["Training Details", "Expected Performance"])
                            
                            with info_tab1:
                                info_col1, info_col2 = st.columns(2)
                                with info_col1:
                                    st.write("**Prophet Model**")
                                    if data_rows < 10:
                                        st.info("Simplified parameters (small dataset)")
                                    else:
                                        st.info("Multiplicative seasonality")
                                    st.write(f"• Data points: {data_rows:,}")
                                    st.write(f"• Seasonality: {'Enabled' if prophet_seasonality else 'Disabled'}")
                                
                                with info_col2:
                                    st.write("**ARIMA Model**")
                                    if arima_model is not None:
                                        st.info("Automatic parameter selection")
                                        st.write("• Seasonal: Enabled" if arima_seasonality else "• Seasonal: Disabled")
                                        st.write("• Auto SARIMA: Yes")
                                    else:
                                        st.warning("ARIMA model not trained")
                            
                            with info_tab2:
                                perf_col1, perf_col2, perf_col3 = st.columns(3)
                                with perf_col1:
                                    # More sophisticated accuracy estimation
                                    data_std = data['AQI'].std()
                                    data_mean = data['AQI'].mean()
                                    data_range = data['AQI'].max() - data['AQI'].min()
                                    coefficient_of_variation = data_std / data_mean if data_mean > 0 else 0
                                    
                                    # Consider multiple factors for accuracy estimation
                                    if data_rows > 1000 and coefficient_of_variation < 0.3:
                                        accuracy_est = "High (85-95%)"
                                    elif data_rows > 500 and coefficient_of_variation < 0.5:
                                        accuracy_est = "Medium (70-85%)"
                                    elif data_rows > 100:
                                        accuracy_est = "Fair (60-70%)"
                                    else:
                                        accuracy_est = "Low (<60%)"
                                    
                                    st.metric("Expected Accuracy", accuracy_est)
                                    st.metric("Data CV", f"{coefficient_of_variation:.3f}")
                                    st.metric("Sample Size", f"{data_rows:,}")
                                
                                with perf_col2:
                                    if data_rows > 365:
                                        reliability = "High"
                                    elif data_rows > 90:
                                        reliability = "Medium"
                                    else:
                                        reliability = "Low"
                                    st.metric("Forecast Reliability", reliability)
                                
                                with perf_col3:
                                    if arima_model is not None:
                                        ensemble_type = "Prophet + ARIMA"
                                    else:
                                        ensemble_type = "Prophet Only"
                                    st.metric("Ensemble Type", ensemble_type)
                        
                        except Exception as e:
                            st.error(f"Error training models: {str(e)}")
                            st.session_state.models_trained = False
                            st.session_state.training_in_progress = False
                            st.session_state.prophet_model = None
                            st.session_state.arima_model = None
    
    with tab3:
        st.header("Forecast Generation")
        
        if not are_models_valid():
            st.warning("Please train models first")
        else:
            # Display model status
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Prophet Model", "✅ Ready" if st.session_state.prophet_model else "❌ Not Available")
            with col2:
                st.metric("ARIMA Model", "✅ Ready" if st.session_state.arima_model else "❌ Not Available")
                
            if st.button("Generate Forecasts", type="primary"):
                with st.spinner(f"Generating {forecast_days}-day forecasts..."):
                    try:
                        # Create temporary config
                        config_data = {
                            'forecasting': {
                                'prophet_weight': prophet_weight,
                                'arima_weight': arima_weight,
                                'confidence_level': confidence_level,
                                'default_horizon': forecast_days
                            }
                        }
                        
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                            yaml.dump(config_data, f)
                            temp_config_path = f.name
                        
                        config = Config(temp_config_path)
                        forecaster = Forecaster(config)
                        
                        # Generate forecasts
                        try:
                            forecasts = forecaster.generate_ensemble_forecast(
                                st.session_state.prophet_model,
                                st.session_state.arima_model,
                                st.session_state.processed_data,
                                forecast_days
                            )
                            
                            # Store forecasts
                            st.session_state.forecasts = forecasts
                            st.session_state.forecasts_generated = True
                            
                            st.success("Forecasts generated successfully!")
                            
                        except Exception as forecast_error:
                            st.error(f"Error generating forecasts: {str(forecast_error)}")
                            
                            # Try to create a simple fallback forecast
                            try:
                                st.info("Attempting to create simple forecast...")
                                data = st.session_state.processed_data
                                
                                # Create simple forecast using last values
                                last_aqi = data['AQI'].iloc[-1]
                                
                                # Get last date from either column or index
                                if 'Timestamp' in data.columns:
                                    last_date = data['Timestamp'].iloc[-1]
                                else:
                                    last_date = data.index[-1]
                                
                                dates = pd.date_range(
                                    start=last_date + pd.Timedelta(days=1),
                                    periods=forecast_days,
                                    freq='D'
                                )
                                
                                # Simple forecast with some variation
                                np.random.seed(42)
                                variation = np.random.normal(0, data['AQI'].std() * 0.1, forecast_days)
                                forecast_values = np.clip(last_aqi + variation, 0, 500)
                                
                                # Create forecast DataFrame
                                forecasts = pd.DataFrame({
                                    'Forecasted_AQI': forecast_values,
                                    'Lower_Bound': forecast_values * 0.8,
                                    'Upper_Bound': forecast_values * 1.2,
                                    'Prophet_Forecast': forecast_values,
                                    'ARIMA_Forecast': forecast_values
                                }, index=dates)
                                
                                # Add AQI categories
                                def get_simple_aqi_category(aqi):
                                    if aqi <= 50:
                                        return "Good"
                                    elif aqi <= 100:
                                        return "Moderate"
                                    elif aqi <= 150:
                                        return "Unhealthy for Sensitive Groups"
                                    elif aqi <= 200:
                                        return "Unhealthy"
                                    elif aqi <= 300:
                                        return "Very Unhealthy"
                                    else:
                                        return "Hazardous"
                                
                                forecasts['AQI_Category'] = forecasts['Forecasted_AQI'].apply(get_simple_aqi_category)
                                forecasts['Health_Recommendation'] = forecasts['AQI_Category'].apply(lambda x: 
                                    "Enjoy outdoor activities!" if x == "Good" else
                                    "Sensitive groups should take precautions" if x == "Moderate" else
                                    "Reduce prolonged outdoor exertion" if x == "Unhealthy for Sensitive Groups" else
                                    "Everyone should reduce outdoor activities" if x == "Unhealthy" else
                                    "Avoid prolonged outdoor exertion" if x == "Very Unhealthy" else
                                    "Avoid all outdoor activities"
                                )
                                
                                st.session_state.forecasts = forecasts
                                st.session_state.forecasts_generated = True
                                
                                st.success("Simple forecast created successfully!")
                                st.warning("Note: Using simplified forecast due to model training issues. For better accuracy, ensure models are properly trained.")
                                
                            except Exception as fallback_error:
                                st.error(f"Fallback forecast also failed: {str(fallback_error)}")
                                st.session_state.forecasts_generated = False
                                return
                        
                        # Display forecast plot
                        st.subheader("Forecast Visualization")
                        fig = create_forecast_plot(forecasts, f"{forecast_days}-Day Air Quality Forecast")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Comprehensive Forecast Analysis
                        st.subheader("Forecast Analysis")
                        analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
                        
                        with analysis_col1:
                            st.metric("Forecast Period", f"{forecast_days} days")
                            st.metric("Starting AQI", f"{forecasts['Forecasted_AQI'].iloc[0]:.1f}")
                            st.metric("Ending AQI", f"{forecasts['Forecasted_AQI'].iloc[-1]:.1f}")
                        
                        with analysis_col2:
                            trend = forecasts['Forecasted_AQI'].iloc[-1] - forecasts['Forecasted_AQI'].iloc[0]
                            trend_dir = "↑ Increasing" if trend > 1 else "↓ Decreasing" if trend < -1 else "→ Stable"
                            st.metric("Overall Trend", trend_dir)
                            st.metric("Trend Magnitude", f"{abs(trend):.1f}")
                            
                            # Calculate volatility
                            volatility = forecasts['Forecasted_AQI'].std()
                            st.metric("Volatility", f"{volatility:.2f}")
                        
                        with analysis_col3:
                            # Count AQI categories
                            category_counts = forecasts['AQI_Category'].value_counts()
                            most_common = category_counts.index[0]
                            st.metric("Most Common Category", most_common)
                            st.metric("Category Count", f"{category_counts.iloc[0]} days")
                            
                            # Risk assessment
                            unhealthy_days = len(forecasts[forecasts['Forecasted_AQI'] > 100])
                            risk_level = "High" if unhealthy_days > forecast_days * 0.3 else "Medium" if unhealthy_days > 0 else "Low"
                            st.metric("Risk Level", risk_level)
                        
                        # Forecast Summary
                        st.subheader("Forecast Summary")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            current_aqi = forecasts['Forecasted_AQI'].iloc[0]
                            st.metric("Current AQI", f"{current_aqi:.1f}")
                        
                        with col2:
                            max_aqi = forecasts['Forecasted_AQI'].max()
                            st.metric("Max Forecast AQI", f"{max_aqi:.1f}")
                        
                        with col3:
                            min_aqi = forecasts['Forecasted_AQI'].min()
                            st.metric("Min Forecast AQI", f"{min_aqi:.1f}")
                        
                        with col4:
                            avg_aqi = forecasts['Forecasted_AQI'].mean()
                            st.metric("Average AQI", f"{avg_aqi:.1f}")
                        
                        # Confidence Intervals Analysis
                        st.subheader("Confidence Intervals Analysis")
                        confidence_col1, confidence_col2 = st.columns(2)
                        
                        with confidence_col1:
                            # Calculate average confidence interval width
                            avg_width = (forecasts['Upper_Bound'] - forecasts['Lower_Bound']).mean()
                            st.metric("Avg Interval Width", f"{avg_width:.1f}")
                            
                            # Calculate percentage uncertainty
                            avg_uncertainty = (avg_width / forecasts['Forecasted_AQI'].mean()) * 100
                            st.metric("Avg Uncertainty", f"{avg_uncertainty:.1f}%")
                        
                        with confidence_col2:
                            # Find most uncertain day
                            max_uncertainty_day = (forecasts['Upper_Bound'] - forecasts['Lower_Bound']).idxmax()
                            max_uncertainty = (forecasts.loc[max_uncertainty_day, 'Upper_Bound'] - forecasts.loc[max_uncertainty_day, 'Lower_Bound'])
                            st.metric("Max Uncertainty Day", max_uncertainty_day.strftime('%Y-%m-%d'))
                            st.metric("Max Uncertainty", f"{max_uncertainty:.1f}")
                        
                        # Model Contribution Analysis
                        if 'Prophet_Forecast' in forecasts.columns and 'ARIMA_Forecast' in forecasts.columns:
                            st.subheader("Model Contribution Analysis")
                            
                            # Calculate correlation between models
                            correlation = forecasts['Prophet_Forecast'].corr(forecasts['ARIMA_Forecast'])
                            st.write(f"**Model Correlation**: {correlation:.3f}")
                            
                            if correlation > 0.8:
                                st.info("🤝 High agreement between models - High confidence in forecasts")
                            elif correlation > 0.5:
                                st.info("⚖️ Moderate agreement between models - Reasonable confidence")
                            else:
                                st.warning("⚠️ Low agreement between models - Consider checking data quality")
                            
                            # Show model comparison chart
                            model_comparison_col1, model_comparison_col2 = st.columns(2)
                            
                            with model_comparison_col1:
                                st.write("**Prophet vs Ensemble**")
                                prophet_diff = (forecasts['Prophet_Forecast'] - forecasts['Forecasted_AQI']).abs().mean()
                                st.metric("Avg Difference", f"{prophet_diff:.2f}")
                                st.write("Prophet contribution: 70%")
                            
                            with model_comparison_col2:
                                st.write("**ARIMA vs Ensemble**")
                                arima_diff = (forecasts['ARIMA_Forecast'] - forecasts['Forecasted_AQI']).abs().mean()
                                st.metric("Avg Difference", f"{arima_diff:.2f}")
                                st.write("ARIMA contribution: 30%")
                        
                        # Detailed Forecast Table with Enhanced Information
                        st.subheader("Detailed Forecast")
                        forecast_display = forecasts[['Forecasted_AQI', 'Lower_Bound', 'Upper_Bound']].copy()
                        forecast_display.columns = ['Forecast AQI', 'Lower Bound', 'Upper Bound']
                        forecast_display['AQI Category'] = forecasts['AQI_Category']
                        forecast_display['Health Recommendation'] = forecasts['Health_Recommendation']
                        
                        # Add risk level indicator
                        def get_risk_level(aqi):
                            if aqi <= 50:
                                return "🟢 Low"
                            elif aqi <= 100:
                                return "🟡 Moderate"
                            elif aqi <= 150:
                                return "🟠 High for Sensitive"
                            elif aqi <= 200:
                                return "🔴 High"
                            elif aqi <= 300:
                                return "🟣 Very High"
                            else:
                                return "⚫ Hazardous"
                        
                        forecast_display['Risk Level'] = forecasts['Forecasted_AQI'].apply(get_risk_level)
                        
                        # Reorder columns for better display
                        forecast_display = forecast_display[['Risk Level', 'Forecast AQI', 'Lower Bound', 'Upper Bound', 'AQI Category', 'Health Recommendation']]
                        
                        st.dataframe(forecast_display, use_container_width=True)
                        
                        # Export Options
                        st.subheader("Export Options")
                        export_col1, export_col2, export_col3 = st.columns(3)
                        
                        with export_col1:
                            # CSV Export
                            csv = forecasts.to_csv(index=True)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv,
                                file_name=f"air_quality_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        
                        with export_col2:
                            # JSON Export
                            json_data = forecasts.to_json(indent=2)
                            st.download_button(
                                label="📄 Download JSON",
                                data=json_data,
                                file_name=f"air_quality_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                        
                        with export_col3:
                            # Summary Report
                            summary = f"""
Air Quality Forecast Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Forecast Period: {forecast_days} days
Average AQI: {avg_aqi:.1f}
Max AQI: {max_aqi:.1f}
Min AQI: {min_aqi:.1f}
Most Common Category: {most_common}
Risk Level: {risk_level}
"""
                            st.download_button(
                                label="📋 Download Summary",
                                data=summary,
                                file_name=f"forecast_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                        
                    except Exception as e:
                        st.error(f"Error generating forecasts: {str(e)}")
                        st.session_state.forecasts_generated = False
    
    with tab4:
        st.header("Health Analysis")
        
        if not st.session_state.forecasts_generated or not are_models_valid():
            st.warning("Please train models and generate forecasts first")
        else:
            # Display model and forecast status
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Models", "✅ Trained" if st.session_state.models_trained else "❌ Not Trained")
            with col2:
                st.metric("Forecasts", "✅ Generated" if st.session_state.forecasts_generated else "❌ Not Generated")
            with col3:
                if st.session_state.model_training_time:
                    st.metric("Models Trained", st.session_state.model_training_time.strftime("%H:%M:%S"))
                    
            forecasts = st.session_state.forecasts
            
            # Current AQI gauge
            current_aqi = forecasts['Forecasted_AQI'].iloc[0]
            category, color, recommendation = get_aqi_category(current_aqi)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("Current Air Quality")
                fig = create_aqi_gauge(current_aqi)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Health Recommendations")
                
                # Create a more readable health recommendation card
                health_color = {
                    'Good': '#00e400',
                    'Moderate': '#ffff00', 
                    'Unhealthy for Sensitive Groups': '#ff7e00',
                    'Unhealthy': '#ff0000',
                    'Very Unhealthy': '#8f3f97',
                    'Hazardous': '#7e0023'
                }.get(category, '#808080')
                
                # Enhanced health recommendation display
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {health_color}20, {health_color}10);
                    border-left: 5px solid {health_color};
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <h3 style="color: {health_color}; margin: 0 0 10px 0; font-size: 1.5em;">
                        {category}
                    </h3>
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <span style="
                            background: {health_color};
                            color: white;
                            padding: 8px 16px;
                            border-radius: 20px;
                            font-weight: bold;
                            font-size: 1.2em;
                        ">AQI: {current_aqi:.0f}</span>
                    </div>
                    <div style="
                        background: white;
                        padding: 15px;
                        border-radius: 8px;
                        border-left: 3px solid {health_color};
                    ">
                        <h4 style="margin: 0 0 8px 0; color: #333;">What this means for you:</h4>
                        <p style="margin: 0; line-height: 1.6; color: #555; font-size: 1.1em;">
                            {recommendation}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Comprehensive Health Impact Analysis
            st.subheader("Health Impact Analysis")
            health_col1, health_col2, health_col3 = st.columns(3)
            
            with health_col1:
                # Calculate health risk distribution
                risk_distribution = forecasts['AQI_Category'].value_counts()
                st.metric("Good Days", risk_distribution.get('Good', 0))
                st.metric("Moderate Days", risk_distribution.get('Moderate', 0))
                st.metric("Unhealthy Days", risk_distribution.get('Unhealthy for Sensitive Groups', 0) + 
                         risk_distribution.get('Unhealthy', 0) + risk_distribution.get('Very Unhealthy', 0) + 
                         risk_distribution.get('Hazardous', 0))
            
            with health_col2:
                # Calculate health impact score
                health_score = 100 - (forecasts['Forecasted_AQI'].mean() / 500) * 100
                st.metric("Health Score", f"{health_score:.1f}/100")
                
                # Calculate cumulative exposure
                total_exposure = forecasts['Forecasted_AQI'].sum()
                st.metric("Cumulative Exposure", f"{total_exposure:.0f}")
            
            with health_col3:
                # Sensitive group recommendations
                sensitive_days = len(forecasts[forecasts['Forecasted_AQI'] > 100])
                st.metric("Sensitive Group Risk Days", sensitive_days)
                
                # Calculate average daily risk
                avg_risk = forecasts['Forecasted_AQI'].mean()
                risk_level = "Low" if avg_risk < 50 else "Moderate" if avg_risk < 100 else "High"
                st.metric("Average Daily Risk", risk_level)
            
            # Detailed Health Recommendations by Category
            st.subheader("Category-Specific Health Guidelines")
            
            # Group forecasts by AQI category
            category_groups = forecasts.groupby('AQI_Category')
            
            for category, group in category_groups:
                with st.expander(f"{category} ({len(group)} days)"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Dates:**")
                        st.write(f"From: {group.index.min().strftime('%Y-%m-%d')}")
                        st.write(f"To: {group.index.max().strftime('%Y-%m-%d')}")
                        st.write(f"**AQI Range:**")
                        st.write(f"Min: {group['Forecasted_AQI'].min():.1f}")
                        st.write(f"Max: {group['Forecasted_AQI'].max():.1f}")
                        st.write(f"**Average AQI:** {group['Forecasted_AQI'].mean():.1f}")
                        
                        # Get specific health recommendations
                        sample_rec = group['Health_Recommendation'].iloc[0]
                        st.write(f"**Recommendation:** {sample_rec}")
                    
                    with col2:
                        # Risk level indicator
                        if 'Good' in category:
                            st.success("🟢 Low Risk")
                        elif 'Moderate' in category:
                            st.warning("🟡 Moderate Risk")
                        elif 'Unhealthy for Sensitive Groups' in category:
                            st.warning("🟠 High Risk for Sensitive Groups")
                        elif 'Unhealthy' in category:
                            st.error("🔴 High Risk for Everyone")
                        elif 'Very Unhealthy' in category:
                            st.error("🟣 Very High Risk")
                        else:
                            st.error("⚫ Hazardous")
                        
                        # Protection measures
                        if 'Good' in category:
                            st.write("**Protection:** None needed")
                        elif 'Moderate' in category:
                            st.write("**Protection:** Sensitive groups should limit prolonged outdoor exertion")
                        else:
                            st.write("**Protection:** Everyone should limit outdoor activities")
            
            # Health Impact Timeline
            st.subheader("Health Impact Timeline")
            
            # Create enhanced timeline chart
            fig = go.Figure()
            
            for category in forecasts['AQI_Category'].unique():
                category_data = forecasts[forecasts['AQI_Category'] == category]
                fig.add_trace(go.Scatter(
                    x=category_data.index,
                    y=category_data['Forecasted_AQI'],
                    mode='markers+lines',
                    name=category,
                    marker=dict(
                        color=category_data['AQI_Category'].apply(lambda x: get_aqi_category(100 if 'Good' in x else 200 if 'Moderate' in x else 300 if 'Unhealthy' in x else 400)[1]),
                        size=8,
                        line=dict(width=2)
                    ),
                    text=category_data['AQI_Category'],
                    hovertemplate='<b>%{text}</b><br>Date: %{x}<br>AQI: %{y:.1f}<extra></extra>'
                ))
            
            fig.update_layout(
                title="Air Quality Health Impact Timeline",
                xaxis_title="Date",
                yaxis_title="AQI",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Risk Periods Analysis
            st.subheader("Risk Periods Analysis")
            
            # Find all unhealthy periods
            unhealthy_periods = forecasts[forecasts['Forecasted_AQI'] > 100]
            
            if not unhealthy_periods.empty:
                st.warning("⚠️ Unhealthy air quality periods detected:")
                
                # Group consecutive unhealthy days
                unhealthy_periods['Date'] = unhealthy_periods.index
                unhealthy_periods = unhealthy_periods.sort_index()
                
                # Find consecutive periods
                periods = []
                current_period = []
                
                for i, (date, row) in enumerate(unhealthy_periods.iterrows()):
                    if i == 0:
                        current_period = [date]
                    else:
                        prev_date = unhealthy_periods.index[i-1]
                        if (date - prev_date).days == 1:
                            current_period.append(date)
                        else:
                            if current_period:
                                periods.append(current_period)
                            current_period = [date]
                
                if current_period:
                    periods.append(current_period)
                
                # Display risk periods
                for i, period in enumerate(periods, 1):
                    period_data = forecasts.loc[period]
                    max_aqi = period_data['Forecasted_AQI'].max()
                    avg_aqi = period_data['Forecasted_AQI'].mean()
                    
                    with st.expander(f"Risk Period {i}: {period[0].strftime('%Y-%m-%d')} to {period[-1].strftime('%Y-%m-%d')} ({len(period)} days)"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Max AQI", f"{max_aqi:.1f}")
                            st.metric("Avg AQI", f"{avg_aqi:.1f}")
                        
                        with col2:
                            # Determine dominant category
                            dominant_cat = period_data['AQI_Category'].mode().iloc[0]
                            st.metric("Dominant Category", dominant_cat)
                            
                            # Risk level
                            if max_aqi > 200:
                                st.metric("Risk Level", "Very High")
                            elif max_aqi > 150:
                                st.metric("Risk Level", "High")
                            else:
                                st.metric("Risk Level", "Moderate")
                        
                        with col3:
                            st.write("**Recommended Actions:**")
                            if max_aqi > 150:
                                st.write("• Avoid outdoor activities")
                                st.write("• Use air purifiers indoors")
                                st.write("• Wear N95 masks if going outside")
                            else:
                                st.write("• Limit prolonged outdoor exertion")
                                st.write("• Keep windows closed")
                                st.write("• Monitor symptoms")
                        
                        # Show daily breakdown
                        st.write("**Daily Breakdown:**")
                        daily_display = period_data[['Forecasted_AQI', 'AQI_Category', 'Health_Recommendation']].copy()
                        daily_display.columns = ['AQI', 'Category', 'Recommendation']
                        st.dataframe(daily_display, use_container_width=True)
            else:
                st.success("✅ No unhealthy air quality periods detected in the forecast!")
                st.info("All forecast days have AQI ≤ 100, which is generally safe for most people.")
            
            # Population Impact Assessment
            st.subheader("Population Impact Assessment")
            
            pop_col1, pop_col2, pop_col3 = st.columns(3)
            
            with pop_col1:
                # General population impact
                general_risk_days = len(forecasts[forecasts['Forecasted_AQI'] > 200])
                general_risk_pct = (general_risk_days / len(forecasts)) * 100
                st.metric("General Population Risk Days", general_risk_days)
                st.metric("General Population Risk %", f"{general_risk_pct:.1f}%")
            
            with pop_col2:
                # Sensitive groups impact
                sensitive_risk_days = len(forecasts[forecasts['Forecasted_AQI'] > 100])
                sensitive_risk_pct = (sensitive_risk_days / len(forecasts)) * 100
                st.metric("Sensitive Groups Risk Days", sensitive_risk_days)
                st.metric("Sensitive Groups Risk %", f"{sensitive_risk_pct:.1f}%")
            
            with pop_col3:
                # Overall health burden
                health_burden = forecasts['Forecasted_AQI'].sum() / len(forecasts)
                if health_burden < 50:
                    burden_level = "Low"
                    burden_color = "🟢"
                elif health_burden < 100:
                    burden_level = "Moderate"
                    burden_color = "🟡"
                else:
                    burden_level = "High"
                    burden_color = "🔴"
                
                st.metric("Average Health Burden", f"{health_burden:.1f}")
                st.metric("Burden Level", f"{burden_color} {burden_level}")
            
            # Actionable Recommendations Summary
            st.subheader("Actionable Recommendations Summary")
            
            # Generate overall recommendations based on forecast
            overall_avg_aqi = forecasts['Forecasted_AQI'].mean()
            max_forecast_aqi = forecasts['Forecasted_AQI'].max()
            
            recommendation_col1, recommendation_col2 = st.columns(2)
            
            with recommendation_col1:
                st.write("**General Population:**")
                if max_forecast_aqi <= 50:
                    st.success("✅ Enjoy outdoor activities normally")
                elif max_forecast_aqi <= 100:
                    st.info("ℹ️ Normal activities acceptable")
                elif max_forecast_aqi <= 150:
                    st.warning("⚠️ Limit prolonged outdoor exertion")
                else:
                    st.error("🚫 Avoid outdoor activities")
                
                st.write("**Sensitive Groups:**")
                if max_forecast_aqi <= 100:
                    st.info("ℹ️ Normal activities acceptable")
                elif max_forecast_aqi <= 150:
                    st.warning("⚠️ Reduce prolonged outdoor exertion")
                else:
                    st.error("🚫 Avoid all outdoor activities")
            
            with recommendation_col2:
                st.write("**Precautionary Measures:**")
                if overall_avg_aqi > 100:
                    st.write("• Keep windows closed")
                    st.write("• Use air purifiers")
                    st.write("• Monitor AQI regularly")
                    st.write("• Have rescue medication ready")
                else:
                    st.write("• Monitor air quality")
                    st.write("• Enjoy outdoor activities")
                    st.write("• Stay hydrated")
                    st.write("• Exercise normally")
                
                st.write("**When to Seek Medical Help:**")
                st.write("• Difficulty breathing")
                st.write("• Chest pain or tightness")
                st.write("• Persistent coughing")
                st.write("• Eye irritation")
                st.write("• Worsening asthma symptoms")
            
            # Health impact timeline
            st.subheader("Health Impact Timeline")
            
            # Create timeline chart
            fig = go.Figure()
            
            for category in forecasts['AQI_Category'].unique():
                category_data = forecasts[forecasts['AQI_Category'] == category]
                fig.add_trace(go.Scatter(
                    x=category_data.index,
                    y=category_data['Forecasted_AQI'],
                    mode='markers',
                    name=category,
                    marker=dict(
                        color=category_data['AQI_Category'].apply(lambda x: get_aqi_category(100 if 'Good' in x else 200 if 'Moderate' in x else 300 if 'Unhealthy' in x else 400)[1]),
                        size=8
                    ),
                    text=category_data['AQI_Category'],
                    hovertemplate='<b>%{text}</b><br>Date: %{x}<br>AQI: %{y:.1f}<extra></extra>'
                ))
            
            fig.update_layout(
                title="Air Quality Health Impact Timeline",
                xaxis_title="Date",
                yaxis_title="AQI",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Risk periods
            st.subheader("High Risk Periods")
            
            unhealthy_periods = forecasts[forecasts['Forecasted_AQI'] > 100]
            if not unhealthy_periods.empty:
                st.warning("Unhealthy air quality periods detected:")
                
                # Create more readable risk period cards
                for date, row in unhealthy_periods.iterrows():
                    cat, _, rec = get_aqi_category(row['Forecasted_AQI'])
                    
                    # Color coding for risk levels
                    risk_color = {
                        'Unhealthy for Sensitive Groups': '#ff7e00',
                        'Unhealthy': '#ff0000',
                        'Very Unhealthy': '#8f3f97',
                        'Hazardous': '#7e0023'
                    }.get(cat, '#ff0000')
                    
                    st.markdown(f"""
                    <div style="
                        background: {risk_color}10;
                        border-left: 4px solid {risk_color};
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        border: 1px solid {risk_color}30;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <strong style="color: {risk_color}; font-size: 1.1em;">
                                {date.strftime('%B %d, %Y')}
                            </strong>
                            <span style="
                                background: {risk_color};
                                color: white;
                                padding: 4px 12px;
                                border-radius: 15px;
                                font-size: 0.9em;
                                font-weight: bold;
                            ">AQI {row['Forecasted_AQI']:.0f}</span>
                        </div>
                        <div style="color: #666; font-size: 0.95em; margin-bottom: 5px;">
                            <strong>Category:</strong> {cat}
                        </div>
                        <div style="color: #555; line-height: 1.5;">
                            <strong>Recommendation:</strong> {rec}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No unhealthy air quality periods in the forecast")
            
            # Download results
            st.subheader("Download Results")
            
            # Prepare download data
            download_data = forecasts[['Forecasted_AQI', 'Lower_Bound', 'Upper_Bound']].copy()
            download_data.columns = ['Forecast AQI', 'Lower Bound', 'Upper Bound']
            download_data['Health Category'] = forecasts['AQI_Category']
            download_data['Recommendation'] = forecasts['Health_Recommendation']
            
            csv = download_data.to_csv(index=True)
            b64 = base64.b64encode(csv.encode()).decode()
            
            href = f'<a href="data:file/csv;base64,{b64}" download="air_quality_forecast_{datetime.now().strftime("%Y%m%d")}.csv">Download Forecast Results (CSV)</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
