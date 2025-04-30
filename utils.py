import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO
import json

def format_large_number(num):
    """
    Format large numbers for display.
    
    Args:
        num (int): Number to format
        
    Returns:
        str: Formatted number
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)

def export_data(data, format='csv'):
    """
    Export data to specified format and provide download link.
    
    Args:
        data (pd.DataFrame): Data to export
        format (str): Export format (csv, excel, json)
    """
    if data is None or len(data) == 0:
        st.error("No data to export")
        return
    
    # Prepare file for download
    if format == 'csv':
        file_data = data.to_csv(index=False)
        file_name = "trend_data.csv"
        mime_type = "text/csv"
    elif format == 'excel':
        buffer = BytesIO()
        data.to_excel(buffer, index=False)
        buffer.seek(0)
        file_data = buffer.read()
        file_name = "trend_data.xlsx"
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == 'json':
        file_data = data.to_json(orient='records')
        file_name = "trend_data.json"
        mime_type = "application/json"
    else:
        st.error(f"Unsupported format: {format}")
        return
    
    # Create download link
    b64 = base64.b64encode(file_data.encode()).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{file_name}">Download {format.upper()} file</a>'
    st.markdown(href, unsafe_allow_html=True)

def apply_theme(dark_mode=False):
    """
    Apply theme settings based on mode.
    
    Args:
        dark_mode (bool): Whether to use dark mode
    """
    if dark_mode:
        # Dark mode settings
        st.markdown("""
        <style>
        .reportview-container {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .sidebar .sidebar-content {
            background-color: #262730;
            color: #FFFFFF;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light mode settings (default)
        pass

def generate_color_palette(n_colors, theme='default'):
    """
    Generate a color palette for visualizations.
    
    Args:
        n_colors (int): Number of colors to generate
        theme (str): Color theme to use
        
    Returns:
        list: List of color hex codes
    """
    import colorsys
    
    if theme == 'default':
        # Default color palette
        base_palette = [
            '#1f77b4',  # Blue
            '#ff7f0e',  # Orange
            '#2ca02c',  # Green
            '#d62728',  # Red
            '#9467bd',  # Purple
            '#8c564b',  # Brown
            '#e377c2',  # Pink
            '#7f7f7f',  # Gray
            '#bcbd22',  # Yellow-green
            '#17becf'   # Cyan
        ]
        
        # If we need more colors than in the base palette, generate them
        if n_colors <= len(base_palette):
            return base_palette[:n_colors]
        else:
            # Generate additional colors using HSV color space
            additional_colors = []
            for i in range(n_colors - len(base_palette)):
                hue = i / (n_colors - len(base_palette))
                r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
                hex_color = "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))
                additional_colors.append(hex_color)
            
            return base_palette + additional_colors
    
    elif theme == 'pastel':
        # Pastel color palette
        base_palette = [
            '#c7e9b4',  # Light green
            '#41b6c4',  # Light blue
            '#1d91c0',  # Medium blue
            '#225ea8',  # Dark blue
            '#fdae61',  # Light orange
            '#f46d43',  # Orange
            '#d53e4f',  # Red
            '#9e0142',  # Dark red
            '#c994c7',  # Light purple
            '#df65b0'   # Pink
        ]
        
        if n_colors <= len(base_palette):
            return base_palette[:n_colors]
        else:
            additional_colors = []
            for i in range(n_colors - len(base_palette)):
                hue = i / (n_colors - len(base_palette))
                r, g, b = colorsys.hsv_to_rgb(hue, 0.4, 0.9)
                hex_color = "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))
                additional_colors.append(hex_color)
            
            return base_palette + additional_colors
    
    elif theme == 'viridis':
        # Viridis color palette (colorblind-friendly)
        colors = []
        for i in range(n_colors):
            t = i / max(1, n_colors - 1)
            
            # These values approximate the viridis colormap
            r = np.interp(t, [0, 0.4, 0.8, 1], [0.267, 0.275, 0.470, 0.993])
            g = np.interp(t, [0, 0.4, 0.8, 1], [0.004, 0.376, 0.759, 0.905])
            b = np.interp(t, [0, 0.4, 0.8, 1], [0.329, 0.431, 0.376, 0.145])
            
            hex_color = "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))
            colors.append(hex_color)
        
        return colors
    
    else:
        # Default to 'default' theme
        return generate_color_palette(n_colors, 'default')

def create_date_features(df, date_col='date'):
    """
    Create date-based features from a date column.
    
    Args:
        df (pd.DataFrame): Input dataframe
        date_col (str): Name of date column
        
    Returns:
        pd.DataFrame: Dataframe with date features added
    """
    df = df.copy()
    
    # Convert to datetime if not already
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Extract date components
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['day'] = df[date_col].dt.day
    df['day_of_week'] = df[date_col].dt.dayofweek
    df['day_of_year'] = df[date_col].dt.dayofyear
    df['week_of_year'] = df[date_col].dt.isocalendar().week
    df['quarter'] = df[date_col].dt.quarter
    df['is_weekend'] = df[date_col].dt.dayofweek >= 5
    
    return df

def detect_seasonal_pattern(data, value_col='value'):
    """
    Detect seasonal patterns in time series data.
    
    Args:
        data (pd.DataFrame): Time series data
        value_col (str): Column name for values
        
    Returns:
        dict: Dictionary containing detected patterns
    """
    # Check if we have enough data
    if len(data) < 14:
        return {
            'has_seasonality': False,
            'period': None,
            'strength': None,
            'message': "Not enough data to detect seasonality"
        }
    
    # Get values
    values = data[value_col].values
    
    # Calculate autocorrelation
    from statsmodels.tsa.stattools import acf
    lag_acf = acf(values, nlags=min(len(values) // 2, 365), fft=True)
    
    # Find peaks in autocorrelation
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(lag_acf[1:], height=0.1)  # Skip lag 0
    peaks = peaks + 1  # Adjust indexes (as we skipped lag 0)
    
    if len(peaks) == 0:
        return {
            'has_seasonality': False,
            'period': None,
            'strength': None,
            'message': "No significant seasonality detected"
        }
    
    # Get strongest peak
    strongest_peak = peaks[np.argmax(lag_acf[peaks])]
    strength = lag_acf[strongest_peak]
    
    # Look for common patterns
    patterns = {
        7: 'Weekly',
        14: 'Bi-weekly',
        30: 'Monthly',
        90: 'Quarterly',
        365: 'Yearly'
    }
    
    # Find closest common pattern
    closest_pattern = min(patterns.keys(), key=lambda x: abs(x - strongest_peak))
    
    # Check if the peak is close enough to a common pattern
    if abs(closest_pattern - strongest_peak) <= closest_pattern * 0.2:  # Within 20% of pattern period
        period_name = patterns[closest_pattern]
        period = closest_pattern
    else:
        period_name = f"Custom ({strongest_peak} days)"
        period = strongest_peak
    
    return {
        'has_seasonality': True,
        'period': period,
        'period_name': period_name,
        'strength': strength,
        'message': f"Detected {period_name} seasonality with strength {strength:.2f}"
    }

def calculate_trend_strength(data, value_col='value'):
    """
    Calculate the strength of trend in time series data.
    
    Args:
        data (pd.DataFrame): Time series data
        value_col (str): Column name for values
        
    Returns:
        float: Trend strength (0-1)
    """
    # Check if we have enough data
    if len(data) < 10:
        return 0
    
    # Get values
    values = data[value_col].values
    
    # Create time index
    time_idx = np.arange(len(values))
    
    # Fit linear regression
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(time_idx.reshape(-1, 1), values)
    
    # Get model predictions
    predictions = model.predict(time_idx.reshape(-1, 1))
    
    # Calculate R-squared
    ss_total = np.sum((values - np.mean(values)) ** 2)
    ss_residual = np.sum((values - predictions) ** 2)
    
    if ss_total == 0:
        return 0
    
    r_squared = 1 - (ss_residual / ss_total)
    
    return max(0, min(1, r_squared))
