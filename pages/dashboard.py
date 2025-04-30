import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import custom modules
from data_sources import load_data_sources, get_data_from_source
from data_processor import process_data, filter_data
from visualization import create_visualization
from forecasting import forecast_trend
from utils import format_large_number, export_data

st.title("Dashboard")
st.subheader("Key Performance Indicators and Overview")

# Check if data is loaded
if 'current_data' not in st.session_state or st.session_state.current_data is None:
    st.info("Please load data from the home page first")
    
    # Show sample dashboard image
    st.image("https://images.unsplash.com/photo-1556155092-490a1ba16284", caption="Business Intelligence Dashboard")
    
    st.markdown("""
    This dashboard will display key performance indicators and visualizations based on your data.
    
    Features include:
    - Key metric summaries
    - Time series trend analysis
    - Comparative analytics
    - Data distributions
    - Forecast projections
    
    Please load a dataset from the home page to get started.
    """)
else:
    # Get the current data
    data = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data
    
    # Create dashboard layout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader("Data Overview")
        
        # Display main trend visualization
        fig_main = create_visualization(
            data,
            visualization_type='trend',
            chart_type='line',
            forecast_data=st.session_state.forecast_data if 'forecast_data' in st.session_state else None
        )
        
        st.plotly_chart(fig_main, use_container_width=True)
    
    with col2:
        st.subheader("Key Metrics")
        
        # Calculate metrics
        num_records = len(data)
        
        if 'value' in data.columns:
            avg_value = data['value'].mean()
            max_value = data['value'].max()
            min_value = data['value'].min()
            
            # Calculate change
            if len(data) > 1:
                current_value = data['value'].iloc[-1]
                previous_value = data['value'].iloc[-2]
                percent_change = ((current_value - previous_value) / previous_value) * 100 if previous_value != 0 else 0
            else:
                percent_change = 0
            
            # Display metrics
            st.metric("Total Records", format_large_number(num_records))
            st.metric("Average Value", f"{avg_value:.2f}")
            st.metric("Current Value", f"{data['value'].iloc[-1]:.2f}", f"{percent_change:.1f}%")
            st.metric("Min/Max", f"{min_value:.2f} / {max_value:.2f}")
        
        else:
            st.metric("Total Records", format_large_number(num_records))
    
    with col3:
        st.subheader("Distribution")
        
        # Create distribution visualization
        if 'value' in data.columns:
            fig_dist = create_visualization(
                data,
                visualization_type='distribution',
                chart_type='histogram'
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
    
    # Second row
    st.subheader("Detailed Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Time Analysis", "Comparison", "Forecast"])
    
    with tab1:
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            # Monthly trend
            if 'date' in data.columns:
                # Group by month
                data['month'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m')
                monthly_data = data.groupby('month')['value'].mean().reset_index()
                
                fig_monthly = px.bar(
                    monthly_data,
                    x='month',
                    y='value',
                    title='Monthly Trend',
                    labels={'month': 'Month', 'value': 'Average Value'}
                )
                
                st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col_t2:
            # Day of week pattern
            if 'date' in data.columns:
                # Group by day of week
                data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
                day_names = {
                    0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
                    3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
                }
                data['day_name'] = data['day_of_week'].map(day_names)
                
                daily_data = data.groupby('day_name')['value'].mean().reset_index()
                
                # Set correct order of days
                daily_data['day_order'] = daily_data['day_name'].map({
                    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
                    'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
                })
                daily_data = daily_data.sort_values('day_order')
                
                fig_daily = px.line(
                    daily_data,
                    x='day_name',
                    y='value',
                    title='Day of Week Pattern',
                    labels={'day_name': 'Day', 'value': 'Average Value'},
                    markers=True
                )
                
                st.plotly_chart(fig_daily, use_container_width=True)
    
    with tab2:
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            # Find a category column for comparison
            category_col = None
            for col in data.columns:
                if col not in ['date', 'value', 'month', 'day_of_week', 'day_name'] and data[col].nunique() <= 10:
                    category_col = col
                    break
            
            if category_col:
                fig_comp = create_visualization(
                    data,
                    visualization_type='comparison',
                    chart_type='bar'
                )
                
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                # If no suitable category, show variation by month
                if 'month' in data.columns:
                    fig_comp = px.box(
                        data,
                        x='month',
                        y='value',
                        title='Value Distribution by Month',
                        labels={'month': 'Month', 'value': 'Value'}
                    )
                    
                    st.plotly_chart(fig_comp, use_container_width=True)
        
        with col_c2:
            # Composition visualization
            fig_comp = create_visualization(
                data,
                visualization_type='composition',
                chart_type='pie'
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
    
    with tab3:
        # Forecast visualization and controls
        if 'forecast_data' in st.session_state and st.session_state.forecast_data is not None:
            st.subheader("Forecast Results")
            
            # Combined actual and forecast data
            fig_forecast = go.Figure()
            
            # Add actual data
            fig_forecast.add_trace(
                go.Scatter(
                    x=data['date'],
                    y=data['value'],
                    mode='lines',
                    name='Actual Data',
                    line=dict(color='blue')
                )
            )
            
            # Add forecast data
            fig_forecast.add_trace(
                go.Scatter(
                    x=st.session_state.forecast_data['date'],
                    y=st.session_state.forecast_data['forecast'],
                    mode='lines',
                    name='Forecast',
                    line=dict(dash='dash', color='red')
                )
            )
            
            # Add confidence intervals
            fig_forecast.add_trace(
                go.Scatter(
                    x=st.session_state.forecast_data['date'],
                    y=st.session_state.forecast_data['upper'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                )
            )
            fig_forecast.add_trace(
                go.Scatter(
                    x=st.session_state.forecast_data['date'],
                    y=st.session_state.forecast_data['lower'],
                    mode='lines',
                    line=dict(width=0),
                    fillcolor='rgba(255, 0, 0, 0.2)',
                    fill='tonexty',
                    name='Confidence Interval'
                )
            )
            
            fig_forecast.update_layout(
                title='Actual vs Forecast',
                xaxis_title='Date',
                yaxis_title='Value',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Forecast metrics
            forecast_data = st.session_state.forecast_data
            
            # Display forecast statistics
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                last_actual = data['value'].iloc[-1]
                next_forecast = forecast_data['forecast'].iloc[0]
                pct_change = ((next_forecast - last_actual) / last_actual) * 100 if last_actual != 0 else 0
                
                st.metric(
                    "Next Period Forecast", 
                    f"{next_forecast:.2f}",
                    f"{pct_change:.1f}%"
                )
            
            with col_f2:
                avg_forecast = forecast_data['forecast'].mean()
                avg_actual = data['value'].mean()
                avg_pct_change = ((avg_forecast - avg_actual) / avg_actual) * 100 if avg_actual != 0 else 0
                
                st.metric(
                    "Average Forecast", 
                    f"{avg_forecast:.2f}",
                    f"{avg_pct_change:.1f}%"
                )
            
            with col_f3:
                # Calculate trend direction
                first_forecast = forecast_data['forecast'].iloc[0]
                last_forecast = forecast_data['forecast'].iloc[-1]
                trend_pct = ((last_forecast - first_forecast) / first_forecast) * 100 if first_forecast != 0 else 0
                
                st.metric(
                    "Forecast Trend", 
                    "Up" if trend_pct > 0 else "Down" if trend_pct < 0 else "Flat",
                    f"{trend_pct:.1f}%"
                )
        
        else:
            st.info("Generate a forecast from the sidebar to see forecast analysis.")
            
            # Show forecast controls in this tab as well
            forecast_method = st.selectbox(
                "Forecast Method",
                options=["Prophet", "ARIMA", "Exponential Smoothing", "Linear Regression"],
                index=0,
                key="tab_forecast_method"
            )
            
            forecast_days = st.slider(
                "Forecast Period (Days)", 
                7, 365, 30,
                key="tab_forecast_days"
            )
            
            if st.button("Generate Forecast", key="tab_generate_forecast"):
                if 'current_data' in st.session_state and st.session_state.current_data is not None:
                    with st.spinner("Generating forecast..."):
                        data_to_use = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data
                        forecast_data = forecast_trend(
                            data_to_use,
                            method=forecast_method.lower().replace(" ", "_"),
                            periods=forecast_days
                        )
                        st.session_state.forecast_data = forecast_data
                        st.success(f"Forecast generated for {forecast_days} days")
                        st.rerun()
