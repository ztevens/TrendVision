import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta
import random
import io

def load_data_sources():
    """
    Load available data sources for the application.
    
    Returns:
        dict: Dictionary of data sources with their configurations
    """
    
    # Define data sources with their configurations
    data_sources = {
        "Stock Market Data": {
            "type": "yfinance",
            "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
            "period": "1y",
            "interval": "1d"
        },
        "Economic Indicators": {
            "type": "simulated",
            "indicators": ["GDP", "Inflation", "Unemployment", "Interest Rate"],
            "start_date": "2020-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d")
        },
        "Social Media Trends": {
            "type": "simulated",
            "platforms": ["Twitter", "Facebook", "Instagram", "LinkedIn", "TikTok", "YouTube"],
            "metrics": ["Engagement", "Followers", "Reach", "Impressions"],
            "start_date": "2022-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d")
        },
        "E-commerce Sales": {
            "type": "simulated",
            "products": ["Electronics", "Clothing", "Home Goods", "Beauty", "Books"],
            "metrics": ["Revenue", "Units Sold", "Average Order Value"],
            "start_date": "2021-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d")
        },
        "Web Analytics": {
            "type": "simulated",
            "metrics": ["Page Views", "Unique Visitors", "Bounce Rate", "Conversion Rate"],
            "start_date": "2022-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d")
        },
        "Upload Custom Data": {
            "type": "upload",
            "formats": ["csv", "excel", "json"]
        }
    }
    
    return data_sources

def get_data_from_source(source_config):
    """
    Get data from the selected data source based on its configuration.
    
    Args:
        source_config (dict): Configuration for the data source
        
    Returns:
        pd.DataFrame: Dataframe containing the loaded data
    """
    
    if source_config["type"] == "yfinance":
        # Get stock market data from yfinance
        data = get_stock_data(source_config)
    elif source_config["type"] == "simulated":
        # Generate simulated data
        data = generate_simulated_data(source_config)
    elif source_config["type"] == "upload":
        # Handle uploaded data
        data = handle_uploaded_data()
    else:
        st.error(f"Unknown data source type: {source_config['type']}")
        return None
    
    return data

def get_stock_data(config):
    """
    Get stock market data using yfinance.
    
    Args:
        config (dict): Configuration for yfinance data source
        
    Returns:
        pd.DataFrame: Dataframe containing stock data
    """
    # Let the user select which ticker to download
    ticker = st.sidebar.selectbox("Select Ticker", config["tickers"])
    
    # Download data
    data = yf.download(
        ticker,
        period=config["period"],
        interval=config["interval"],
        progress=False
    )
    
    # Reset index to make Date a column
    data = data.reset_index()
    
    # Rename columns to be more user-friendly
    data = data.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume"
    })
    
    # Add a value column (use adjusted close)
    data["value"] = data["adj_close"]
    
    # Add metadata columns
    data["ticker"] = ticker
    data["source"] = "yfinance"
    
    return data

