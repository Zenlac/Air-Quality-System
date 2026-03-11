# Strict Data Format Requirements

## Overview
The Air Pollution Forecasting System now **only accepts data files that exactly match the format of `sample_air_quality_data.csv`**. This ensures consistency and reliability in model training and forecasting.

## Required Data Format

### File Structure
- **File type**: CSV (Comma-Separated Values)
- **Encoding**: UTF-8
- **Header row**: Required (first row contains column names)

### Required Columns (Exact Names and Order)

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `Timestamp` | DateTime | Date and time of measurement | `2023-01-01` |
| `AQI` | Numeric | Air Quality Index value | `57.45` |
| `PM2.5` | Numeric | PM2.5 concentration (μg/m³) | `22.37` |
| `PM10` | Numeric | PM10 concentration (μg/m³) | `35.82` |
| `NO2` | Numeric | Nitrogen dioxide concentration (μg/m³) | `18.67` |
| `CO` | Numeric | Carbon monoxide concentration (mg/m³) | `1.99` |
| `NO` | Numeric | Nitric oxide concentration (μg/m³) | `33.90` |
| `NOx` | Numeric | Nitrogen oxides concentration (μg/m³) | `46.16` |
| `NH3` | Numeric | Ammonia concentration (μg/m³) | `5.03` |
| `SO2` | Numeric | Sulfur dioxide concentration (μg/m³) | `11.31` |
| `O3` | Numeric | Ozone concentration (μg/m³) | `13.51` |
| `Benzene` | Numeric | Benzene concentration (μg/m³) | `3.49` |
| `Toluene` | Numeric | Toluene concentration (μg/m³) | `1.86` |
| `Xylene` | Numeric | Xylene concentration (μg/m³) | `4.65` |

### Data Requirements

#### Timestamp Column
- **Format**: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`
- **Timezone**: Not required (system assumes local time)
- **Frequency**: Regular intervals (daily, hourly, etc.)
- **Sorting**: Data will be automatically sorted by timestamp

#### AQI Column
- **Required**: Must contain valid numeric values
- **Range**: Typically 0-500 (US EPA standard)
- **Empty values**: Not allowed - AQI column must have values

#### Pollutant Columns
- **Data type**: Numeric (float or integer)
- **Missing values**: Allowed (system will fill using forward/backward fill)
- **Units**: As specified in table above

### Validation Rules

#### Strict Column Validation
- ✅ **All 14 required columns must be present**
- ✅ **Column names must match exactly (case-sensitive)**
- ❌ **Extra columns will generate warnings but won't cause failure**
- ❌ **Missing columns will cause immediate failure**

#### Data Quality Validation
- **Timestamp**: Must be valid datetime format
- **AQI**: Cannot be completely empty
- **Minimum rows**: 30 rows recommended for reliable forecasting
- **Data types**: Numeric columns must contain valid numbers

### Example Valid Data File

```csv
Timestamp,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene,Xylene
2023-01-01,57.45,22.37,35.82,18.67,1.99,33.90,46.16,5.03,11.31,13.51,3.49,1.86,4.65
2023-01-02,56.26,38.55,47.76,7.82,4.73,7.92,10.39,13.49,3.58,70.02,1.43,7.29,1.84
2023-01-03,70.50,21.49,55.92,23.09,3.39,31.10,10.54,9.97,12.47,39.07,1.03,3.29,5.99
```

### Common Format Mistakes (Will Be Rejected)

#### ❌ Incorrect Column Names
```csv
Date,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene,Xylene  # "Date" instead of "Timestamp"
timestamp,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene,Xylene  # lowercase "timestamp"
```

#### ❌ Missing Required Columns
```csv
Timestamp,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene  # Missing "Xylene"
```

#### ❌ Extra Columns (Will Generate Warning)
```csv
Timestamp,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene,Xylene,City,Station  # Extra columns
```

#### ❌ Empty AQI Column
```csv
Timestamp,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene,Xylene
2023-01-01,,22.37,35.82,18.67,1.99,33.90,46.16,5.03,11.31,13.51,3.49,1.86,4.65  # Empty AQI
```

### Error Messages

When invalid data is provided, the system will show specific error messages:

#### Missing Columns Error
```
Data format validation failed. Missing required columns: ['Timestamp']
Required columns: ['AQI', 'Benzene', 'CO', 'NH3', 'NO', 'NO2', 'NOx', 'O3', 'PM10', 'PM2.5', 'SO2', 'Timestamp', 'Toluene', 'Xylene']
Available columns: ['AQI', 'AQI_Bucket', 'Benzene', 'CO', 'City', 'Date', 'NH3', 'NO', 'NO2', 'NOx', 'O3', 'PM10', 'PM2.5', 'SO2', 'Toluene', 'Xylene']

Please ensure your data file matches the format of sample_air_quality_data.csv
```

#### Empty AQI Error
```
AQI column cannot be empty. Please provide valid AQI values.
```

#### Invalid Timestamp Error
```
Timestamp column must contain valid datetime values.
```

### How to Prepare Your Data

#### Step 1: Check Column Names
Ensure your CSV file has exactly these 14 columns in the header:
```
Timestamp,AQI,PM2.5,PM10,NO2,CO,NO,NOx,NH3,SO2,O3,Benzene,Toluene,Xylene
```

#### Step 2: Validate Data Types
- Timestamp: Valid dates/times
- AQI: Numeric values (not empty)
- Pollutants: Numeric values (can be empty)

#### Step 3: Test Your File
Use this command to test your data file:
```bash
python main.py --data your_file.csv --output test_output --days 7
```

### Reference File
Use `sample_air_quality_data.csv` as the reference format. This file is located in the root directory and demonstrates the exact format required.

### Benefits of Strict Format

1. **Consistency**: All models trained on standardized data
2. **Reliability**: Predictable behavior and results
3. **Debugging**: Easier to identify and fix issues
4. **Performance**: Optimized for specific data structure
5. **Maintenance**: Simplified codebase and documentation

### Migration from Previous Versions

If you were using the previous flexible format:
1. **Check your data files** against the required format
2. **Rename columns** if necessary (e.g., "Date" → "Timestamp")
3. **Ensure AQI values** are present and valid
4. **Remove extra columns** or accept warnings
5. **Test your files** with the new validation system

### Support

For help with data format issues:
1. Check your file against `sample_air_quality_data.csv`
2. Review the error messages carefully
3. Ensure all 14 required columns are present
4. Validate that AQI column has numeric values
