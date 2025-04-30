import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

def process_data(data, operations=None):
    """
    Process data with specified operations.
    
    Args:
        data (pd.DataFrame): Input data
        operations (list): List of operations to perform
        
    Returns:
        pd.DataFrame: Processed data
    """
    # If no operations specified, return original data
    if operations is None or not operations:
        return data
    
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    # Apply operations
    for operation in operations:
        if operation["type"] == "filter":
            df = filter_data(df, operation["start_date"], operation["end_date"])
        elif operation["type"] == "resample":
            df = resample_data(df, operation["rule"])
        elif operation["type"] == "rolling":
            df = apply_rolling(df, operation["window"], operation["function"])
        elif operation["type"] == "diff":
            df = calculate_diff(df, operation["periods"])
        elif operation["type"] == "pct_change":
            df = calculate_pct_change(df, operation["periods"])
        elif operation["type"] == "normalization":
            df = normalize_data(df, operation["method"])
        elif operation["type"] == "fill_missing":
            df = fill_missing_values(df, operation["method"])
        elif operation["type"] == "outlier_removal":
            df = remove_outliers(df, operation["method"], operation["threshold"])
    
    return df

def filter_data(data, start_date, end_date):
    """
    Filter data by date range.
    
    Args:
        data (pd.DataFrame): Input data
        start_date (str or datetime): Start date
        end_date (str or datetime): End date
        
    Returns:
        pd.DataFrame: Filtered data
    """
    # Convert string dates to datetime if needed
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    
    # Ensure start_date and end_date are pandas Timestamp objects
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    
    # Filter data
    filtered_data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
    
    return filtered_data

def resample_data(data, rule):
    """
    Resample time series data.
    
    Args:
        data (pd.DataFrame): Input data
        rule (str): Resampling rule (e.g., 'D', 'W', 'M')
        
    Returns:
        pd.DataFrame: Resampled data
    """
    # Set date as index
    df = data.copy()
    df = df.set_index('date')
    
    # Resample numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    resampled = df[numeric_cols].resample(rule).mean()
    
    # Reset index
    resampled = resampled.reset_index()
    
    return resampled

def apply_rolling(data, window, function='mean'):
    """
    Apply rolling window function to data.
    
    Args:
        data (pd.DataFrame): Input data
        window (int): Window size
        function (str): Function to apply (mean, median, sum, min, max)
        
    Returns:
        pd.DataFrame: Data with rolling window applied
    """
    df = data.copy()
    
    # Apply rolling function to value column
    if 'value' in df.columns:
        if function == 'mean':
            df['rolling_value'] = df['value'].rolling(window=window).mean()
        elif function == 'median':
            df['rolling_value'] = df['value'].rolling(window=window).median()
        elif function == 'sum':
            df['rolling_value'] = df['value'].rolling(window=window).sum()
        elif function == 'min':
            df['rolling_value'] = df['value'].rolling(window=window).min()
        elif function == 'max':
            df['rolling_value'] = df['value'].rolling(window=window).max()
    
    # Drop NaN values from rolling calculation
    df = df.dropna(subset=['rolling_value'])
    
    return df

def calculate_diff(data, periods=1):
    """
    Calculate difference between consecutive values.
    
    Args:
        data (pd.DataFrame): Input data
        periods (int): Periods to shift
        
    Returns:
        pd.DataFrame: Data with difference calculated
    """
    df = data.copy()
    
    # Calculate difference for value column
    if 'value' in df.columns:
        df['diff'] = df['value'].diff(periods=periods)
    
    # Drop NaN values from diff calculation
    df = df.dropna(subset=['diff'])
    
    return df

def calculate_pct_change(data, periods=1):
    """
    Calculate percentage change between consecutive values.
    
    Args:
        data (pd.DataFrame): Input data
        periods (int): Periods to shift
        
    Returns:
        pd.DataFrame: Data with percentage change calculated
    """
    df = data.copy()
    
    # Calculate percentage change for value column
    if 'value' in df.columns:
        df['pct_change'] = df['value'].pct_change(periods=periods) * 100
    
    # Drop NaN values from pct_change calculation
    df = df.dropna(subset=['pct_change'])
    
    return df

def normalize_data(data, method='minmax'):
    """
    Normalize data using specified method.
    
    Args:
        data (pd.DataFrame): Input data
        method (str): Normalization method (minmax, zscore)
        
    Returns:
        pd.DataFrame: Normalized data
    """
    df = data.copy()
    
    # Normalize value column
    if 'value' in df.columns:
        if method == 'minmax':
            min_val = df['value'].min()
            max_val = df['value'].max()
            df['normalized_value'] = (df['value'] - min_val) / (max_val - min_val)
        elif method == 'zscore':
            mean = df['value'].mean()
            std = df['value'].std()
            df['normalized_value'] = (df['value'] - mean) / std
    
    return df

def fill_missing_values(data, method='ffill'):
    """
    Fill missing values in data.
    
    Args:
        data (pd.DataFrame): Input data
        method (str): Filling method (ffill, bfill, interpolate)
        
    Returns:
        pd.DataFrame: Data with missing values filled
    """
    df = data.copy()
    
    # Apply method to entire dataframe
    if method == 'ffill':
        df = df.ffill()
    elif method == 'bfill':
        df = df.bfill()
    elif method == 'interpolate':
        df = df.interpolate()
    
    return df

def remove_outliers(data, method='zscore', threshold=3):
    """
    Remove outliers from data.
    
    Args:
        data (pd.DataFrame): Input data
        method (str): Method for outlier detection (zscore, iqr)
        threshold (float): Threshold for outlier detection
        
    Returns:
        pd.DataFrame: Data with outliers removed
    """
    df = data.copy()
    
    if 'value' in df.columns:
        if method == 'zscore':
            mean = df['value'].mean()
            std = df['value'].std()
            z_scores = abs((df['value'] - mean) / std)
            df = df[z_scores <= threshold]
        elif method == 'iqr':
            q1 = df['value'].quantile(0.25)
            q3 = df['value'].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            df = df[(df['value'] >= lower_bound) & (df['value'] <= upper_bound)]
    
    return df