def generate_simulated_data(config):
    """
    Generate simulated data based on configuration.
    
    Args:
        config (dict): Configuration for simulated data
        
    Returns:
        pd.DataFrame: Dataframe containing simulated data
    """
    # Parse dates
    start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(config["end_date"], "%Y-%m-%d")
    
    # Generate date range
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    
    # Create empty dataframe
    df = pd.DataFrame({"date": date_range})
    
    # Determine which type of simulated data to generate
    if "indicators" in config:
        # Economic indicators
        indicator = st.sidebar.selectbox("Select Indicator", config["indicators"])
        
        # Generate time series with trend and seasonality
        np.random.seed(42)  # For reproducibility
        
        # Base value and trend
        if indicator == "GDP":
            base = 21000  # Billions
            trend = 100
            seasonality = 50
            noise_factor = 200
        elif indicator == "Inflation":
            base = 2.0  # Percent
            trend = 0.01
            seasonality = 0.5
            noise_factor = 0.2
        elif indicator == "Unemployment":
            base = 5.0  # Percent
            trend = -0.01
            seasonality = 0.3
            noise_factor = 0.1
        elif indicator == "Interest Rate":
            base = 3.0  # Percent
            trend = 0.005
            seasonality = 0.1
            noise_factor = 0.05
        
        # Generate values
        values = []
        for i, date in enumerate(date_range):
            # Trend component
            trend_component = trend * i / 30  # Trend per month
            
            # Seasonality component (yearly cycle)
            season_component = seasonality * np.sin(2 * np.pi * i / 365)
            
            # Random noise
            noise = np.random.normal(0, noise_factor)
            
            # Combine components
            value = base + trend_component + season_component + noise
            values.append(max(0, value))  # Ensure non-negative values
        
        df["value"] = values
        df["indicator"] = indicator
        df["source"] = "simulated"
        
    elif "platforms" in config:
        # Social media trends
        platform = st.sidebar.selectbox("Select Platform", config["platforms"])
        metric = st.sidebar.selectbox("Select Metric", config["metrics"])
        
        # Store the selected platform and metric in session state
        if 'selected_platform' not in st.session_state:
            st.session_state.selected_platform = platform
        elif platform != st.session_state.selected_platform:
            # Update the stored platform if it's different
            st.session_state.selected_platform = platform
            # Force a reload of data
            st.rerun()
            
        if 'selected_metric' not in st.session_state:
            st.session_state.selected_metric = metric
        elif metric != st.session_state.selected_metric:
            # Update the stored metric if it's different
            st.session_state.selected_metric = metric
            # Force a reload of data
            st.rerun()
            
        # Use the stored platform and metric
        platform = st.session_state.selected_platform
        metric = st.session_state.selected_metric
            
        # Reset random seed to ensure different platforms generate different data
        # while keeping them consistent between runs
        platform_seed_map = {
            "Twitter": 42,
            "Facebook": 43,
            "Instagram": 44,
            "LinkedIn": 45,
            "TikTok": 46,
            "YouTube": 47
        }
        seed = platform_seed_map.get(platform, 42)
        np.random.seed(seed)
        
        # Base values vary by platform and metric
        if platform == "Twitter":
            base = 10000
            trend = 50
            seasonality = 1000
            spike_prob = 0.02
            spike_factor = 3
        elif platform == "Facebook":
            base = 50000
            trend = 100
            seasonality = 5000
            spike_prob = 0.01
            spike_factor = 2
        elif platform == "Instagram":
            base = 30000
            trend = 200
            seasonality = 3000
            spike_prob = 0.03
            spike_factor = 4
        elif platform == "LinkedIn":
            base = 8000
            trend = 30
            seasonality = 500
            spike_prob = 0.01
            spike_factor = 1.5
        elif platform == "TikTok":
            base = 20000
            trend = 500
            seasonality = 2000
            spike_prob = 0.04
            spike_factor = 5
        elif platform == "YouTube":
            base = 100000
            trend = 300
            seasonality = 5000
            spike_prob = 0.03
            spike_factor = 6
        
        # Adjust based on metric
        if metric == "Engagement":
            base = base * 0.1
            trend = trend * 0.2
        elif metric == "Followers":
            # Keep as is
            pass
        elif metric == "Reach":
            base = base * 5
            trend = trend * 3
        elif metric == "Impressions":
            base = base * 10
            trend = trend * 5
        
        # Generate values
        values = []
        for i, date in enumerate(date_range):
            # Trend component
            trend_component = trend * i / 30  # Trend per month
            
            # Seasonality component (weekly cycle)
            season_component = seasonality * np.sin(2 * np.pi * i / 7)
            
            # Random noise
            noise = np.random.normal(0, base * 0.05)
            
            # Occasional spikes
            spike = 0
            if np.random.random() < spike_prob:
                spike = base * spike_factor * np.random.random()
            
            # Combine components
            value = base + trend_component + season_component + noise + spike
            values.append(max(0, value))  # Ensure non-negative values
        
        df["value"] = values
        df["platform"] = platform
        df["metric"] = metric
        df["source"] = "simulated"
        
    elif "products" in config:
        # E-commerce sales
        product = st.sidebar.selectbox("Select Product Category", config["products"])
        metric = st.sidebar.selectbox("Select Metric", config["metrics"])
        
        # Generate time series with trend, seasonality, and weekend effects
        np.random.seed(42)  # For reproducibility
        
        # Base values vary by product
        if product == "Electronics":
            base = 50000  # Revenue in $
            trend = 200
            seasonality = 10000
            weekend_factor = 1.5
        elif product == "Clothing":
            base = 30000
            trend = 100
            seasonality = 15000
            weekend_factor = 2.0
        elif product == "Home Goods":
            base = 25000
            trend = 80
            seasonality = 8000
            weekend_factor = 1.8
        elif product == "Beauty":
            base = 15000
            trend = 50
            seasonality = 5000
            weekend_factor = 1.3
        elif product == "Books":
            base = 10000
            trend = 30
            seasonality = 3000
            weekend_factor = 1.2
        
        # Adjust based on metric
        if metric == "Revenue":
            # Keep as is
            pass
        elif metric == "Units Sold":
            base = base / 50  # Average price $50
            trend = trend / 50
            seasonality = seasonality / 50
        elif metric == "Average Order Value":
            base = 50  # AOV in $
            trend = 0.05
            seasonality = 5
            weekend_factor = 1.1
        
        # Generate values
        values = []
        for i, date in enumerate(date_range):
            # Trend component
            trend_component = trend * i / 30  # Trend per month
            
            # Seasonality component (yearly cycle with holiday spike)
            day_of_year = date.dayofyear
            # Higher sales near holidays (end of year)
            holiday_factor = 1 + max(0, np.sin(np.pi * day_of_year / 365) * 0.5)
            season_component = seasonality * holiday_factor
            
            # Weekend effect
            is_weekend = 1 if date.weekday() >= 5 else 0
            weekend_component = base * (weekend_factor - 1) * is_weekend
            
            # Random noise
            noise = np.random.normal(0, base * 0.1)
            
            # Combine components
            value = base + trend_component + season_component + weekend_component + noise
            values.append(max(0, value))  # Ensure non-negative values
        
        df["value"] = values
        df["product"] = product
        df["metric"] = metric
        df["source"] = "simulated"
        
    elif "metrics" in config and "platforms" not in config:
        # Web analytics
        metric = st.sidebar.selectbox("Select Metric", config["metrics"])
        
        # Generate time series with trend, seasonality, and daily patterns
        np.random.seed(42)  # For reproducibility
        
        # Base values vary by metric
        if metric == "Page Views":
            base = 5000
            trend = 10
            seasonality = 1000
            daily_pattern = 0.5
        elif metric == "Unique Visitors":
            base = 2000
            trend = 5
            seasonality = 500
            daily_pattern = 0.6
        elif metric == "Bounce Rate":
            base = 40  # Percent
            trend = -0.01
            seasonality = 5
            daily_pattern = 0.2
        elif metric == "Conversion Rate":
            base = 3  # Percent
            trend = 0.005
            seasonality = 0.5
            daily_pattern = 0.1
        
        # Generate values
        values = []
        for i, date in enumerate(date_range):
            # Trend component
            trend_component = trend * i / 30  # Trend per month
            
            # Seasonality component (weekly cycle)
            season_component = seasonality * np.sin(2 * np.pi * i / 7)
            
            # Daily pattern (higher during work hours)
            hour_of_day = date.hour if hasattr(date, 'hour') else 12
            hour_factor = np.sin(np.pi * hour_of_day / 24)
            daily_component = base * daily_pattern * hour_factor
            
            # Random noise
            noise = np.random.normal(0, base * 0.05)
            
            # Combine components
            value = base + trend_component + season_component + daily_component + noise
            
            # Ensure values are within realistic ranges
            if metric in ["Bounce Rate", "Conversion Rate"]:
                value = max(0, min(100, value))  # 0-100%
            else:
                value = max(0, value)  # Non-negative
                
            values.append(value)
        
        df["value"] = values
        df["metric"] = metric
        df["source"] = "simulated"
    
    return df

