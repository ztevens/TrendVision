import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def forecast_trend(data, method='prophet', periods=30):
    """
    Forecast trend based on historical data.
    
    Args:
        data (pd.DataFrame): Historical data
        method (str): Forecasting method (prophet, arima, exponential_smoothing, linear_regression)
        periods (int): Number of periods to forecast
        
    Returns:
        pd.DataFrame: Dataframe with forecast values
    """
    # Check if data contains required columns
    if 'date' not in data.columns or 'value' not in data.columns:
        st.error("Data must contain 'date' and 'value' columns for forecasting")
        return None
    
    # Sort data by date
    df = data.sort_values('date').copy()
    
    # Ensure date column is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Select forecasting method
    if method == 'prophet':
        forecast_data = forecast_with_prophet(df, periods)
    elif method == 'arima':
        forecast_data = forecast_with_arima(df, periods)
    elif method == 'exponential_smoothing':
        forecast_data = forecast_with_exponential_smoothing(df, periods)
    elif method == 'linear_regression':
        forecast_data = forecast_with_linear_regression(df, periods)
    else:
        st.error(f"Unknown forecasting method: {method}")
        return None
    
    return forecast_data

def forecast_with_prophet(df, periods):
    """
    Forecast using Facebook Prophet.
    
    Args:
        df (pd.DataFrame): Historical data
        periods (int): Number of periods to forecast
        
    Returns:
        pd.DataFrame: Dataframe with forecast values
    """
    # Try to import Prophet
    try:
        from prophet import Prophet
    except ImportError:
        st.warning("Prophet is not installed. Using Exponential Smoothing instead.")
        return forecast_with_exponential_smoothing(df, periods)
    
    # Prepare data for Prophet
    prophet_df = df[['date', 'value']].rename(columns={'date': 'ds', 'value': 'y'})
    
    # Create and fit model
    model = Prophet(yearly_seasonality=True, daily_seasonality=False, weekly_seasonality=True)
    model.fit(prophet_df)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=periods)
    
    # Make forecast
    forecast = model.predict(future)
    
    # Prepare result dataframe
    result = pd.DataFrame({
        'date': forecast['ds'],
        'forecast': forecast['yhat'],
        'lower': forecast['yhat_lower'],
        'upper': forecast['yhat_upper']
    })
    
    # Filter to only include future dates
    last_date = df['date'].max()
    result = result[result['date'] > last_date]
    
    return result

def forecast_with_arima(df, periods):
    """
    Forecast using ARIMA model.
    
    Args:
        df (pd.DataFrame): Historical data
        periods (int): Number of periods to forecast
        
    Returns:
        pd.DataFrame: Dataframe with forecast values
    """
    # Prepare data for ARIMA
    # Get only the value column
    values = df['value'].values
    
    try:
        # Fit ARIMA model
        model = ARIMA(values, order=(5, 1, 0))
        model_fit = model.fit()
        
        # Make forecast
        forecast = model_fit.forecast(steps=periods)
        
        # Calculate forecast error (for confidence intervals)
        residuals = model_fit.resid
        error_std = np.std(residuals)
        
        # Create future dates
        last_date = df['date'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods)
        
        # Prepare result dataframe
        result = pd.DataFrame({
            'date': future_dates,
            'forecast': forecast,
            'lower': forecast - 1.96 * error_std,
            'upper': forecast + 1.96 * error_std
        })
        
        return result
    except Exception as e:
        st.error(f"Error in ARIMA forecasting: {str(e)}")
        # Fallback to simple moving average
        return forecast_with_moving_average(df, periods)

