#!/usr/bin/env python3
"""
Convert EMB-CEPMOo1-year.csv to match the required format
"""

import pandas as pd

def convert_emb_data(input_file='EMB-CEPMOo1-year.csv', output_file='EMB_converted.csv'):
    """
    Convert EMB data to match the required format
    
    Args:
        input_file: Path to EMB data file
        output_file: Path for converted output file
    """
    print(f"Loading EMB data from: {input_file}")
    
    # Load the EMB data
    df = pd.read_csv(input_file)
    print(f"Original shape: {df.shape}")
    print(f"Original columns: {list(df.columns)}")
    
    # Convert Date to Timestamp format
    df['Timestamp'] = pd.to_datetime(df['Date'])
    
    # Calculate AQI if it's empty (using PM2.5 and PM10)
    if df['AQI'].isna().all():
        print("AQI column is empty, calculating from pollutant concentrations...")
        
        def calculate_aqi(pm25, pm10):
            """Simple AQI calculation based on PM2.5 and PM10"""
            # Use the higher AQI from PM2.5 or PM10
            aqi_pm25 = max(0, min(500, pm25 * 2.1))  # Rough conversion
            aqi_pm10 = max(0, min(500, pm10 * 1.2))   # Rough conversion
            return max(aqi_pm25, aqi_pm10)
        
        df['AQI'] = df.apply(lambda row: calculate_aqi(row['PM2.5'], row['PM10']), axis=1)
    
    # Select and reorder columns to match required format
    required_columns = [
        'Timestamp', 'AQI', 'PM2.5', 'PM10', 'NO2', 'CO', 'NO', 'NOx', 
        'NH3', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'
    ]
    
    # Create new DataFrame with required columns
    converted_df = df[required_columns].copy()
    
    # Remove rows with missing AQI values
    converted_df = converted_df.dropna(subset=['AQI'])
    
    # Sort by timestamp
    converted_df = converted_df.sort_values('Timestamp')
    
    print(f"Converted shape: {converted_df.shape}")
    print(f"Converted columns: {list(converted_df.columns)}")
    print(f"AQI range: {converted_df['AQI'].min():.2f} - {converted_df['AQI'].max():.2f}")
    
    # Save converted data
    converted_df.to_csv(output_file, index=False)
    print(f"Converted data saved to: {output_file}")
    
    return converted_df

if __name__ == "__main__":
    # Convert the EMB data
    converted_data = convert_emb_data()
    
    print("\nFirst few rows of converted data:")
    print(converted_data.head())
    
    print("\nConversion completed successfully!")
    print("You can now use the converted file with:")
    print(f"python main.py --data EMB_converted.csv --output outputs --days 31")
