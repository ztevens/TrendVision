import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Import custom modules
from forecasting import forecast_trend
from visualization import create_visualization
from utils import format_large_number

st.title("Forecasting")
st.subheader("Predict future trends based on historical data")

# Check if data is loaded
if 'current_data' not in st.session_state or st.session_state.current_data is None:
    st.info("Please load data from the home page first")
    
    # Show sample forecasting images
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://images.unsplash.com/photo-1653389527532-884074ac1c65", caption="Trend Forecasting")
    with col2:
        st.image("https://images.unsplash.com/photo-1653389526309-f8e2e75f8aaf", caption="Predictive Analytics")
    
    st.markdown("""
    This page provides advanced forecasting capabilities:
    
    - **Multiple Forecasting Methods**: Choose from several prediction algorithms
    - **Configurable Parameters**: Fine-tune your forecasts with model-specific settings
    - **Confidence Intervals**: Visualize uncertainty in predictions
    - **Forecast Evaluation**: Compare model performance and accuracy
    - **What-If Analysis**: Test different scenarios and their impact
    
    Please load a dataset from the home page to get started.
    """)

else:
    # Get the current data
    data = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data
    
    # Sidebar for forecasting options
    with st.sidebar:
        st.header("Forecasting Options")
        
        # Basic forecast settings
        forecast_method = st.selectbox(
            "Forecasting Method",
            options=["Prophet", "ARIMA", "Exponential Smoothing", "Linear Regression", "Random Forest"],
            index=0
        )
        
        forecast_periods = st.slider(
            "Forecast Horizon (Days)",
            min_value=7,
            max_value=365,
            value=30,
            step=1
        )
        
        # Method-specific parameters
        st.subheader(f"{forecast_method} Parameters")
        
        if forecast_method == "Prophet":
            yearly_seasonality = st.checkbox("Yearly Seasonality", value=True)
            weekly_seasonality = st.checkbox("Weekly Seasonality", value=True)
            daily_seasonality = st.checkbox("Daily Seasonality", value=False)
            
            seasonality_mode = st.selectbox(
                "Seasonality Mode",
                options=["Additive", "Multiplicative"],
                index=0
            )
            
            changepoint_prior_scale = st.slider(
                "Changepoint Prior Scale",
                min_value=0.001,
                max_value=0.5,
                value=0.05,
                step=0.001,
                format="%.3f"
            )
        
        elif forecast_method == "ARIMA":
            p = st.slider("p (AR order)", 0, 5, 1)
            d = st.slider("d (Differencing)", 0, 2, 1)
            q = st.slider("q (MA order)", 0, 5, 0)
            
            seasonal = st.checkbox("Seasonal Component", value=False)
            
            if seasonal:
                seasonal_period = st.slider("Seasonal Period", 1, 52, 7)
                P = st.slider("P (Seasonal AR)", 0, 2, 1)
                D = st.slider("D (Seasonal Differencing)", 0, 1, 1)
                Q = st.slider("Q (Seasonal MA)", 0, 2, 0)
        
        elif forecast_method == "Exponential Smoothing":
            trend = st.selectbox(
                "Trend Component",
                options=["None", "Additive", "Multiplicative"],
                index=1
            )
            
            seasonal = st.selectbox(
                "Seasonal Component",
                options=["None", "Additive", "Multiplicative"],
                index=1
            )
            
            if seasonal != "None":
                seasonal_periods = st.slider("Seasonal Periods", 1, 52, 7)
            
            damped = st.checkbox("Damped Trend", value=False)
        
        elif forecast_method == "Linear Regression":
            use_time_features = st.checkbox("Use Time-based Features", value=True)
            use_lag_features = st.checkbox("Use Lag Features", value=True)
            
            if use_lag_features:
                max_lag = min(30, len(data) // 4)
                lag_periods = st.slider("Maximum Lag Periods", 1, max_lag, min(7, max_lag))
        
        elif forecast_method == "Random Forest":
            n_estimators = st.slider("Number of Trees", 10, 200, 100, 10)
            max_depth = st.slider("Maximum Tree Depth", 3, 20, 10)
            
            use_time_features = st.checkbox("Use Time-based Features", value=True)
            use_lag_features = st.checkbox("Use Lag Features", value=True)
            
            if use_lag_features:
                max_lag = min(30, len(data) // 4)
                lag_periods = st.slider("Maximum Lag Periods", 1, max_lag, min(7, max_lag))
        
        # Generate forecast button
        if st.button("Generate Forecast", key="sidebar_forecast_button"):
            with st.spinner("Generating forecast..."):
                # Prepare method-specific parameters
                if forecast_method == "Prophet":
                    forecast_params = {
                        "yearly_seasonality": yearly_seasonality,
                        "weekly_seasonality": weekly_seasonality,
                        "daily_seasonality": daily_seasonality,
                        "seasonality_mode": seasonality_mode.lower(),
                        "changepoint_prior_scale": changepoint_prior_scale
                    }
                
                elif forecast_method == "ARIMA":
                    if seasonal:
                        forecast_params = {
                            "order": (p, d, q),
                            "seasonal_order": (P, D, Q, seasonal_period)
                        }
                    else:
                        forecast_params = {
                            "order": (p, d, q)
                        }
                
                elif forecast_method == "Exponential Smoothing":
                    forecast_params = {
                        "trend": None if trend == "None" else trend.lower(),
                        "seasonal": None if seasonal == "None" else seasonal.lower(),
                        "damped_trend": damped
                    }
                    
                    if seasonal != "None":
                        forecast_params["seasonal_periods"] = seasonal_periods
                
                elif forecast_method == "Linear Regression":
                    forecast_params = {
                        "use_time_features": use_time_features,
                        "use_lag_features": use_lag_features
                    }
                    
                    if use_lag_features:
                        forecast_params["lag_periods"] = lag_periods
                
                elif forecast_method == "Random Forest":
                    forecast_params = {
                        "n_estimators": n_estimators,
                        "max_depth": max_depth,
                        "use_time_features": use_time_features,
                        "use_lag_features": use_lag_features
                    }
                    
                    if use_lag_features:
                        forecast_params["lag_periods"] = lag_periods
                
                # Generate forecast
                forecast_data = forecast_trend(
                    data,
                    method=forecast_method.lower().replace(" ", "_"),
                    periods=forecast_periods,
                    **forecast_params
                )
                
                # Store in session state
                st.session_state.forecast_data = forecast_data
                st.session_state.forecast_method = forecast_method
                st.session_state.forecast_params = forecast_params
                
                st.success(f"Forecast generated for {forecast_periods} days")
    
    # Main content area
    if 'forecast_data' not in st.session_state or st.session_state.forecast_data is None:
        st.info("Use the options in the sidebar to generate a forecast")
        
        # Display historical data
        st.subheader("Historical Data")
        
        fig = px.line(
            data,
            x='date',
            y='value',
            title='Historical Time Series',
            labels={'date': 'Date', 'value': 'Value'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display data stats for forecasting
        if 'date' in data.columns and 'value' in data.columns:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Data Points", len(data))
            
            with col2:
                date_range = (data['date'].max() - data['date'].min()).days
                st.metric("Date Range", f"{date_range} days")
            
            with col3:
                trend_direction = "Up" if data['value'].iloc[-1] > data['value'].iloc[0] else "Down"
                trend_change = ((data['value'].iloc[-1] - data['value'].iloc[0]) / data['value'].iloc[0]) * 100 if data['value'].iloc[0] != 0 else 0
                st.metric("Overall Trend", trend_direction, f"{trend_change:.1f}%")
            
            with col4:
                volatility = data['value'].std() / data['value'].mean() * 100
                st.metric("Volatility", f"{volatility:.1f}%")
        
        # Forecasting guides
        st.subheader("Forecasting Method Guide")
        
        st.markdown("""
        ### Method Selection Guide
        
        - **Prophet**: Best for data with strong seasonal patterns and multiple seasonality levels
        - **ARIMA**: Good for stationary time series or data that can be made stationary
        - **Exponential Smoothing**: Works well with data that has trend and/or seasonal components
        - **Linear Regression**: Simple and interpretable, good for data with clear trends
        - **Random Forest**: Handles non-linear relationships and complex patterns well
        
        ### Tips for Accurate Forecasting
        
        1. **Data Quality**: Ensure your data is clean and has regular intervals
        2. **Sufficient History**: More historical data generally leads to better forecasts
        3. **Parameter Tuning**: Adjust method-specific parameters to improve results
        4. **Evaluation**: Compare multiple methods to find the best for your data
        5. **Seasonality**: Make sure to account for any seasonal patterns in your data
        """)
    
    else:
        # Display forecast results
        st.header("Forecast Results")
        
        # Forecast visualization
        st.subheader("Forecast Visualization")
        
        # Combined actual and forecast data
        fig = go.Figure()
        
        # Add actual data
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=data['value'],
                mode='lines',
                name='Historical Data',
                line=dict(color='blue')
            )
        )
        
        # Add forecast data
        fig.add_trace(
            go.Scatter(
                x=st.session_state.forecast_data['date'],
                y=st.session_state.forecast_data['forecast'],
                mode='lines',
                name='Forecast',
                line=dict(dash='dash', color='red')
            )
        )
        
        # Add confidence intervals if available
        if 'upper' in st.session_state.forecast_data.columns and 'lower' in st.session_state.forecast_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=st.session_state.forecast_data['date'],
                    y=st.session_state.forecast_data['upper'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=st.session_state.forecast_data['date'],
                    y=st.session_state.forecast_data['lower'],
                    mode='lines',
                    line=dict(width=0),
                    fillcolor='rgba(255, 0, 0, 0.2)',
                    fill='tonexty',
                    name='95% Confidence Interval'
                )
            )
        
        # Add forecast method details to title
        method_name = st.session_state.forecast_method if 'forecast_method' in st.session_state else "Forecast"
        fig.update_layout(
            title=f'{method_name} Forecast (Next {len(st.session_state.forecast_data)} days)',
            xaxis_title='Date',
            yaxis_title='Value',
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast metrics
        st.subheader("Forecast Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Current value vs. first forecast
            current_value = data['value'].iloc[-1]
            next_value = st.session_state.forecast_data['forecast'].iloc[0]
            pct_change = ((next_value - current_value) / current_value) * 100 if current_value != 0 else 0
            
            st.metric(
                "Next Period Forecast", 
                f"{next_value:.2f}",
                f"{pct_change:.1f}%"
            )
        
        with col2:
            # Average forecast
            avg_forecast = st.session_state.forecast_data['forecast'].mean()
            avg_historical = data['value'].mean()
            avg_pct_change = ((avg_forecast - avg_historical) / avg_historical) * 100 if avg_historical != 0 else 0
            
            st.metric(
                "Average Forecast", 
                f"{avg_forecast:.2f}",
                f"{avg_pct_change:.1f}%"
            )
        
        with col3:
            # End of forecast period value
            end_value = st.session_state.forecast_data['forecast'].iloc[-1]
            end_pct_change = ((end_value - current_value) / current_value) * 100 if current_value != 0 else 0
            
            st.metric(
                "End of Forecast", 
                f"{end_value:.2f}",
                f"{end_pct_change:.1f}%"
            )
        
        with col4:
            # Forecast trend
            first_forecast = st.session_state.forecast_data['forecast'].iloc[0]
            last_forecast = st.session_state.forecast_data['forecast'].iloc[-1]
            forecast_pct_change = ((last_forecast - first_forecast) / first_forecast) * 100 if first_forecast != 0 else 0
            
            trend_direction = "Up" if forecast_pct_change > 0 else "Down" if forecast_pct_change < 0 else "Flat"
            
            st.metric(
                "Forecast Trend", 
                trend_direction,
                f"{forecast_pct_change:.1f}%"
            )
        
        # Forecast details
        with st.expander("Forecast Details"):
            # Show parameters used for forecast
            st.subheader("Forecast Parameters")
            
            if 'forecast_params' in st.session_state:
                for param, value in st.session_state.forecast_params.items():
                    st.write(f"**{param}:** {value}")
            
            # Show forecast data
            st.subheader("Forecast Data")
            
            forecast_df = st.session_state.forecast_data.copy()
            
            # Format date for display
            if 'date' in forecast_df.columns:
                forecast_df['date'] = forecast_df['date'].dt.strftime('%Y-%m-%d')
            
            # Round numeric columns
            numeric_cols = forecast_df.select_dtypes(include=[np.number]).columns
            forecast_df[numeric_cols] = forecast_df[numeric_cols].round(2)
            
            st.dataframe(forecast_df, use_container_width=True)
        
        # Forecast analysis
        st.subheader("Forecast Analysis")
        
        analysis_tabs = st.tabs(["Forecast Components", "Distribution", "Cumulative Forecast"])
        
        with analysis_tabs[0]:
            # Try to show forecast components (if Prophet was used)
            try:
                if 'forecast_method' in st.session_state and st.session_state.forecast_method == "Prophet":
                    from prophet import Prophet
                    
                    # Prepare data for Prophet
                    prophet_df = data[['date', 'value']].rename(columns={'date': 'ds', 'value': 'y'})
                    
                    # Get parameters
                    params = st.session_state.forecast_params
                    
                    # Create and fit model
                    model = Prophet(
                        yearly_seasonality=params.get('yearly_seasonality', True),
                        weekly_seasonality=params.get('weekly_seasonality', True),
                        daily_seasonality=params.get('daily_seasonality', False),
                        seasonality_mode=params.get('seasonality_mode', 'additive'),
                        changepoint_prior_scale=params.get('changepoint_prior_scale', 0.05)
                    )
                    
                    model.fit(prophet_df)
                    
                    # Create future dataframe
                    future = model.make_future_dataframe(periods=len(st.session_state.forecast_data))
                    forecast = model.predict(future)
                    
                    # Create component plots
                    fig_comp = model.plot_components(forecast)
                    
                    # Convert to Plotly figure for Streamlit
                    import matplotlib.pyplot as plt
                    st.pyplot(fig_comp)
                
                else:
                    # For non-Prophet forecasts, show trend decomposition
                    from statsmodels.tsa.seasonal import seasonal_decompose
                    
                    # Set date as index for decomposition
                    ts_data = data.set_index('date')['value']
                    
                    # Determine period based on data frequency
                    # Assuming daily data, use 7 for weekly pattern
                    period = 7
                    
                    # Check if we have enough data
                    if len(ts_data) >= 2 * period:
                        # Perform decomposition
                        result = seasonal_decompose(
                            ts_data, 
                            model='additive', 
                            period=period
                        )
                        
                        # Create figure with subplots
                        fig = make_subplots(
                            rows=3, 
                            cols=1,
                            subplot_titles=("Trend", "Seasonal", "Residual"),
                            vertical_spacing=0.1
                        )
                        
                        # Add traces
                        fig.add_trace(
                            go.Scatter(x=result.trend.index, y=result.trend, name="Trend"),
                            row=1, col=1
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=result.seasonal.index, y=result.seasonal, name="Seasonal"),
                            row=2, col=1
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=result.resid.index, y=result.resid, name="Residual"),
                            row=3, col=1
                        )
                        
                        # Update layout
                        fig.update_layout(
                            height=600,
                            title_text="Time Series Components",
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"Not enough data for decomposition with period={period}. Need at least {2*period} data points.")
            
            except Exception as e:
                st.error(f"Error showing forecast components: {str(e)}")
                
                # Fallback to simple component analysis
                st.write("Simple trend analysis:")
                
                # Calculate rolling statistics
                window_size = max(3, len(data) // 10)
                data['rolling_mean'] = data['value'].rolling(window=window_size).mean()
                
                fig = px.line(
                    data,
                    x='date',
                    y=['value', 'rolling_mean'],
                    title=f"Trend Analysis with {window_size}-Period Moving Average",
                    labels={'date': 'Date', 'value': 'Value', 'rolling_mean': 'Trend'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with analysis_tabs[1]:
            # Forecast distribution analysis
            forecast_values = st.session_state.forecast_data['forecast']
            
            col_dist1, col_dist2 = st.columns(2)
            
            with col_dist1:
                # Histogram of forecast values
                fig_hist = px.histogram(
                    forecast_values,
                    title="Forecast Value Distribution",
                    labels={'value': 'Value', 'count': 'Frequency'}
                )
                
                fig_hist.update_layout(showlegend=False)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col_dist2:
                # Box plot of forecast vs historical
                comparison_data = pd.DataFrame({
                    'Type': ['Historical'] * len(data) + ['Forecast'] * len(forecast_values),
                    'Value': pd.concat([data['value'], forecast_values])
                })
                
                fig_box = px.box(
                    comparison_data,
                    x='Type',
                    y='Value',
                    title="Historical vs Forecast Distribution",
                    color='Type'
                )
                
                st.plotly_chart(fig_box, use_container_width=True)
            
            # Distribution statistics
            st.subheader("Distribution Statistics")
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("Mean Forecast", f"{forecast_values.mean():.2f}")
                st.metric("Median Forecast", f"{forecast_values.median():.2f}")
            
            with col_stat2:
                st.metric("Min Forecast", f"{forecast_values.min():.2f}")
                st.metric("Max Forecast", f"{forecast_values.max():.2f}")
            
            with col_stat3:
                st.metric("Forecast Std Dev", f"{forecast_values.std():.2f}")
                cv = (forecast_values.std() / forecast_values.mean()) * 100 if forecast_values.mean() != 0 else 0
                st.metric("Coefficient of Variation", f"{cv:.1f}%")
        
        with analysis_tabs[2]:
            # Cumulative forecast analysis
            st.subheader("Cumulative Values")
            
            # Calculate cumulative values
            last_value = data['value'].iloc[-1]
            cumulative_historical = data['value'].sum()
            cumulative_forecast = st.session_state.forecast_data['forecast'].sum()
            
            # Display cumulative metrics
            cumul_col1, cumul_col2, cumul_col3 = st.columns(3)
            
            with cumul_col1:
                st.metric("Cumulative Historical", f"{cumulative_historical:.2f}")
            
            with cumul_col2:
                st.metric("Cumulative Forecast", f"{cumulative_forecast:.2f}")
            
            with cumul_col3:
                forecast_periods = len(st.session_state.forecast_data)
                daily_avg_forecast = cumulative_forecast / forecast_periods
                st.metric("Daily Average (Forecast)", f"{daily_avg_forecast:.2f}")
            
            # Create cumulative plot
            forecast_df = st.session_state.forecast_data.copy()
            forecast_df['cumulative'] = forecast_df['forecast'].cumsum()
            
            fig_cumul = px.line(
                forecast_df,
                x='date',
                y='cumulative',
                title="Cumulative Forecast",
                labels={'date': 'Date', 'cumulative': 'Cumulative Value'}
            )
            
            st.plotly_chart(fig_cumul, use_container_width=True)
        
        # What-if analysis section
        st.header("What-If Analysis")
        
        what_if_col1, what_if_col2 = st.columns(2)
        
        with what_if_col1:
            growth_factor = st.slider(
                "Growth Factor",
                min_value=0.5,
                max_value=1.5,
                value=1.0,
                step=0.01,
                help="Multiply forecast values by this factor"
            )
        
        with what_if_col2:
            shift_amount = st.slider(
                "Shift Amount",
                min_value=-50.0,
                max_value=50.0,
                value=0.0,
                step=1.0,
                help="Add this amount to all forecast values"
            )
        
        # Apply what-if adjustments
        adjusted_forecast = st.session_state.forecast_data.copy()
        adjusted_forecast['adjusted'] = adjusted_forecast['forecast'] * growth_factor + shift_amount
        
        if 'upper' in adjusted_forecast.columns and 'lower' in adjusted_forecast.columns:
            adjusted_forecast['adjusted_upper'] = adjusted_forecast['upper'] * growth_factor + shift_amount
            adjusted_forecast['adjusted_lower'] = adjusted_forecast['lower'] * growth_factor + shift_amount
        
        # Create what-if visualization
        fig_what_if = go.Figure()
        
        # Add actual data
        fig_what_if.add_trace(
            go.Scatter(
                x=data['date'],
                y=data['value'],
                mode='lines',
                name='Historical Data',
                line=dict(color='blue')
            )
        )
        
        # Add original forecast
        fig_what_if.add_trace(
            go.Scatter(
                x=st.session_state.forecast_data['date'],
                y=st.session_state.forecast_data['forecast'],
                mode='lines',
                name='Original Forecast',
                line=dict(dash='dash', color='red')
            )
        )
        
        # Add adjusted forecast
        fig_what_if.add_trace(
            go.Scatter(
                x=adjusted_forecast['date'],
                y=adjusted_forecast['adjusted'],
                mode='lines',
                name='Adjusted Forecast',
                line=dict(dash='dash', color='green')
            )
        )
        
        # Add confidence intervals for adjusted forecast if available
        if 'adjusted_upper' in adjusted_forecast.columns and 'adjusted_lower' in adjusted_forecast.columns:
            fig_what_if.add_trace(
                go.Scatter(
                    x=adjusted_forecast['date'],
                    y=adjusted_forecast['adjusted_upper'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                )
            )
            fig_what_if.add_trace(
                go.Scatter(
                    x=adjusted_forecast['date'],
                    y=adjusted_forecast['adjusted_lower'],
                    mode='lines',
                    line=dict(width=0),
                    fillcolor='rgba(0, 128, 0, 0.2)',
                    fill='tonexty',
                    name='Adjusted Confidence Interval'
                )
            )
        
        # Update layout
        fig_what_if.update_layout(
            title='What-If Analysis',
            xaxis_title='Date',
            yaxis_title='Value',
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_what_if, use_container_width=True)
        
        # Compare metrics for original and adjusted forecasts
        what_if_metrics_col1, what_if_metrics_col2 = st.columns(2)
        
        with what_if_metrics_col1:
            st.subheader("Original Forecast")
            
            total_original = st.session_state.forecast_data['forecast'].sum()
            avg_original = st.session_state.forecast_data['forecast'].mean()
            end_original = st.session_state.forecast_data['forecast'].iloc[-1]
            
            st.metric("Total", f"{total_original:.2f}")
            st.metric("Average", f"{avg_original:.2f}")
            st.metric("End Value", f"{end_original:.2f}")
        
        with what_if_metrics_col2:
            st.subheader("Adjusted Forecast")
            
            total_adjusted = adjusted_forecast['adjusted'].sum()
            avg_adjusted = adjusted_forecast['adjusted'].mean()
            end_adjusted = adjusted_forecast['adjusted'].iloc[-1]
            
            st.metric(
                "Total", 
                f"{total_adjusted:.2f}", 
                f"{((total_adjusted - total_original) / total_original) * 100:.1f}%" if total_original != 0 else ""
            )
            
            st.metric(
                "Average", 
                f"{avg_adjusted:.2f}", 
                f"{((avg_adjusted - avg_original) / avg_original) * 100:.1f}%" if avg_original != 0 else ""
            )
            
            st.metric(
                "End Value", 
                f"{end_adjusted:.2f}", 
                f"{((end_adjusted - end_original) / end_original) * 100:.1f}%" if end_original != 0 else ""
            )