def forecast_with_exponential_smoothing(df, periods):
    """
    Forecast using Exponential Smoothing.
    
    Args:
        df (pd.DataFrame): Historical data
        periods (int): Number of periods to forecast
        
    Returns:
        pd.DataFrame: Dataframe with forecast values
    """
    # Prepare data for Exponential Smoothing
    # Get only the value column
    values = df['value'].values
    
    try:
        # Determine if data has trend and seasonality
        # Check for trend
        x = np.arange(len(values))
        trend_model = LinearRegression()
        trend_model.fit(x.reshape(-1, 1), values)
        has_trend = abs(trend_model.coef_[0]) > 0.01
        
        # Check for seasonality (simplistic approach)
        if len(values) >= 14:  # Need at least 2 weeks of data
            # Calculate autocorrelation
            autocorr = np.correlate(values, values, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Find peaks in autocorrelation
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(autocorr)
            
            # If we find peaks, assume seasonality
            has_seasonality = len(peaks) > 0
            
            # Estimate seasonal period
            if has_seasonality and len(peaks) > 0:
                seasonal_period = peaks[0]
                # Limit to common periods (7 for weekly, 30 for monthly)
                if abs(seasonal_period - 7) < 2:
                    seasonal_period = 7
                elif abs(seasonal_period - 30) < 5:
                    seasonal_period = 30
                else:
                    # Default to weekly
                    seasonal_period = 7
            else:
                seasonal_period = 7  # Default to weekly
        else:
            has_seasonality = False
            seasonal_period = 7  # Default to weekly
        
        # Fit Exponential Smoothing model
        if has_seasonality:
            model = ExponentialSmoothing(
                values,
                trend='add' if has_trend else None,
                seasonal='add',
                seasonal_periods=seasonal_period
            )
        else:
            model = ExponentialSmoothing(
                values,
                trend='add' if has_trend else None,
                seasonal=None
            )
        
        model_fit = model.fit()
        
        # Make forecast
        forecast = model_fit.forecast(periods)
        
        # Calculate forecast error (for confidence intervals)
        residuals = model_fit.resid
        error_std = np.std(residuals)
        
        # Create future dates
        last_date = df['date'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods)
        
        # Prepare result dataframe
        result = pd.DataFrame({
            'date': future_dates,
            'forecast': forecast,
            'lower': forecast - 1.96 * error_std,
            'upper': forecast + 1.96 * error_std
        })
        
        return result
    except Exception as e:
        st.error(f"Error in Exponential Smoothing forecasting: {str(e)}")
        # Fallback to simple moving average
        return forecast_with_moving_average(df, periods)

def forecast_with_linear_regression(df, periods):
    """
    Forecast using Linear Regression with time-based features.
    
    Args:
        df (pd.DataFrame): Historical data
        periods (int): Number of periods to forecast
        
    Returns:
        pd.DataFrame: Dataframe with forecast values
    """
    # Prepare data for Linear Regression
    # Create time-based features
    df = df.copy()
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    
    # Create time index feature
    df['time_idx'] = (df['date'] - df['date'].min()).dt.days
    
    # Create lag features
    for lag in [1, 7, 14, 30]:
        if len(df) > lag:
            df[f'lag_{lag}'] = df['value'].shift(lag)
    
    # Create rolling mean features
    for window in [7, 14, 30]:
        if len(df) > window:
            df[f'rolling_mean_{window}'] = df['value'].rolling(window=window).mean()
    
    # Drop rows with NaN (due to lag features)
    df = df.dropna()
    
    if len(df) < 10:
        # Not enough data for linear regression
        return forecast_with_moving_average(df, periods)
    
    # Prepare features and target
    features = [
        'day_of_week', 'day_of_month', 'month', 'time_idx',
        'lag_1', 'lag_7', 'lag_14', 'lag_30',
        'rolling_mean_7', 'rolling_mean_14', 'rolling_mean_30'
    ]
    
    # Keep only features that exist in dataframe
    features = [f for f in features if f in df.columns]
    
    X = df[features].values
    y = df['value'].values
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit linear regression model
    model = LinearRegression()
    model.fit(X_scaled, y)
    
    # Create future dates
    last_date = df['date'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods)
    
    # Create dataframe for future prediction
    future_df = pd.DataFrame({'date': future_dates})
    
    # Create time-based features for future dates
    future_df['day_of_week'] = future_df['date'].dt.dayofweek
    future_df['day_of_month'] = future_df['date'].dt.day
    future_df['month'] = future_df['date'].dt.month
    future_df['year'] = future_df['date'].dt.year
    future_df['time_idx'] = (future_df['date'] - df['date'].min()).dt.days
    
    # Initialize lag features with the most recent values
    latest_values = df['value'].iloc[-30:].values  # Get last 30 values
    
    # Make predictions iteratively
    all_predictions = []
    prediction_intervals = []
    
    for i in range(periods):
        # Create lag features for current prediction
        if 'lag_1' in features:
            if i == 0:
                future_df.loc[i, 'lag_1'] = df['value'].iloc[-1]
            else:
                future_df.loc[i, 'lag_1'] = all_predictions[i-1]
        
        if 'lag_7' in features:
            if i < 7:
                future_df.loc[i, 'lag_7'] = df['value'].iloc[-7+i]
            else:
                future_df.loc[i, 'lag_7'] = all_predictions[i-7]
        
        if 'lag_14' in features:
            if i < 14:
                future_df.loc[i, 'lag_14'] = df['value'].iloc[-14+i]
            else:
                future_df.loc[i, 'lag_14'] = all_predictions[i-14]
        
        if 'lag_30' in features:
            if i < 30:
                future_df.loc[i, 'lag_30'] = df['value'].iloc[-30+i]
            else:
                future_df.loc[i, 'lag_30'] = all_predictions[i-30]
        
        # Create rolling mean features
        if 'rolling_mean_7' in features:
            if i < 7:
                # Use combination of historical and predicted values
                values_to_use = np.concatenate([latest_values[-(7-i):], all_predictions[:i]])
            else:
                values_to_use = all_predictions[i-7:i]
            future_df.loc[i, 'rolling_mean_7'] = np.mean(values_to_use)
        
        if 'rolling_mean_14' in features:
            if i < 14:
                values_to_use = np.concatenate([latest_values[-(14-i):], all_predictions[:i]])
            else:
                values_to_use = all_predictions[i-14:i]
            future_df.loc[i, 'rolling_mean_14'] = np.mean(values_to_use)
        
        if 'rolling_mean_30' in features:
            if i < 30:
                values_to_use = np.concatenate([latest_values[-(30-i):], all_predictions[:i]])
            else:
                values_to_use = all_predictions[i-30:i]
            future_df.loc[i, 'rolling_mean_30'] = np.mean(values_to_use)
        
        # Get features for current prediction
        X_future = future_df.iloc[i][features].values.reshape(1, -1)
        
        # Scale features
        X_future_scaled = scaler.transform(X_future)
        
        # Make prediction
        prediction = model.predict(X_future_scaled)[0]
        all_predictions.append(prediction)
        
        # Calculate prediction interval
        # Use mean squared error for simple confidence interval
        mse = np.mean((model.predict(X_scaled) - y) ** 2)
        std_error = np.sqrt(mse)
        prediction_intervals.append(1.96 * std_error)
    
    # Prepare result dataframe
    result = pd.DataFrame({
        'date': future_dates,
        'forecast': all_predictions,
        'lower': [all_predictions[i] - prediction_intervals[i] for i in range(len(all_predictions))],
        'upper': [all_predictions[i] + prediction_intervals[i] for i in range(len(all_predictions))]
    })
    
    return result

def forecast_with_moving_average(df, periods, window=7):
    """
    Forecast using Simple Moving Average (fallback method).
    
    Args:
        df (pd.DataFrame): Historical data
        periods (int): Number of periods to forecast
        window (int): Window size for moving average
        
    Returns:
        pd.DataFrame: Dataframe with forecast values
    """
    # Calculate moving average
    if len(df) < window:
        window = len(df)
    
    moving_avg = df['value'].rolling(window=window).mean().iloc[-1]
    
    # Create future dates
    last_date = df['date'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods)
    
    # Create constant forecast
    forecast = [moving_avg] * periods
    
    # Calculate simple error estimate
    error_std = df['value'].std()
    
    # Prepare result dataframe
    result = pd.DataFrame({
        'date': future_dates,
        'forecast': forecast,
        'lower': [f - 1.96 * error_std for f in forecast],
        'upper': [f + 1.96 * error_std for f in forecast]
    })
    
    return result
