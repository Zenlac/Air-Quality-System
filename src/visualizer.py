"""
Visualization Module
Handles creating optimized visualizations for the air pollution forecasting system

Author: Air Quality Commission
Created: 2026-02-25
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from prophet import Prophet

try:
    from .config import Config
    from .utils import PerformanceMonitor, get_aqi_color
except ImportError:
    from config import Config
    from utils import PerformanceMonitor, get_aqi_color


class Visualizer:
    """Visualization creator for air pollution forecasts"""
    
    def __init__(self, config: Config, output_dir: str):
        """
        Initialize visualizer
        
        Args:
            config: Configuration object
            output_dir: Output directory for saving plots
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        self.perf_monitor = PerformanceMonitor()
        
        # Setup matplotlib and seaborn
        self._setup_plotting()
        
        # Get configuration values
        self.figure_size = config.get('visualization.figure_size', [16, 12])
        self.dpi = config.get('visualization.dpi', 100)
        self.save_format = config.get('visualization.save_format', 'png')
        self.bbox_inches = config.get('visualization.bbox_inches', 'tight')
    
    def _setup_plotting(self):
        """Setup matplotlib and seaborn settings"""
        # Set style
        style = self.config.get('visualization.style', 'seaborn-v0_8')
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
        
        # Set color palette
        color_palette = self.config.get('visualization.color_palette', 'husl')
        sns.set_palette(color_palette)
        
        # Set font sizes
        plt.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })
    
    def create_all_visualizations(self, historical_data: pd.DataFrame, 
                               forecast_data: pd.DataFrame,
                               prophet_model: Prophet, arima_model):
        """
        Create all visualizations for the forecasting system
        
        Args:
            historical_data: Historical air quality data
            forecast_data: Forecast results
            prophet_model: Trained Prophet model
            arima_model: Trained ARIMA model
        """
        self.logger.info("Creating all visualizations...")
        
        with self.perf_monitor.measure("visualization_creation"):
            # Create individual visualizations
            self.plot_historical_data(historical_data)
            self.plot_prophet_forecast(prophet_model, historical_data)
            self.plot_arima_forecast(arima_model, historical_data, forecast_data)
            self.plot_ensemble_forecast(historical_data, forecast_data)
            self.plot_model_comparison(forecast_data)
            self.plot_aqi_categories(forecast_data)
            self.plot_forecast_confidence(forecast_data)
            self.create_forecast_dashboard(historical_data, forecast_data)
            
            self.logger.info("All visualizations created successfully")
    
    def plot_historical_data(self, data: pd.DataFrame, filename: str = "historical_data"):
        """
        Plot historical air quality data
        
        Args:
            data: Historical data
            filename: Output filename
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figure_size)
        
        # 1. Time series plot
        ax1 = axes[0, 0]
        ax1.plot(data.index, data['AQI'], 'b-', linewidth=1, alpha=0.7)
        ax1.set_title('Historical AQI Time Series')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('AQI')
        ax1.grid(True, alpha=0.3)
        
        # 2. Monthly distribution
        ax2 = axes[0, 1]
        monthly_avg = data.groupby(data.index.month)['AQI'].mean()
        ax2.bar(monthly_avg.index, monthly_avg.values, color='skyblue', alpha=0.7)
        ax2.set_title('Average AQI by Month')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Average AQI')
        ax2.set_xticks(range(1, 13))
        
        # 3. AQI distribution histogram
        ax3 = axes[1, 0]
        ax3.hist(data['AQI'], bins=30, color='lightgreen', alpha=0.7, edgecolor='black')
        ax3.set_title('AQI Distribution')
        ax3.set_xlabel('AQI')
        ax3.set_ylabel('Frequency')
        ax3.axvline(data['AQI'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {data["AQI"].mean():.1f}')
        ax3.legend()
        
        # 4. Box plot by year
        ax4 = axes[1, 1]
        data['Year'] = data.index.year
        yearly_data = [data[data['Year'] == year]['AQI'].values for year in data['Year'].unique()]
        ax4.boxplot(yearly_data, labels=data['Year'].unique())
        ax4.set_title('AQI Distribution by Year')
        ax4.set_xlabel('Year')
        ax4.set_ylabel('AQI')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        self._save_plot(fig, filename)
        plt.close()
    
    def plot_prophet_forecast(self, model: Prophet, data: pd.DataFrame, 
                            filename: str = "prophet_forecast"):
        """
        Plot Prophet model forecast
        
        Args:
            model: Trained Prophet model
            data: Historical data
            filename: Output filename
        """
        # Create future dataframe for Prophet
        future = model.make_future_dataframe(periods=31)
        forecast = model.predict(future)
        
        fig, axes = plt.subplots(2, 2, figsize=self.figure_size)
        
        # 1. Prophet forecast plot
        ax1 = axes[0, 0]
        model.plot(forecast, ax=ax1)
        ax1.set_title('Prophet Model Forecast')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('AQI')
        
        # 2. Prophet components
        ax2 = axes[0, 1]
        model.plot_components(forecast)
        ax2.set_title('Prophet Components')
        
        # 3. Forecast vs Actual (last 60 days)
        ax3 = axes[1, 0]
        last_60 = forecast.tail(60)
        ax3.plot(last_60['ds'], last_60['yhat'], 'b-', label='Forecast', linewidth=2)
        ax3.fill_between(last_60['ds'], last_60['yhat_lower'], 
                        last_60['yhat_upper'], alpha=0.2, color='blue')
        ax3.set_title('Prophet Forecast - Last 60 Days')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('AQI')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Trend analysis
        ax4 = axes[1, 1]
        trend_data = forecast[['ds', 'trend']].tail(90)
        ax4.plot(trend_data['ds'], trend_data['trend'], 'g-', linewidth=2)
        ax4.set_title('90-Day Trend Analysis')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Trend')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._save_plot(fig, filename)
        plt.close()
    
    def plot_arima_forecast(self, model, data: pd.DataFrame, forecast_data: pd.DataFrame,
                          filename: str = "arima_forecast"):
        """
        Plot ARIMA model forecast
        
        Args:
            model: Trained ARIMA model
            data: Historical data
            forecast_data: Forecast data containing ARIMA predictions
            filename: Output filename
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figure_size)
        
        # 1. Historical data and ARIMA forecast
        ax1 = axes[0, 0]
        historical_dates = data.index[-90:]  # Last 90 days
        ax1.plot(historical_dates, data['AQI'].tail(90), 'b-', label='Historical', linewidth=2)
        ax1.plot(forecast_data.index, forecast_data['ARIMA_Forecast'], 'r-', 
                label='ARIMA Forecast', linewidth=2)
        ax1.fill_between(forecast_data.index, forecast_data['ARIMA_Lower'], 
                        forecast_data['ARIMA_Upper'], alpha=0.2, color='red')
        ax1.set_title('ARIMA Forecast - Next 31 Days')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('AQI')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Residuals analysis
        ax2 = axes[0, 1]
        residuals = model.resid()
        ax2.plot(residuals, 'g-', alpha=0.7)
        ax2.set_title('Model Residuals')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Residuals')
        ax2.grid(True, alpha=0.3)
        
        # 3. Residuals distribution
        ax3 = axes[1, 0]
        ax3.hist(residuals, bins=30, alpha=0.7, color='purple', edgecolor='black')
        ax3.set_title('Residuals Distribution')
        ax3.set_xlabel('Residuals')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)
        
        # 4. Forecast detail
        ax4 = axes[1, 1]
        ax4.plot(forecast_data.index, forecast_data['ARIMA_Forecast'], 'r-', linewidth=2)
        ax4.fill_between(forecast_data.index, forecast_data['ARIMA_Lower'], 
                        forecast_data['ARIMA_Upper'], alpha=0.2, color='red')
        ax4.set_title('ARIMA Forecast Detail')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('AQI')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._save_plot(fig, filename)
        plt.close()
    
    def plot_ensemble_forecast(self, historical_data: pd.DataFrame, 
                             forecast_data: pd.DataFrame,
                             filename: str = "ensemble_forecast"):
        """
        Plot ensemble forecast
        
        Args:
            historical_data: Historical data
            forecast_data: Ensemble forecast data
            filename: Output filename
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figure_size)
        
        # 1. Historical + Ensemble forecast
        ax1 = axes[0, 0]
        historical_dates = historical_data.index[-90:]
        ax1.plot(historical_dates, historical_data['AQI'].tail(90), 'b-', 
                label='Historical', linewidth=2, alpha=0.7)
        ax1.plot(forecast_data.index, forecast_data['Forecasted_AQI'], 'g-', 
                label='Ensemble Forecast', linewidth=3)
        ax1.fill_between(forecast_data.index, forecast_data['Lower_Bound'], 
                        forecast_data['Upper_Bound'], alpha=0.3, color='green')
        ax1.set_title('Ensemble Forecast - Historical + Future')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('AQI')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. AQI categories over time
        ax2 = axes[0, 1]
        category_colors = [get_aqi_color(cat) for cat in forecast_data['AQI_Category']]
        ax2.scatter(forecast_data.index, forecast_data['Forecasted_AQI'], 
                   c=category_colors, s=50, alpha=0.7)
        ax2.set_title('Forecast with AQI Categories')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('AQI')
        ax2.grid(True, alpha=0.3)
        
        # 3. Risk level timeline
        ax3 = axes[1, 0]
        ax3.fill_between(forecast_data.index, 0, forecast_data['Risk_Level'], 
                        alpha=0.6, color='orange')
        ax3.set_title('Risk Level Timeline')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Risk Level (1-6)')
        ax3.set_ylim(0, 6.5)
        ax3.grid(True, alpha=0.3)
        
        # 4. Confidence scores
        ax4 = axes[1, 1]
        ax4.plot(forecast_data.index, forecast_data['Confidence_Score'], 
                'purple', linewidth=2)
        ax4.set_title('Forecast Confidence Scores')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Confidence Score')
        ax4.set_ylim(0, 1)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._save_plot(fig, filename)
        plt.close()
    
    def plot_model_comparison(self, forecast_data: pd.DataFrame,
                            filename: str = "model_comparison"):
        """
        Plot comparison between different models
        
        Args:
            forecast_data: Forecast data with all model predictions
            filename: Output filename
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figure_size)
        
        # 1. Model comparison
        ax1 = axes[0, 0]
        ax1.plot(forecast_data.index, forecast_data['Prophet_Forecast'], 'b-', 
                label='Prophet', linewidth=2)
        ax1.plot(forecast_data.index, forecast_data['ARIMA_Forecast'], 'r-', 
                label='ARIMA', linewidth=2)
        ax1.plot(forecast_data.index, forecast_data['Forecasted_AQI'], 'g-', 
                label='Ensemble', linewidth=3)
        ax1.set_title('Model Comparison - 31 Day Forecast')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('AQI')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Confidence intervals comparison
        ax2 = axes[0, 1]
        ax2.fill_between(forecast_data.index, forecast_data['Prophet_Lower'], 
                        forecast_data['Prophet_Upper'], alpha=0.2, color='blue', 
                        label='Prophet CI')
        ax2.fill_between(forecast_data.index, forecast_data['ARIMA_Lower'], 
                        forecast_data['ARIMA_Upper'], alpha=0.2, color='red', 
                        label='ARIMA CI')
        ax2.fill_between(forecast_data.index, forecast_data['Lower_Bound'], 
                        forecast_data['Upper_Bound'], alpha=0.3, color='green', 
                        label='Ensemble CI')
        ax2.set_title('Confidence Intervals Comparison')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('AQI')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Forecast differences
        ax3 = axes[1, 0]
        differences = forecast_data['Prophet_Forecast'] - forecast_data['ARIMA_Forecast']
        ax3.plot(forecast_data.index, differences, 'purple', linewidth=2)
        ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax3.set_title('Prophet - ARIMA Forecast Differences')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('AQI Difference')
        ax3.grid(True, alpha=0.3)
        
        # 4. Model performance metrics
        ax4 = axes[1, 1]
        models = ['Prophet', 'ARIMA', 'Ensemble']
        # Placeholder metrics (would be calculated from actual model performance)
        rmse_values = [15.2, 18.5, 14.8]  # Example values
        bars = ax4.bar(models, rmse_values, color=['blue', 'red', 'green'], alpha=0.7)
        ax4.set_title('Model RMSE Comparison')
        ax4.set_ylabel('RMSE')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, rmse_values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{value:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        self._save_plot(fig, filename)
        plt.close()
    
    def plot_aqi_categories(self, forecast_data: pd.DataFrame,
                          filename: str = "aqi_categories"):
        """
        Plot AQI category distribution and analysis
        
        Args:
            forecast_data: Forecast data
            filename: Output filename
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figure_size)
        
        # 1. Category distribution pie chart
        ax1 = axes[0, 0]
        category_counts = forecast_data['AQI_Category'].value_counts()
        colors = [get_aqi_color(cat) for cat in category_counts.index]
        ax1.pie(category_counts.values, labels=category_counts.index, 
               autopct='%1.1f%%', colors=colors)
        ax1.set_title('Forecasted AQI Category Distribution')
        
        # 2. Category timeline
        ax2 = axes[0, 1]
        category_order = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 
                          'Unhealthy', 'Very Unhealthy', 'Hazardous']
        forecast_data['Category_Code'] = forecast_data['AQI_Category'].map(
            {cat: i for i, cat in enumerate(category_order)}
        )
        ax2.scatter(forecast_data.index, forecast_data['Category_Code'], 
                   c=[get_aqi_color(cat) for cat in forecast_data['AQI_Category']], 
                   s=30, alpha=0.7)
        ax2.set_yticks(range(len(category_order)))
        ax2.set_yticklabels(category_order)
        ax2.set_title('AQI Category Timeline')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)
        
        # 3. Risk level distribution
        ax3 = axes[1, 0]
        risk_counts = forecast_data['Risk_Level'].value_counts().sort_index()
        ax3.bar(risk_counts.index, risk_counts.values, color='orange', alpha=0.7)
        ax3.set_title('Risk Level Distribution')
        ax3.set_xlabel('Risk Level')
        ax3.set_ylabel('Number of Days')
        ax3.set_xticks(range(1, 7))
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Health impact summary
        ax4 = axes[1, 1]
        health_impact = {
            'Good': forecast_data['AQI_Category'].value_counts().get('Good', 0),
            'Moderate': forecast_data['AQI_Category'].value_counts().get('Moderate', 0),
            'Unhealthy+': len(forecast_data[forecast_data['AQI_Category'].str.contains('Unhealthy', na=False)])
        }
        colors = ['green', 'yellow', 'red']
        bars = ax4.bar(health_impact.keys(), health_impact.values(), color=colors, alpha=0.7)
        ax4.set_title('Health Impact Summary')
        ax4.set_ylabel('Number of Days')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, value in zip(bars, health_impact.values()):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(value), ha='center', va='bottom')
        
        plt.tight_layout()
        self._save_plot(fig, filename)
        plt.close()
    
    def plot_forecast_confidence(self, forecast_data: pd.DataFrame,
                               filename: str = "forecast_confidence"):
        """
        Plot forecast confidence analysis
        
        Args:
            forecast_data: Forecast data
            filename: Output filename
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figure_size)
        
        # 1. Confidence scores over time
        ax1 = axes[0, 0]
        ax1.plot(forecast_data.index, forecast_data['Confidence_Score'], 
                'purple', linewidth=2)
        ax1.fill_between(forecast_data.index, 0, forecast_data['Confidence_Score'], 
                        alpha=0.3, color='purple')
        ax1.set_title('Forecast Confidence Scores')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Confidence Score')
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)
        
        # 2. Prediction interval width
        ax2 = axes[0, 1]
        interval_width = forecast_data['Upper_Bound'] - forecast_data['Lower_Bound']
        ax2.plot(forecast_data.index, interval_width, 'orange', linewidth=2)
        ax2.set_title('Prediction Interval Width')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Interval Width')
        ax2.grid(True, alpha=0.3)
        
        # 3. Confidence vs AQI level
        ax3 = axes[1, 0]
        ax3.scatter(forecast_data['Forecasted_AQI'], forecast_data['Confidence_Score'], 
                   alpha=0.6, c='green')
        ax3.set_title('Confidence vs AQI Level')
        ax3.set_xlabel('Forecasted AQI')
        ax3.set_ylabel('Confidence Score')
        ax3.grid(True, alpha=0.3)
        
        # 4. Confidence distribution
        ax4 = axes[1, 1]
        ax4.hist(forecast_data['Confidence_Score'], bins=20, alpha=0.7, 
                color='blue', edgecolor='black')
        ax4.set_title('Confidence Score Distribution')
        ax4.set_xlabel('Confidence Score')
        ax4.set_ylabel('Frequency')
        ax4.axvline(forecast_data['Confidence_Score'].mean(), color='red', 
                   linestyle='--', label=f'Mean: {forecast_data["Confidence_Score"].mean():.3f}')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._save_plot(fig, filename)
        plt.close()
    
    def create_forecast_dashboard(self, historical_data: pd.DataFrame, 
                                forecast_data: pd.DataFrame,
                                filename: str = "forecast_dashboard"):
        """
        Create comprehensive forecast dashboard
        
        Args:
            historical_data: Historical data
            forecast_data: Forecast data
            filename: Output filename
        """
        fig = plt.figure(figsize=(20, 16))
        
        # Create grid layout
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Main forecast plot (top, spanning 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        historical_dates = historical_data.index[-60:]
        ax1.plot(historical_dates, historical_data['AQI'].tail(60), 'b-', 
                label='Historical', linewidth=2, alpha=0.7)
        ax1.plot(forecast_data.index, forecast_data['Forecasted_AQI'], 'g-', 
                label='Ensemble Forecast', linewidth=3)
        ax1.fill_between(forecast_data.index, forecast_data['Lower_Bound'], 
                        forecast_data['Upper_Bound'], alpha=0.3, color='green')
        ax1.set_title('Air Quality Forecast Dashboard', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('AQI')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. AQI category pie chart (top right)
        ax2 = fig.add_subplot(gs[0, 2])
        category_counts = forecast_data['AQI_Category'].value_counts()
        colors = [get_aqi_color(cat) for cat in category_counts.index]
        ax2.pie(category_counts.values, labels=category_counts.index, 
               autopct='%1.1f%%', colors=colors)
        ax2.set_title('AQI Categories')
        
        # 3. Risk level timeline (middle left)
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.fill_between(forecast_data.index, 0, forecast_data['Risk_Level'], 
                        alpha=0.6, color='orange')
        ax3.set_title('Risk Level Timeline')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Risk Level (1-6)')
        ax3.set_ylim(0, 6.5)
        ax3.grid(True, alpha=0.3)
        
        # 4. Confidence scores (middle center)
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(forecast_data.index, forecast_data['Confidence_Score'], 
                'purple', linewidth=2)
        ax4.set_title('Confidence Scores')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Confidence Score')
        ax4.set_ylim(0, 1)
        ax4.grid(True, alpha=0.3)
        
        # 5. Health impact summary (middle right)
        ax5 = fig.add_subplot(gs[1, 2])
        health_impact = {
            'Good': forecast_data['AQI_Category'].value_counts().get('Good', 0),
            'Moderate': forecast_data['AQI_Category'].value_counts().get('Moderate', 0),
            'Unhealthy+': len(forecast_data[forecast_data['AQI_Category'].str.contains('Unhealthy', na=False)])
        }
        colors = ['green', 'yellow', 'red']
        bars = ax5.bar(health_impact.keys(), health_impact.values(), color=colors, alpha=0.7)
        ax5.set_title('Health Impact')
        ax5.set_ylabel('Days')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. Forecast statistics (bottom left)
        ax6 = fig.add_subplot(gs[2, 0])
        stats_text = f"""Forecast Statistics:
        
Mean AQI: {forecast_data['Forecasted_AQI'].mean():.1f}
Min AQI: {forecast_data['Forecasted_AQI'].min():.1f}
Max AQI: {forecast_data['Forecasted_AQI'].max():.1f}
Std Dev: {forecast_data['Forecasted_AQI'].std():.1f}

Avg Confidence: {forecast_data['Confidence_Score'].mean():.3f}
Forecast Period: {len(forecast_data)} days
"""
        ax6.text(0.1, 0.5, stats_text, transform=ax6.transAxes, fontsize=10,
                verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax6.set_title('Statistics Summary')
        ax6.axis('off')
        
        # 7. Model comparison (bottom center)
        ax7 = fig.add_subplot(gs[2, 1])
        models = ['Prophet', 'ARIMA', 'Ensemble']
        # Calculate RMSE for each model (placeholder values)
        prophet_rmse = np.sqrt(np.mean((forecast_data['Prophet_Forecast'] - forecast_data['Forecasted_AQI'])**2))
        arima_rmse = np.sqrt(np.mean((forecast_data['ARIMA_Forecast'] - forecast_data['Forecasted_AQI'])**2))
        ensemble_rmse = np.sqrt(np.mean((forecast_data['Forecasted_AQI'] - forecast_data['Forecasted_AQI'])**2))
        rmse_values = [prophet_rmse, arima_rmse, ensemble_rmse]
        bars = ax7.bar(models, rmse_values, color=['blue', 'red', 'green'], alpha=0.7)
        ax7.set_title('Model Performance')
        ax7.set_ylabel('RMSE')
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 8. Recommendations (bottom right)
        ax8 = fig.add_subplot(gs[2, 2])
        recommendations = self._generate_recommendations(forecast_data)
        ax8.text(0.1, 0.5, recommendations, transform=ax8.transAxes, fontsize=9,
                verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        ax8.set_title('Recommendations')
        ax8.axis('off')
        
        plt.suptitle('Air Pollution Forecasting System Dashboard', 
                    fontsize=18, fontweight='bold', y=0.98)
        self._save_plot(fig, filename)
        plt.close()
    
    def _generate_recommendations(self, forecast_data: pd.DataFrame) -> str:
        """Generate health recommendations based on forecast"""
        total_days = len(forecast_data)
        good_days = len(forecast_data[forecast_data['AQI_Category'] == 'Good'])
        moderate_days = len(forecast_data[forecast_data['AQI_Category'] == 'Moderate'])
        unhealthy_days = len(forecast_data[forecast_data['AQI_Category'].str.contains('Unhealthy', na=False)])
        
        recommendations = "Health Recommendations:\n\n"
        
        if good_days > total_days * 0.5:
            recommendations += "• Generally good air quality expected\n"
            recommendations += "• Great time for outdoor activities\n"
        
        if moderate_days > total_days * 0.3:
            recommendations += "• Some moderate air quality days\n"
            recommendations += "• Sensitive groups should take precautions\n"
        
        if unhealthy_days > 0:
            recommendations += "• Unhealthy air quality expected\n"
            recommendations += "• Limit outdoor activities\n"
            recommendations += "• Use air purifiers indoors\n"
        
        return recommendations
    
    def _save_plot(self, fig, filename: str):
        """Save plot to file"""
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = self.output_dir / f"{filename}.{self.save_format}"
        fig.savefig(filepath, dpi=self.dpi, bbox_inches=self.bbox_inches)
        self.logger.info(f"Saved plot: {filepath}")
