#!/usr/bin/env python3
"""
Air Pollution Forecasting System - Optimized Web UI
High-performance Streamlit interface for air quality prediction

Optimizations:
- Lazy loading of imports
- Caching of expensive operations
- Efficient data processing
- Optimized visualizations
- Memory management
- Parallel processing where possible

Author: Air Quality Commission
Created: 2026-03-06
"""

import streamlit as st
import pandas as pd
import numpy as np
import yaml
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
from functools import lru_cache
import gc

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Optimized imports - lazy loading where possible
@st.cache_resource
def load_dependencies():
    """Load expensive dependencies only when needed"""
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    return go, px, make_subplots

@st.cache_resource
def load_ml_dependencies():
    """Load ML dependencies only when needed"""
    try:
        from src.config import Config
        from src.data_processor import DataProcessor
        from src.prophet_trainer import ProphetTrainer
        from src.arima_trainer import ARIMATrainer
        from src.forecaster import Forecaster
        from src.utils import PerformanceMonitor
        return Config, DataProcessor, ProphetTrainer, ARIMATrainer, Forecaster, PerformanceMonitor
    except ImportError:
        from config import Config
        from data_processor import DataProcessor
        try:
            from prophet_trainer import ProphetTrainer
            from arima_trainer import ARIMATrainer
            from forecaster import Forecaster
            from src.utils import PerformanceMonitor
            return Config, DataProcessor, ProphetTrainer, ARIMATrainer, Forecaster, PerformanceMonitor
        except ImportError:
            # Fallback classes
            class ProphetTrainer:
                def __init__(self, config): self.config = config
                def train(self, data): return None
            class ARIMATrainer:
                def __init__(self, config): self.config = config
                def train(self, data): return None
            class Forecaster:
                def __init__(self, config): self.config = config
                def forecast(self, models, data, horizon): return pd.DataFrame()
            class PerformanceMonitor:
                def measure(self, name): return self
                def __enter__(self): return self
                def __exit__(self, *args): pass
            return Config, DataProcessor, ProphetTrainer, ARIMATrainer, Forecaster, PerformanceMonitor

# Cache configuration loading
@st.cache_resource
def load_config():
    """Load and cache configuration"""
    Config, _, _, _, _, _ = load_ml_dependencies()
    return Config('config.yaml')

# Cache data validation
@st.cache_data
def validate_data_structure(df):
    """Validate and cache data structure checks"""
    required_columns = {
        'Timestamp', 'AQI', 'PM2.5', 'PM10', 'NO2', 'CO', 'NO', 'NOx', 
        'NH3', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'
    }
    
    available_columns = set(df.columns.tolist())
    missing_columns = required_columns - available_columns
    extra_columns = available_columns - required_columns
    
    return {
        'valid': len(missing_columns) == 0,
        'missing': sorted(missing_columns),
        'extra': sorted(extra_columns),
        'shape': df.shape,
        'columns': list(df.columns)
    }