def handle_uploaded_data():
    """
    Handle user-uploaded data files.
    
    Returns:
        pd.DataFrame: Dataframe containing uploaded data
    """
    uploaded_file = st.sidebar.file_uploader("Upload your data", type=["csv", "xlsx", "xls", "json"])
    
    if uploaded_file is not None:
        try:
            # Determine file type from extension
            file_extension = uploaded_file.name.split(".")[-1].lower()
            
            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension in ["xlsx", "xls"]:
                df = pd.read_excel(uploaded_file)
            elif file_extension == "json":
                df = pd.read_json(uploaded_file)
            else:
                st.error(f"Unsupported file format: {file_extension}")
                return None
            
            # Check if the dataframe has a date column
            if "date" not in df.columns:
                date_column = st.sidebar.selectbox(
                    "Select date column",
                    options=df.columns
                )
                df = df.rename(columns={date_column: "date"})
            
            # Ensure date column is in datetime format
            df["date"] = pd.to_datetime(df["date"])
            
            # Check if the dataframe has a value column
            if "value" not in df.columns:
                value_column = st.sidebar.selectbox(
                    "Select value column",
                    options=[col for col in df.columns if col != "date"]
                )
                df = df.rename(columns={value_column: "value"})
            
            # Add source metadata
            df["source"] = "upload"
            
            return df
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return None
    
    # If no file uploaded, return None
    return None
