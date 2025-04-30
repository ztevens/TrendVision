import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Import custom modules
from data_sources import load_data_sources, get_data_from_source
from data_processor import process_data, filter_data
from visualization import create_visualization
from forecasting import forecast_trend
from utils import format_large_number, export_data

# Page configuration
st.set_page_config(
    page_title="TrendVision AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'data_sources' not in st.session_state:
    st.session_state.data_sources = load_data_sources()
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = 'line'
if 'visualization_type' not in st.session_state:
    st.session_state.visualization_type = 'trend'

# Main application header
st.title("📊 TrendVision AI")
st.subheader("Advanced Trend Analysis & Forecasting Platform")

# Sidebar for navigation and controls
with st.sidebar:
    st.title("Navigation")
    
    # Data source selection
    st.header("Data Source")
    data_source = st.selectbox(
        "Select Data Source", 
        options=list(st.session_state.data_sources.keys()),
        index=0
    )
    
    # Load data button
    if st.button("Load Data"):
        with st.spinner("Loading data..."):
            # Reset the platform and metric selection to make sure we get fresh data
            if 'selected_platform' in st.session_state:
                del st.session_state.selected_platform
            if 'selected_metric' in st.session_state:
                del st.session_state.selected_metric
                
            data = get_data_from_source(st.session_state.data_sources[data_source])
            # Save the current data source configuration for later use
            st.session_state.current_data_source = st.session_state.data_sources[data_source]
            st.session_state.current_data = data
            st.session_state.current_visualization = True
            st.session_state.current_visualization_type = 'trend'
            st.session_state.current_chart_type = 'line'
            st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success(f"Data loaded successfully at {st.session_state.last_update}")
            
    # Date range selector (only if data is loaded)
    if st.session_state.current_data is not None:
        st.header("Date Range")
        
        # Get min and max dates from data
        min_date = st.session_state.current_data['date'].min()
        max_date = st.session_state.current_data['date'].max()
        
        date_range = st.date_input(
            "Select date range",
            value=[
                min_date,
                max_date
            ],
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_data = filter_data(st.session_state.current_data, start_date, end_date)
            st.session_state.filtered_data = filtered_data
        
    # Visualization options
    st.header("Visualization")
    viz_type = st.selectbox(
        "Select Visualization Type",
        options=["Trend Analysis", "Comparison", "Distribution", "Composition"],
        index=0
    )
    st.session_state.visualization_type = viz_type.lower().replace(" ", "_")
    
    chart_type = st.selectbox(
        "Select Chart Type",
        options=["Line", "Bar", "Scatter", "Area", "Pie", "Heatmap"],
        index=0
    )
    st.session_state.chart_type = chart_type.lower()
    
    # Forecasting options
    st.header("Forecasting")
    forecast_enabled = st.checkbox("Enable Forecasting", value=False)
    
    if forecast_enabled:
        forecast_days = st.slider("Forecast Period (Days)", 7, 365, 30)
        forecast_method = st.selectbox(
            "Forecast Method",
            options=["Prophet", "ARIMA", "Exponential Smoothing", "Linear Regression"],
            index=0
        )
        
        if st.button("Generate Forecast"):
            if st.session_state.current_data is not None:
                with st.spinner("Generating forecast..."):
                    forecast_data = forecast_trend(
                        st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data,
                        method=forecast_method.lower().replace(" ", "_"),
                        periods=forecast_days
                    )
                    st.session_state.forecast_data = forecast_data
                    st.success(f"Forecast generated for {forecast_days} days")
    
    # Export options
    st.header("Export Options")
    export_format = st.selectbox(
        "Export Format",
        options=["CSV", "Excel", "JSON"],
        index=0
    )
    
    if st.button("Export Data"):
        if st.session_state.current_data is not None:
            data_to_export = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data
            export_data(data_to_export, format=export_format.lower())
    
    # Settings
    st.header("Settings")
    if st.checkbox("Dark Mode", value=st.session_state.dark_mode):
        st.session_state.dark_mode = True
    else:
        st.session_state.dark_mode = False

# Main content area
if st.session_state.current_data is None:
    # Welcome screen with stock photos
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://images.unsplash.com/photo-1526628953301-3e589a6a8b74", caption="Advanced Data Visualization")
        st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", caption="Trend Analysis")
    
    with col2:
        st.image("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3", caption="Business Intelligence Dashboard")
        st.image("https://images.unsplash.com/photo-1653389525308-e7ab9fc0c260", caption="Real-time Analytics")
    
    # Platform introduction
    st.header("Welcome to TrendVision AI")
    st.write("""
    TrendVision AI is a powerful trend analysis and forecasting platform designed to help you make data-driven decisions.
    With advanced visualization capabilities, multi-source data integration, and predictive analytics, TrendVision AI gives you the insights you need to stay ahead of the curve.
    
    To get started, select a data source from the sidebar and click 'Load Data'.
    """)
    
    # Features
    st.header("Key Features")
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.subheader("📊 Advanced Visualizations")
        st.write("Interactive charts and graphs powered by Plotly")
        
        st.subheader("🔍 Deep Trend Analysis")
        st.write("Uncover patterns and insights in your data")
    
    with feature_col2:
        st.subheader("🔮 Predictive Forecasting")
        st.write("Forecast future trends with advanced algorithms")
        
        st.subheader("📱 Responsive Design")
        st.write("Optimized for all devices and screen sizes")
    
    with feature_col3:
        st.subheader("🔄 Multi-source Integration")
        st.write("Connect to multiple data sources seamlessly")
        
        st.subheader("📤 Export Capabilities")
        st.write("Export data and visualizations in multiple formats")

else:
    # Display data and visualizations when data is loaded
    st.header(f"Data Analysis: {data_source}")
    
    # Display last update time
    st.caption(f"Last updated: {st.session_state.last_update}")
    
    # Display data summary
    data_to_display = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data
    
    # Key metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    # Assuming data has a 'value' column for demonstration
    with metric_col1:
        st.metric(
            label="Total Records", 
            value=format_large_number(len(data_to_display))
        )
    
    with metric_col2:
        if 'value' in data_to_display.columns:
            avg_value = data_to_display['value'].mean()
            st.metric(
                label="Average Value", 
                value=f"{avg_value:.2f}"
            )
    
    with metric_col3:
        if 'value' in data_to_display.columns:
            min_value = data_to_display['value'].min()
            st.metric(
                label="Minimum Value", 
                value=f"{min_value:.2f}"
            )
    
    with metric_col4:
        if 'value' in data_to_display.columns:
            max_value = data_to_display['value'].max()
            st.metric(
                label="Maximum Value", 
                value=f"{max_value:.2f}"
            )
    
    # Data visualization
    st.subheader("Data Visualization")
    
    # Create visualization based on selected type
    fig = create_visualization(
        data_to_display,
        visualization_type=st.session_state.visualization_type,
        chart_type=st.session_state.chart_type,
        forecast_data=st.session_state.forecast_data
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("Data Table")
    st.dataframe(data_to_display, use_container_width=True)
    
    # Advanced analysis
    if st.checkbox("Show Advanced Analysis"):
        st.subheader("Advanced Analysis")
        
        advanced_tabs = st.tabs(["Correlation Analysis", "Statistical Summary", "Anomaly Detection"])
        
        with advanced_tabs[0]:
            st.write("Correlation between variables in the dataset")
            
            # Only include numeric columns for correlation
            numeric_cols = data_to_display.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) > 1:
                corr = data_to_display[numeric_cols].corr()
                fig_corr = px.imshow(
                    corr,
                    text_auto=True,
                    color_continuous_scale='RdBu_r'
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("Not enough numeric columns for correlation analysis")
        
        with advanced_tabs[1]:
            st.write("Statistical summary of the dataset")
            st.dataframe(data_to_display.describe(), use_container_width=True)
        
        with advanced_tabs[2]:
            st.write("Anomaly detection in the dataset")
            
            if 'value' in data_to_display.columns:
                # Simple anomaly detection using Z-score
                mean = data_to_display['value'].mean()
                std = data_to_display['value'].std()
                threshold = 3
                
                data_to_display['z_score'] = (data_to_display['value'] - mean) / std
                anomalies = data_to_display[abs(data_to_display['z_score']) > threshold]
                
                if not anomalies.empty:
                    st.write(f"Found {len(anomalies)} anomalies in the data")
                    st.dataframe(anomalies, use_container_width=True)
                    
                    # Visualize anomalies
                    fig_anomaly = go.Figure()
                    
                    # Add normal data points
                    fig_anomaly.add_trace(go.Scatter(
                        x=data_to_display['date'],
                        y=data_to_display['value'],
                        mode='lines',
                        name='Normal Data'
                    ))
                    
                    # Add anomaly points
                    fig_anomaly.add_trace(go.Scatter(
                        x=anomalies['date'],
                        y=anomalies['value'],
                        mode='markers',
                        marker=dict(
                            color='red',
                            size=10,
                            line=dict(
                                color='black',
                                width=2
                            )
                        ),
                        name='Anomalies'
                    ))
                    
                    fig_anomaly.update_layout(
                        title="Anomaly Detection",
                        xaxis_title="Date",
                        yaxis_title="Value"
                    )
                    
                    st.plotly_chart(fig_anomaly, use_container_width=True)
                else:
                    st.write("No anomalies detected in the data")
            else:
                st.info("No 'value' column found for anomaly detection")