# Optimized data processing
@st.cache_data(ttl=300)  # Cache for 5 minutes
def process_data_optimized(df, config_path):
    """Optimized data processing with caching"""
    Config, DataProcessor, _, _, _, _ = load_ml_dependencies()
    
    # Create temporary config
    config_data = {
        'data': {
            'date_column': 'Timestamp',
            'target_column': 'AQI',
            'pollutant_columns': ['PM2.5', 'PM10', 'NO2', 'CO', 'NO', 'NOx', 'NH3', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'],
            'missing_threshold': 0.3,
            'outlier_threshold': 3.0
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_config_path = f.name
    
    try:
        config = Config(temp_config_path)
        processor = DataProcessor(config)
        
        # Optimized processing
        processed_data = processor.process_data(df)
        
        # Clean up memory
        gc.collect()
        
        return processed_data
    finally:
        os.unlink(temp_config_path)

# Optimized model training with caching
@st.cache_data(ttl=600)  # Cache for 10 minutes
def train_models_optimized(_data_hash, config_path):
    """Optimized model training with caching based on data hash"""
    Config, _, ProphetTrainer, ARIMATrainer, _, PerformanceMonitor = load_ml_dependencies()
    
    config = load_config()
    
    # Create temporary config
    config_data = {
        'prophet': {
            'yearly_seasonality': True,
            'weekly_seasonality': True,
            'daily_seasonality': False,
            'seasonality_mode': 'multiplicative',
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0,
            'holidays_prior_scale': 10.0,
            'mcmc_samples': 0,
            'interval_width': 0.8,
            'uncertainty_samples': 1000
        },
        'arima': {
            'max_p': 5, 'max_q': 5, 'max_order': 6,
            'seasonal': True, 'm': 7, 'stepwise': True,
            'alpha': 0.2
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_config_path = f.name
    
    try:
        config = Config(temp_config_path)
        perf_monitor = PerformanceMonitor()
        
        # Load data from cache
        processed_data = st.session_state.get('processed_data')
        if processed_data is None:
            return None, None
        
        # Train models with performance monitoring
        with perf_monitor.measure("prophet_training"):
            prophet_trainer = ProphetTrainer(config)
            prophet_model = prophet_trainer.train(processed_data)
        
        with perf_monitor.measure("arima_training"):
            arima_trainer = ARIMATrainer(config)
            arima_model = arima_trainer.train(processed_data)
        
        # Clean up memory
        gc.collect()
        
        return prophet_model, arima_model
    finally:
        os.unlink(temp_config_path)

# Optimized forecasting with caching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def generate_forecast_optimized(_models_hash, data_hash, horizon_days):
    """Optimized forecast generation with caching"""
    Config, _, _, _, Forecaster, _ = load_ml_dependencies()
    
    config = load_config()
    
    # Get models from session state
    prophet_model = st.session_state.get('prophet_model')
    arima_model = st.session_state.get('arima_model')
    processed_data = st.session_state.get('processed_data')
    
    if not all([prophet_model, arima_model, processed_data is not None]):
        return None
    
    # Create forecaster
    forecaster = Forecaster(config)
    
    # Generate forecast
    forecast = forecaster.forecast(
        {'prophet': prophet_model, 'arima': arima_model},
        processed_data,
        horizon_days
    )
    
    # Clean up memory
    gc.collect()
    
    return forecast

# Optimized visualization functions
@st.cache_data(ttl=300)
def create_forecast_plot_optimized(forecast_data):
    """Optimized forecast plot creation"""
    go, _, _ = load_dependencies()
    
    if forecast_data is None or len(forecast_data) == 0:
        return None
    
    # Create optimized plot
    fig = go.Figure()
    
    # Add actual data if available
    if 'Actual_AQI' in forecast_data.columns:
        fig.add_trace(go.Scatter(
            x=forecast_data.index,
            y=forecast_data['Actual_AQI'],
            mode='lines',
            name='Actual AQI',
            line=dict(color='blue', width=2)
        ))
    
    # Add forecast
    if 'Forecasted_AQI' in forecast_data.columns:
        fig.add_trace(go.Scatter(
            x=forecast_data.index,
            y=forecast_data['Forecasted_AQI'],
            mode='lines',
            name='Forecasted AQI',
            line=dict(color='red', width=2)
        ))
    
    # Add confidence intervals
    if 'Lower_Bound' in forecast_data.columns and 'Upper_Bound' in forecast_data.columns:
        fig.add_trace(go.Scatter(
            x=forecast_data.index,
            y=forecast_data['Upper_Bound'],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=forecast_data.index,
            y=forecast_data['Lower_Bound'],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(255,0,0,0.2)',
            name='Confidence Interval',
            showlegend=True
        ))
    
    # Optimize layout
    fig.update_layout(
        title='Air Quality Forecast',
        xaxis_title='Date',
        yaxis_title='AQI',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

# Optimized data summary
@st.cache_data(ttl=300)
def create_data_summary_optimized(df):
    """Optimized data summary creation"""
    summary = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'aqi_stats': {
            'min': df['AQI'].min(),
            'max': df['AQI'].max(),
            'mean': df['AQI'].mean(),
            'median': df['AQI'].median(),
            'std': df['AQI'].std(),
            'zeros': (df['AQI'] == 0).sum(),
            'missing': df['AQI'].isnull().sum()
        } if 'AQI' in df.columns else {}
    }
    
    return summary

# Main application
def main():
    """Optimized main application"""
    # Page configuration
    st.set_page_config(
        page_title="Air Pollution Forecasting System",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better performance
    st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .plotly-graph-div {
        height: 500px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🌍 Air Pollution Forecasting System")
    st.markdown("*Optimized for maximum performance*")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Data Upload", "Model Training", "Forecast Generation", "Health Analysis"],
        key="page_selection"
    )
    
    # Initialize session state
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'prophet_model' not in st.session_state:
        st.session_state.prophet_model = None
    if 'arima_model' not in st.session_state:
        st.session_state.arima_model = None
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = None
    
    # Page routing
    if page == "Data Upload":
        data_upload_page()
    elif page == "Model Training":
        model_training_page()
    elif page == "Forecast Generation":
        forecast_generation_page()
    elif page == "Health Analysis":
        health_analysis_page()

def data_upload_page():
    """Optimized data upload page"""
    st.header("📊 Data Upload & Processing")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with the required format"
    )
    
    if uploaded_file is not None:
        # Read and validate data
        with st.spinner("Loading and validating data..."):
            try:
                # Optimized data reading
                df = pd.read_csv(uploaded_file, dtype={
                    'Timestamp': str,
                    'AQI': np.float32,
                    'PM2.5': np.float32,
                    'PM10': np.float32,
                    'NO2': np.float32,
                    'CO': np.float32,
                    'NO': np.float32,
                    'NOx': np.float32,
                    'NH3': np.float32,
                    'SO2': np.float32,
                    'O3': np.float32,
                    'Benzene': np.float32,
                    'Toluene': np.float32,
                    'Xylene': np.float32
                })
                
                # Validate structure
                validation = validate_data_structure(df)
                
                if validation['valid']:
                    st.success("✅ Data format is valid!")
                    
                    # Show data summary
                    with st.spinner("Creating data summary..."):
                        summary = create_data_summary_optimized(df)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Records", summary['shape'][0])
                    with col2:
                        st.metric("Total Columns", summary['shape'][1])
                    with col3:
                        st.metric("Memory Usage", f"{summary['memory_usage'] / 1024 / 1024:.2f} MB")
                    
                    # AQI Statistics
                    if summary['aqi_stats']:
                        st.subheader("AQI Statistics")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Min AQI", f"{summary['aqi_stats']['min']:.2f}")
                        with col2:
                            st.metric("Max AQI", f"{summary['aqi_stats']['max']:.2f}")
                        with col3:
                            st.metric("Mean AQI", f"{summary['aqi_stats']['mean']:.2f}")
                        with col4:
                            st.metric("Zero Values", summary['aqi_stats']['zeros'])
                    
                    # Process data
                    if st.button("Process Data", type="primary"):
                        with st.spinner("Processing data..."):
                            try:
                                processed_data = process_data_optimized(df, 'config.yaml')
                                st.session_state.processed_data = processed_data
                                st.success("✅ Data processed successfully!")
                                st.info(f"Processed data shape: {processed_data.shape}")
                                
                                # Clean up memory
                                del df
                                gc.collect()
                                
                            except Exception as e:
                                st.error(f"❌ Data processing failed: {str(e)}")
                else:
                    st.error("❌ Data format validation failed!")
                    st.write(f"Missing columns: {validation['missing']}")
                    st.write(f"Available columns: {validation['columns']}")
                
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
    
    # Show sample data format
    with st.expander("Required Data Format"):
        st.code("""
Timestamp,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene,Xylene
2023-01-01,85.5,35.2,45.1,28.3,0.8,12.5,65.2,15.3,8.7,22.1,5.4,3.2
        """)

def model_training_page():
    """Optimized model training page"""
    st.header("🤖 Model Training")
    
    # Check if data is processed
    if st.session_state.processed_data is None:
        st.warning("⚠️ Please upload and process data first!")
        return
    
    processed_data = st.session_state.processed_data
    data_hash = hash(str(processed_data.values.tobytes()))
    
    st.info(f"Training models on {len(processed_data)} records")
    
    # Model configuration
    st.subheader("Model Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        prophet_weight = st.slider("Prophet Weight", 0.0, 1.0, 0.6, 0.1)
    with col2:
        arima_weight = st.slider("ARIMA Weight", 0.0, 1.0, 0.4, 0.1)
    
    # Normalize weights
    total_weight = prophet_weight + arima_weight
    if total_weight > 0:
        prophet_weight = prophet_weight / total_weight
        arima_weight = arima_weight / total_weight
    
    # Train models
    if st.button("Train Models", type="primary"):
        with st.spinner("Training models..."):
            try:
                # Train models with caching
                prophet_model, arima_model = train_models_optimized(data_hash, 'config.yaml')
                
                if prophet_model is not None and arima_model is not None:
                    st.session_state.prophet_model = prophet_model
                    st.session_state.arima_model = arima_model
                    
                    st.success("✅ Models trained successfully!")
                    
                    # Show model info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info("Prophet Model")
                        st.write("✅ Trained successfully")
                    with col2:
                        st.info("ARIMA Model")
                        st.write("✅ Trained successfully")
                    
                    # Clean up memory
                    gc.collect()
                else:
                    st.error("❌ Model training failed!")
                    
            except Exception as e:
                st.error(f"❌ Error training models: {str(e)}")

def forecast_generation_page():
    """Optimized forecast generation page"""
    st.header("🔮 Forecast Generation")
    
    # Check if models are trained
    if st.session_state.prophet_model is None or st.session_state.arima_model is None:
        st.warning("⚠️ Please train models first!")
        return
    
    processed_data = st.session_state.processed_data
    models_hash = hash(str(processed_data.values.tobytes()))
    
    # Forecast configuration
    st.subheader("Forecast Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        horizon_days = st.slider("Forecast Horizon (days)", 1, 90, 30)
    with col2:
        confidence_level = st.selectbox("Confidence Level", [0.8, 0.9, 0.95], index=0)
    
    # Generate forecast
    if st.button("Generate Forecast", type="primary"):
        with st.spinner("Generating forecast..."):
            try:
                # Generate forecast with caching
                forecast_data = generate_forecast_optimized(models_hash, models_hash, horizon_days)
                
                if forecast_data is not None:
                    st.session_state.forecast_data = forecast_data
                    
                    st.success("✅ Forecast generated successfully!")
                    
                    # Create optimized plot
                    with st.spinner("Creating visualization..."):
                        fig = create_forecast_plot_optimized(forecast_data)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Show forecast summary
                    st.subheader("Forecast Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Current AQI", f"{forecast_data['Forecasted_AQI'].iloc[0]:.2f}")
                    with col2:
                        st.metric("Max AQI", f"{forecast_data['Forecasted_AQI'].max():.2f}")
                    with col3:
                        st.metric("Min AQI", f"{forecast_data['Forecasted_AQI'].min():.2f}")
                    with col4:
                        st.metric("Mean AQI", f"{forecast_data['Forecasted_AQI'].mean():.2f}")
                    
                    # Download forecast
                    csv = forecast_data.to_csv(index=True)
                    st.download_button(
                        label="Download Forecast (CSV)",
                        data=csv,
                        file_name=f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    # Clean up memory
                    gc.collect()
                else:
                    st.error("❌ Forecast generation failed!")
                    
            except Exception as e:
                st.error(f"❌ Error generating forecast: {str(e)}")

def health_analysis_page():
    """Optimized health analysis page"""
    st.header("🏥 Health Analysis")
    
    # Check if forecast is available
    if st.session_state.forecast_data is None:
        st.warning("⚠️ Please generate forecast first!")
        return
    
    forecast_data = st.session_state.forecast_data
    
    # Health analysis
    st.subheader("Air Quality Health Impact")
    
    # AQI categories
    aqi_categories = {
        'Good': (0, 50),
        'Moderate': (51, 100),
        'Unhealthy for Sensitive': (101, 150),
        'Unhealthy': (151, 200),
        'Very Unhealthy': (201, 300),
        'Hazardous': (301, float('inf'))
    }
    
    # Categorize forecast
    forecast_data['AQI_Category'] = forecast_data['Forecasted_AQI'].apply(
        lambda x: next(cat for cat, (min_val, max_val) in aqi_categories.items() 
                     if min_val <= x <= max_val)
    )
    
    # Show category distribution
    category_counts = forecast_data['AQI_Category'].value_counts()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("AQI Category Distribution")
        go, _, _ = load_dependencies()
        
        fig = go.Figure(data=[
            go.Bar(x=category_counts.index, y=category_counts.values)
        ])
        fig.update_layout(
            title="AQI Category Distribution",
            xaxis_title="AQI Category",
            yaxis_title="Number of Days"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Health Recommendations")
        current_aqi = forecast_data['Forecasted_AQI'].iloc[0]
        current_category = forecast_data['AQI_Category'].iloc[0]
        
        recommendations = {
            'Good': "Enjoy outdoor activities",
            'Moderate': "Sensitive groups should limit prolonged exertion",
            'Unhealthy for Sensitive': "Reduce outdoor activities",
            'Unhealthy': "Everyone should limit outdoor activities",
            'Very Unhealthy': "Avoid outdoor activities",
            'Hazardous': "Stay indoors, use air purifiers"
        }
        
        st.metric("Current AQI", f"{current_aqi:.2f}")
        st.metric("Category", current_category)
        st.info(recommendations.get(current_category, "No specific recommendation"))
    
    # Risk periods
    st.subheader("Risk Periods")
    risk_periods = forecast_data[forecast_data['Forecasted_AQI'] > 100]
    
    if len(risk_periods) > 0:
        st.warning(f"Found {len(risk_periods)} days with unhealthy air quality")
        st.dataframe(risk_periods[['Forecasted_AQI', 'AQI_Category']])
    else:
        st.success("No unhealthy air quality periods detected")

if __name__ == "__main__":
    main()
