import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import custom modules
from data_processor import process_data, filter_data
from visualization import create_visualization
from utils import format_large_number, detect_seasonal_pattern, calculate_trend_strength

st.title("Trend Analysis")
st.subheader("Discover patterns and insights in your data")

# Check if data is loaded
if 'current_data' not in st.session_state or st.session_state.current_data is None:
    st.info("Please load data from the home page first")
    
    # Show sample trend analysis images
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", caption="Trend Analysis Dashboard")
    with col2:
        st.image("https://images.unsplash.com/photo-1653389525308-e7ab9fc0c260", caption="Pattern Detection")
    
    st.markdown("""
    This page provides advanced trend analysis tools:
    
    - **Pattern Detection**: Identify seasonal patterns and trends
    - **Correlation Analysis**: Discover relationships between variables
    - **Decomposition**: Break down trends into components
    - **Anomaly Detection**: Find outliers and unusual patterns
    - **Comparative Analysis**: Compare trends across different segments
    
    Please load a dataset from the home page to get started.
    """)

else:
    # Get the current data
    data = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data
    
    # Sidebar for trend analysis options
    with st.sidebar:
        st.header("Analysis Options")
        
        analysis_type = st.selectbox(
            "Analysis Type",
            options=["Pattern Detection", "Correlation Analysis", "Trend Decomposition", "Anomaly Detection", "Comparative Analysis"],
            index=0
        )
        
        # Additional options based on analysis type
        if analysis_type == "Pattern Detection":
            pattern_timeframe = st.selectbox(
                "Timeframe",
                options=["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
                index=1
            )
            
            detect_seasonality = st.checkbox("Detect Seasonal Patterns", value=True)
            detect_trends = st.checkbox("Detect Trends", value=True)
            
            smoothing = st.slider("Smoothing Factor", 0.0, 1.0, 0.2, 0.05)
        
        elif analysis_type == "Correlation Analysis":
            correlation_method = st.selectbox(
                "Correlation Method",
                options=["Pearson", "Spearman", "Kendall"],
                index=0
            )
            
            if 'date' in data.columns:
                # Create lag options
                max_lag = min(30, len(data) // 3)
                lag_periods = st.slider("Lag Periods", 1, max_lag, 1)
        
        elif analysis_type == "Trend Decomposition":
            decomp_model = st.selectbox(
                "Decomposition Model",
                options=["Additive", "Multiplicative"],
                index=0
            )
            
            period = st.slider("Period Length (Days)", 7, 365, 7)
        
        elif analysis_type == "Anomaly Detection":
            anomaly_method = st.selectbox(
                "Detection Method",
                options=["Z-Score", "IQR", "Moving Average"],
                index=0
            )
            
            threshold = st.slider("Threshold", 1.0, 5.0, 3.0, 0.1)
        
        elif analysis_type == "Comparative Analysis":
            # Find categorical columns
            categorical_cols = [col for col in data.columns if col not in ['date', 'value'] and data[col].nunique() <= 10]
            
            if categorical_cols:
                compare_by = st.selectbox("Compare By", options=categorical_cols)
            else:
                # If no categorical columns, create time-based comparison
                if 'date' in data.columns:
                    period_options = ["Month", "Quarter", "Year", "Day of Week"]
                    compare_by = st.selectbox("Compare By", options=period_options)
    
    # Main content area
    if analysis_type == "Pattern Detection":
        st.header("Pattern Detection")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create time series plot
            if 'date' in data.columns and 'value' in data.columns:
                # Apply smoothing if needed
                if smoothing > 0:
                    window_size = max(2, int(len(data) * smoothing))
                    data['smoothed_value'] = data['value'].rolling(window=window_size, center=True).mean()
                    # For the beginning and end of the series where rolling creates NaN
                    data['smoothed_value'] = data['smoothed_value'].fillna(data['value'])
                    y_col = 'smoothed_value'
                else:
                    y_col = 'value'
                
                fig = px.line(
                    data,
                    x='date',
                    y=y_col,
                    title=f'Time Series Analysis ({pattern_timeframe})',
                    labels={'date': 'Date', y_col: 'Value'}
                )
                
                if detect_trends:
                    # Add trend line
                    x = np.arange(len(data))
                    y = data[y_col].values
                    
                    # Fit polynomial for trend
                    z = np.polyfit(x, y, 1)
                    p = np.poly1d(z)
                    
                    fig.add_trace(
                        go.Scatter(
                            x=data['date'],
                            y=p(x),
                            mode='lines',
                            name='Trend',
                            line=dict(color='red', dash='dash')
                        )
                    )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pattern detection metrics
            st.subheader("Pattern Metrics")
            
            if 'value' in data.columns:
                # Detect seasonal patterns
                if detect_seasonality:
                    seasonal_pattern = detect_seasonal_pattern(data)
                    
                    if seasonal_pattern['has_seasonality']:
                        st.success(f"✓ Detected {seasonal_pattern['period_name']} seasonality")
                        st.metric("Seasonality Strength", f"{seasonal_pattern['strength']:.2f}")
                    else:
                        st.info(seasonal_pattern['message'])
                
                # Calculate trend strength
                if detect_trends:
                    trend_strength = calculate_trend_strength(data)
                    trend_direction = "Upward" if trend_strength > 0 and data['value'].iloc[-1] > data['value'].iloc[0] else "Downward" if trend_strength > 0 else "No Clear Trend"
                    
                    st.metric("Trend Strength", f"{trend_strength:.2f}")
                    st.metric("Trend Direction", trend_direction)
        
        # Additional pattern visuals
        st.subheader("Pattern Visualization")
        
        tab1, tab2, tab3 = st.tabs(["Time Patterns", "Seasonality", "Distribution Over Time"])
        
        with tab1:
            if 'date' in data.columns:
                # Create time-based patterns
                time_pattern_col1, time_pattern_col2 = st.columns(2)
                
                with time_pattern_col1:
                    # Day of week patterns
                    data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
                    day_names = {
                        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
                        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
                    }
                    data['day_name'] = data['day_of_week'].map(day_names)
                    
                    day_data = data.groupby('day_name')['value'].agg(['mean', 'std']).reset_index()
                    
                    # Set correct order of days
                    day_data['day_order'] = day_data['day_name'].map({
                        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
                        'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
                    })
                    day_data = day_data.sort_values('day_order')
                    
                    fig_day = px.bar(
                        day_data,
                        x='day_name',
                        y='mean',
                        error_y='std',
                        title='Day of Week Pattern',
                        labels={'day_name': 'Day', 'mean': 'Average Value', 'std': 'Standard Deviation'}
                    )
                    
                    st.plotly_chart(fig_day, use_container_width=True)
                
                with time_pattern_col2:
                    # Month patterns
                    data['month'] = pd.to_datetime(data['date']).dt.month
                    month_names = {
                        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
                    }
                    data['month_name'] = data['month'].map(month_names)
                    
                    month_data = data.groupby('month_name')['value'].agg(['mean', 'std']).reset_index()
                    
                    # Set correct order of months
                    month_data['month_order'] = month_data['month_name'].map({
                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                    })
                    month_data = month_data.sort_values('month_order')
                    
                    fig_month = px.line(
                        month_data,
                        x='month_name',
                        y='mean',
                        error_y='std',
                        title='Monthly Pattern',
                        labels={'month_name': 'Month', 'mean': 'Average Value', 'std': 'Standard Deviation'},
                        markers=True
                    )
                    
                    st.plotly_chart(fig_month, use_container_width=True)
        
        with tab2:
            if 'date' in data.columns:
                # Seasonal decomposition visual
                try:
                    from statsmodels.tsa.seasonal import seasonal_decompose
                    
                    # Set date as index for decomposition
                    ts_data = data.set_index('date')['value']
                    
                    # Determine period based on pattern_timeframe
                    if pattern_timeframe == "Daily":
                        period = 1
                    elif pattern_timeframe == "Weekly":
                        period = 7
                    elif pattern_timeframe == "Monthly":
                        period = 30
                    elif pattern_timeframe == "Quarterly":
                        period = 90
                    else:  # Yearly
                        period = 365
                    
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
                            rows=4, 
                            cols=1,
                            subplot_titles=("Observed", "Trend", "Seasonal", "Residual"),
                            vertical_spacing=0.1
                        )
                        
                        # Add traces
                        fig.add_trace(
                            go.Scatter(x=result.observed.index, y=result.observed, name="Observed"),
                            row=1, col=1
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=result.trend.index, y=result.trend, name="Trend"),
                            row=2, col=1
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=result.seasonal.index, y=result.seasonal, name="Seasonal"),
                            row=3, col=1
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=result.resid.index, y=result.resid, name="Residual"),
                            row=4, col=1
                        )
                        
                        # Update layout
                        fig.update_layout(
                            height=800,
                            title_text="Seasonal Decomposition",
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"Not enough data for seasonal decomposition with period={period}. Need at least {2*period} data points.")
                
                except Exception as e:
                    st.error(f"Error performing seasonal decomposition: {str(e)}")
                    
                    # Fall back to simpler visualization
                    if 'month' not in data.columns:
                        data['month'] = pd.to_datetime(data['date']).dt.month
                    
                    if 'year' not in data.columns:
                        data['year'] = pd.to_datetime(data['date']).dt.year
                    
                    pivot_data = data.pivot_table(
                        index='month',
                        columns='year',
                        values='value',
                        aggfunc='mean'
                    )
                    
                    fig = px.imshow(
                        pivot_data,
                        labels=dict(x="Year", y="Month", color="Value"),
                        title="Monthly Patterns by Year",
                        color_continuous_scale='Viridis'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Distribution over time
            if 'date' in data.columns:
                data['year_month'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m')
                
                # Create box plot by month
                fig = px.box(
                    data,
                    x='year_month',
                    y='value',
                    title='Value Distribution Over Time',
                    labels={'year_month': 'Month', 'value': 'Value'}
                )
                
                # If too many months, show only some x-axis labels
                if data['year_month'].nunique() > 12:
                    fig.update_layout(
                        xaxis=dict(
                            tickmode='array',
                            tickvals=list(data['year_month'].unique())[::3],
                            ticktext=list(data['year_month'].unique())[::3]
                        )
                    )
                
                st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Correlation Analysis":
        st.header("Correlation Analysis")
        
        if 'value' in data.columns and 'date' in data.columns:
            # Create correlation visuals
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Auto-correlation plot
                try:
                    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
                    import matplotlib.pyplot as plt
                    
                    # Create lag features
                    if 'lag_periods' in locals():
                        for i in range(1, lag_periods + 1):
                            data[f'lag_{i}'] = data['value'].shift(i)
                        
                        # Drop NaN values
                        lag_data = data.dropna()
                        
                        # Calculate correlation
                        if correlation_method == "Pearson":
                            corr_matrix = lag_data[['value'] + [f'lag_{i}' for i in range(1, lag_periods + 1)]].corr(method='pearson')
                        elif correlation_method == "Spearman":
                            corr_matrix = lag_data[['value'] + [f'lag_{i}' for i in range(1, lag_periods + 1)]].corr(method='spearman')
                        else:  # Kendall
                            corr_matrix = lag_data[['value'] + [f'lag_{i}' for i in range(1, lag_periods + 1)]].corr(method='kendall')
                        
                        # Plot correlation heatmap
                        fig = px.imshow(
                            corr_matrix,
                            text_auto=True,
                            title=f"{correlation_method} Correlation Matrix with Lags",
                            color_continuous_scale='RdBu_r',
                            zmin=-1, zmax=1
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    else:
                        # Plot autocorrelation
                        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                        
                        plot_acf(data['value'].dropna(), lags=min(30, len(data)//2), ax=ax1, title="Autocorrelation")
                        plot_pacf(data['value'].dropna(), lags=min(30, len(data)//2), ax=ax2, title="Partial Autocorrelation")
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                
                except Exception as e:
                    st.error(f"Error generating autocorrelation plot: {str(e)}")
                    
                    # Fallback to manual autocorrelation calculation
                    max_lag = min(30, len(data) // 3)
                    autocorr = [data['value'].autocorr(lag=lag) for lag in range(1, max_lag + 1)]
                    
                    fig = px.bar(
                        x=list(range(1, max_lag + 1)),
                        y=autocorr,
                        title="Autocorrelation",
                        labels={'x': 'Lag', 'y': 'Correlation'}
                    )
                    
                    # Add reference lines for significance
                    significance = 1.96 / np.sqrt(len(data))
                    fig.add_hline(y=significance, line_dash="dash", line_color="red")
                    fig.add_hline(y=-significance, line_dash="dash", line_color="red")
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Correlation stats
                st.subheader("Correlation Statistics")
                
                if 'lag_periods' in locals():
                    # Display strongest correlations
                    corr_with_value = corr_matrix['value'].drop('value').sort_values(ascending=False)
                    
                    st.write("Strongest Correlations:")
                    
                    for lag, corr in corr_with_value.items():
                        lag_num = int(lag.split('_')[1])
                        st.metric(f"Lag {lag_num}", f"{corr:.3f}")
                        
                        if abs(corr) > 0.7:
                            st.success(f"Strong correlation with {lag_num} period(s) ago")
                        elif abs(corr) > 0.5:
                            st.info(f"Moderate correlation with {lag_num} period(s) ago")
                
                # Add interpretation
                st.markdown("### Interpretation")
                st.markdown("""
                - **Positive values** indicate that values tend to move in the same direction after the given lag.
                - **Negative values** indicate that values tend to move in opposite directions.
                - Values above/below the red dashed lines are statistically significant.
                """)
            
            # Additional correlation analysis
            st.subheader("Lag Scatter Plot")
            
            if 'lag_periods' in locals():
                # Let user select which lag to plot
                selected_lag = st.selectbox(
                    "Select Lag Period", 
                    options=list(range(1, lag_periods + 1)),
                    index=0
                )
                
                lag_col = f'lag_{selected_lag}'
                
                # Create scatter plot
                fig = px.scatter(
                    lag_data,
                    x=lag_col,
                    y='value',
                    trendline='ols',
                    title=f"Value vs {selected_lag}-Period Lag",
                    labels={lag_col: f'Value (t-{selected_lag})', 'value': 'Value (t)'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add regression stats
                import statsmodels.api as sm
                
                X = sm.add_constant(lag_data[lag_col])
                model = sm.OLS(lag_data['value'], X).fit()
                
                st.write("Regression Statistics:")
                st.code(model.summary().tables[1].as_text())
    
    elif analysis_type == "Trend Decomposition":
        st.header("Trend Decomposition")
        
        if 'date' in data.columns and 'value' in data.columns:
            try:
                from statsmodels.tsa.seasonal import seasonal_decompose
                from plotly.subplots import make_subplots
                
                # Set date as index for decomposition
                ts_data = data.set_index('date')['value']
                
                # Check if we have enough data
                if len(ts_data) >= 2 * period:
                    # Perform decomposition
                    result = seasonal_decompose(
                        ts_data, 
                        model=decomp_model.lower(), 
                        period=period
                    )
                    
                    # Create figure with subplots
                    fig = make_subplots(
                        rows=4, 
                        cols=1,
                        subplot_titles=("Observed", "Trend", "Seasonal", "Residual"),
                        vertical_spacing=0.1
                    )
                    
                    # Add traces
                    fig.add_trace(
                        go.Scatter(x=result.observed.index, y=result.observed, name="Observed"),
                        row=1, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(x=result.trend.index, y=result.trend, name="Trend"),
                        row=2, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(x=result.seasonal.index, y=result.seasonal, name="Seasonal"),
                        row=3, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(x=result.resid.index, y=result.resid, name="Residual"),
                        row=4, col=1
                    )
                    
                    # Update layout
                    fig.update_layout(
                        height=800,
                        title_text=f"{decomp_model} Decomposition (Period={period})",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Analysis of components
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.subheader("Trend")
                        trend_change = ((result.trend.iloc[-1] - result.trend.iloc[0]) / result.trend.iloc[0]) * 100 if result.trend.iloc[0] != 0 else 0
                        trend_direction = "Upward" if trend_change > 0 else "Downward" if trend_change < 0 else "Flat"
                        
                        st.metric("Direction", trend_direction, f"{trend_change:.1f}%")
                        st.metric("Contribution", f"{result.trend.std() / result.observed.std() * 100:.1f}%")
                    
                    with col2:
                        st.subheader("Seasonality")
                        seasonal_strength = result.seasonal.std() / result.observed.std() * 100
                        
                        st.metric("Strength", f"{seasonal_strength:.1f}%")
                        st.metric("Max Effect", f"{result.seasonal.max() - result.seasonal.min():.2f}")
                    
                    with col3:
                        st.subheader("Residual")
                        residual_size = result.resid.std() / result.observed.std() * 100
                        
                        st.metric("Noise Level", f"{residual_size:.1f}%")
                        st.metric("Analysis Quality", "Good" if residual_size < 30 else "Fair" if residual_size < 50 else "Poor")
                    
                    # Seasonal pattern
                    st.subheader("Seasonal Pattern")
                    
                    # Group seasonal component by time period
                    if period == 7:  # Weekly
                        result_reset = result.seasonal.reset_index()
                        result_reset['day_of_week'] = result_reset['date'].dt.dayofweek
                        seasonal_pattern = result_reset.groupby('day_of_week')['seasonal'].mean()
                        
                        day_names = {
                            0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
                            3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
                        }
                        
                        seasonal_pattern.index = [day_names[i] for i in seasonal_pattern.index]
                        
                        fig = px.bar(
                            x=seasonal_pattern.index,
                            y=seasonal_pattern.values,
                            title="Average Seasonal Effect by Day of Week",
                            labels={'x': 'Day', 'y': 'Effect'}
                        )
                        
                    elif period == 30 or period == 31:  # Monthly
                        result_reset = result.seasonal.reset_index()
                        result_reset['day_of_month'] = result_reset['date'].dt.day
                        seasonal_pattern = result_reset.groupby('day_of_month')['seasonal'].mean()
                        
                        fig = px.line(
                            x=seasonal_pattern.index,
                            y=seasonal_pattern.values,
                            title="Average Seasonal Effect by Day of Month",
                            labels={'x': 'Day', 'y': 'Effect'},
                            markers=True
                        )
                        
                    elif period == 365 or period == 366:  # Yearly
                        result_reset = result.seasonal.reset_index()
                        result_reset['day_of_year'] = result_reset['date'].dt.dayofyear
                        seasonal_pattern = result_reset.groupby('day_of_year')['seasonal'].mean()
                        
                        # Smooth for better visualization
                        from scipy.signal import savgol_filter
                        if len(seasonal_pattern) > 10:
                            smoothed = savgol_filter(seasonal_pattern.values, min(21, len(seasonal_pattern) // 2 * 2 + 1), 3)
                            
                            fig = px.line(
                                x=seasonal_pattern.index,
                                y=smoothed,
                                title="Average Seasonal Effect by Day of Year",
                                labels={'x': 'Day', 'y': 'Effect'}
                            )
                        else:
                            fig = px.line(
                                x=seasonal_pattern.index,
                                y=seasonal_pattern.values,
                                title="Average Seasonal Effect by Day of Year",
                                labels={'x': 'Day', 'y': 'Effect'}
                            )
                    
                    else:  # Generic
                        # Just show one full period
                        one_period = result.seasonal.iloc[:period]
                        
                        fig = px.line(
                            x=list(range(len(one_period))),
                            y=one_period.values,
                            title=f"Seasonal Pattern (One Period = {period} units)",
                            labels={'x': 'Position in Period', 'y': 'Effect'},
                            markers=True
                        )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning(f"Not enough data for decomposition with period={period}. Need at least {2*period} data points.")
                    
                    # Show simple trend line instead
                    fig = px.scatter(
                        data,
                        x='date',
                        y='value',
                        trendline='ols',
                        title="Trend Analysis",
                        labels={'date': 'Date', 'value': 'Value'}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            except Exception as e:
                st.error(f"Error performing decomposition: {str(e)}")
                
                # Fallback visualization
                st.subheader("Simple Trend Analysis")
                
                # Calculate rolling statistics
                window_size = max(3, len(data) // 10)
                data['rolling_mean'] = data['value'].rolling(window=window_size).mean()
                data['rolling_std'] = data['value'].rolling(window=window_size).std()
                
                fig = go.Figure()
                
                # Add original data
                fig.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['value'],
                        mode='lines',
                        name='Original',
                        line=dict(color='blue')
                    )
                )
                
                # Add rolling mean
                fig.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['rolling_mean'],
                        mode='lines',
                        name=f'Trend (MA {window_size})',
                        line=dict(color='red', width=2)
                    )
                )
                
                # Add confidence intervals
                fig.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['rolling_mean'] + 2*data['rolling_std'],
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    )
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['rolling_mean'] - 2*data['rolling_std'],
                        mode='lines',
                        line=dict(width=0),
                        fillcolor='rgba(255, 0, 0, 0.1)',
                        fill='tonexty',
                        name='Confidence Interval'
                    )
                )
                
                fig.update_layout(
                    title=f"Trend with {window_size}-Period Moving Average",
                    xaxis_title='Date',
                    yaxis_title='Value'
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Anomaly Detection":
        st.header("Anomaly Detection")
        
        if 'value' in data.columns:
            # Apply selected anomaly detection method
            if anomaly_method == "Z-Score":
                # Calculate Z-scores
                mean = data['value'].mean()
                std = data['value'].std()
                data['z_score'] = (data['value'] - mean) / std
                
                # Identify anomalies
                data['is_anomaly'] = abs(data['z_score']) > threshold
                anomalies = data[data['is_anomaly']]
                
                # Anomaly score is Z-score
                data['anomaly_score'] = abs(data['z_score'])
            
            elif anomaly_method == "IQR":
                # Calculate IQR
                q1 = data['value'].quantile(0.25)
                q3 = data['value'].quantile(0.75)
                iqr = q3 - q1
                
                # Calculate bounds
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr
                
                # Identify anomalies
                data['is_anomaly'] = (data['value'] < lower_bound) | (data['value'] > upper_bound)
                anomalies = data[data['is_anomaly']]
                
                # Anomaly score is distance from bounds divided by IQR
                data['distance_from_bound'] = np.maximum(0, lower_bound - data['value']) + np.maximum(0, data['value'] - upper_bound)
                data['anomaly_score'] = data['distance_from_bound'] / iqr
            
            elif anomaly_method == "Moving Average":
                # Calculate moving average and standard deviation
                window_size = max(3, len(data) // 10)
                data['ma'] = data['value'].rolling(window=window_size, center=True).mean()
                data['ma_std'] = data['value'].rolling(window=window_size, center=True).std()
                
                # For the first and last few points where rolling creates NaN
                data['ma'] = data['ma'].fillna(data['value'])
                data['ma_std'] = data['ma_std'].fillna(data['value'].std())
                
                # Calculate deviation from moving average
                data['deviation'] = abs(data['value'] - data['ma'])
                
                # Identify anomalies
                data['is_anomaly'] = data['deviation'] > threshold * data['ma_std']
                anomalies = data[data['is_anomaly']]
                
                # Anomaly score is deviation in terms of standard deviations
                data['anomaly_score'] = data['deviation'] / data['ma_std']
            
            # Count anomalies
            anomaly_count = len(anomalies)
            anomaly_percent = (anomaly_count / len(data)) * 100
            
            # Display summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Anomalies", anomaly_count)
            
            with col2:
                st.metric("Anomaly Percentage", f"{anomaly_percent:.2f}%")
            
            with col3:
                if anomaly_count > 0:
                    max_anomaly = data.loc[data['anomaly_score'].idxmax()]
                    st.metric("Max Anomaly Score", f"{max_anomaly['anomaly_score']:.2f}")
            
            # Plot with anomalies highlighted
            if 'date' in data.columns:
                fig = go.Figure()
                
                # Add normal data
                fig.add_trace(
                    go.Scatter(
                        x=data[~data['is_anomaly']]['date'],
                        y=data[~data['is_anomaly']]['value'],
                        mode='lines',
                        name='Normal Data',
                        line=dict(color='blue')
                    )
                )
                
                # Add anomalies
                fig.add_trace(
                    go.Scatter(
                        x=anomalies['date'],
                        y=anomalies['value'],
                        mode='markers',
                        name='Anomalies',
                        marker=dict(
                            color='red',
                            size=10,
                            line=dict(color='black', width=1)
                        )
                    )
                )
                
                # Add thresholds if using Moving Average
                if anomaly_method == "Moving Average":
                    fig.add_trace(
                        go.Scatter(
                            x=data['date'],
                            y=data['ma'] + threshold * data['ma_std'],
                            mode='lines',
                            line=dict(dash='dash', color='orange', width=1),
                            name='Upper Threshold'
                        )
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=data['date'],
                            y=data['ma'] - threshold * data['ma_std'],
                            mode='lines',
                            line=dict(dash='dash', color='orange', width=1),
                            name='Lower Threshold'
                        )
                    )
                
                fig.update_layout(
                    title=f"Anomaly Detection using {anomaly_method} (Threshold={threshold})",
                    xaxis_title='Date',
                    yaxis_title='Value'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Show anomaly table
            if anomaly_count > 0:
                st.subheader("Anomaly Details")
                
                # Format for display
                display_columns = ['date', 'value', 'anomaly_score']
                display_columns = [col for col in display_columns if col in anomalies.columns]
                
                # Sort by anomaly score
                anomalies_display = anomalies[display_columns].sort_values('anomaly_score', ascending=False)
                
                # Rename columns for display
                anomalies_display = anomalies_display.rename(columns={
                    'date': 'Date',
                    'value': 'Value',
                    'anomaly_score': 'Anomaly Score'
                })
                
                st.dataframe(anomalies_display, use_container_width=True)
            
            # Distribution of anomalies
            if anomaly_count > 0 and 'date' in data.columns:
                st.subheader("Anomaly Distribution")
                
                # Group by month to see when anomalies occur
                if 'month' not in data.columns:
                    data['month'] = pd.to_datetime(data['date']).dt.month
                if 'year' not in data.columns:
                    data['year'] = pd.to_datetime(data['date']).dt.year
                data['year_month'] = data['year'].astype(str) + '-' + data['month'].astype(str).str.zfill(2)
                
                # Count anomalies by month
                anomaly_by_month = data.groupby('year_month')['is_anomaly'].sum().reset_index()
                total_by_month = data.groupby('year_month').size().reset_index(name='total')
                
                monthly_stats = pd.merge(anomaly_by_month, total_by_month, on='year_month')
                monthly_stats['percentage'] = (monthly_stats['is_anomaly'] / monthly_stats['total']) * 100
                
                fig = px.bar(
                    monthly_stats,
                    x='year_month',
                    y='is_anomaly',
                    title='Anomalies by Month',
                    labels={'year_month': 'Month', 'is_anomaly': 'Number of Anomalies'}
                )
                
                # If too many months, show only some x-axis labels
                if monthly_stats['year_month'].nunique() > 12:
                    fig.update_layout(
                        xaxis=dict(
                            tickmode='array',
                            tickvals=list(monthly_stats['year_month'].unique())[::3],
                            ticktext=list(monthly_stats['year_month'].unique())[::3]
                        )
                    )
                
                st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Comparative Analysis":
        st.header("Comparative Analysis")
        
        if 'compare_by' in locals():
            # Prepare data for comparison
            if compare_by in data.columns:
                # Direct comparison by existing column
                group_col = compare_by
            else:
                # Create grouping based on time periods
                if compare_by == "Month":
                    data['month'] = pd.to_datetime(data['date']).dt.month
                    month_names = {
                        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
                    }
                    data['month_name'] = data['month'].map(month_names)
                    group_col = 'month_name'
                    
                    # Set correct order for plotting
                    order_dict = {name: idx for idx, name in month_names.items()}
                
                elif compare_by == "Quarter":
                    data['quarter'] = pd.to_datetime(data['date']).dt.quarter
                    data['quarter_name'] = 'Q' + data['quarter'].astype(str)
                    group_col = 'quarter_name'
                    
                    # Set correct order for plotting
                    order_dict = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
                
                elif compare_by == "Year":
                    data['year'] = pd.to_datetime(data['date']).dt.year
                    group_col = 'year'
                    
                    # Set correct order for plotting
                    order_dict = {year: i for i, year in enumerate(sorted(data['year'].unique()))}
                
                elif compare_by == "Day of Week":
                    data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
                    day_names = {
                        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
                        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
                    }
                    data['day_name'] = data['day_of_week'].map(day_names)
                    group_col = 'day_name'
                    
                    # Set correct order for plotting
                    order_dict = {name: idx for idx, name in day_names.items()}
            
            # Create comparison visualizations
            st.subheader(f"Comparison by {compare_by}")
            
            # Aggregate data
            agg_data = data.groupby(group_col)['value'].agg(['mean', 'median', 'std', 'min', 'max', 'count']).reset_index()
            
            # Add coefficient of variation
            agg_data['cv'] = (agg_data['std'] / agg_data['mean']) * 100
            
            # Sort by custom order if available
            if 'order_dict' in locals():
                agg_data['sort_order'] = agg_data[group_col].map(order_dict)
                agg_data = agg_data.sort_values('sort_order')
            
            # Display comparison chart
            chart_type = st.selectbox(
                "Chart Type",
                options=["Bar", "Line", "Box Plot", "Strip Plot"],
                index=0
            )
            
            if chart_type == "Bar":
                # Bar chart comparison
                fig = px.bar(
                    agg_data,
                    x=group_col,
                    y='mean',
                    error_y='std',
                    title=f"Average Value by {compare_by}",
                    labels={group_col: compare_by, 'mean': 'Average Value', 'std': 'Standard Deviation'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Line":
                # Line chart comparison
                fig = px.line(
                    agg_data,
                    x=group_col,
                    y='mean',
                    error_y='std',
                    title=f"Average Value by {compare_by}",
                    labels={group_col: compare_by, 'mean': 'Average Value', 'std': 'Standard Deviation'},
                    markers=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Box Plot":
                # Box plot comparison
                fig = px.box(
                    data,
                    x=group_col,
                    y='value',
                    title=f"Value Distribution by {compare_by}",
                    labels={group_col: compare_by, 'value': 'Value'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Strip Plot":
                # Strip plot comparison
                fig = px.strip(
                    data,
                    x=group_col,
                    y='value',
                    title=f"Value Distribution by {compare_by}",
                    labels={group_col: compare_by, 'value': 'Value'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics table
            st.subheader("Comparison Statistics")
            
            # Format table for display
            stats_display = agg_data[[group_col, 'mean', 'median', 'std', 'min', 'max', 'cv', 'count']]
            stats_display = stats_display.rename(columns={
                group_col: compare_by,
                'mean': 'Mean',
                'median': 'Median',
                'std': 'Std Dev',
                'min': 'Min',
                'max': 'Max',
                'cv': 'CV (%)',
                'count': 'Count'
            })
            
            st.dataframe(stats_display.round(2), use_container_width=True)
            
            # Time series by group
            if 'date' in data.columns:
                st.subheader("Time Series by Group")
                
                # Select groups to display
                if agg_data[group_col].nunique() <= 10:
                    selected_groups = st.multiselect(
                        f"Select {compare_by} to display",
                        options=agg_data[group_col].unique(),
                        default=agg_data[group_col].unique()[:3]  # Default to first 3
                    )
                else:
                    # If too many groups, select top N by count
                    top_groups = agg_data.nlargest(5, 'count')[group_col].tolist()
                    selected_groups = st.multiselect(
                        f"Select {compare_by} to display",
                        options=agg_data[group_col].unique(),
                        default=top_groups
                    )
                
                if selected_groups:
                    # Filter data for selected groups
                    filtered_data = data[data[group_col].isin(selected_groups)]
                    
                    # Create time series plot
                    if len(filtered_data) > 0:
                        # Group by date and category
                        time_freq = st.selectbox(
                            "Time Frequency",
                            options=["Daily", "Weekly", "Monthly"],
                            index=1
                        )
                        
                        # Resample based on selected frequency
                        if time_freq == "Daily":
                            # Daily data - no resampling needed
                            ts_data = filtered_data.copy()
                        elif time_freq == "Weekly":
                            # Add week column
                            filtered_data['week'] = pd.to_datetime(filtered_data['date']).dt.isocalendar().week
                            filtered_data['year'] = pd.to_datetime(filtered_data['date']).dt.isocalendar().year
                            filtered_data['year_week'] = filtered_data['year'].astype(str) + '-W' + filtered_data['week'].astype(str).str.zfill(2)
                            
                            # Group by week and category
                            ts_data = filtered_data.groupby(['year_week', group_col])['value'].mean().reset_index()
                        else:  # Monthly
                            # Add month column
                            filtered_data['month'] = pd.to_datetime(filtered_data['date']).dt.month
                            filtered_data['year'] = pd.to_datetime(filtered_data['date']).dt.year
                            filtered_data['year_month'] = filtered_data['year'].astype(str) + '-' + filtered_data['month'].astype(str).str.zfill(2)
                            
                            # Group by month and category
                            ts_data = filtered_data.groupby(['year_month', group_col])['value'].mean().reset_index()
                        
                        # Create time series plot
                        if time_freq == "Daily":
                            fig = px.line(
                                ts_data,
                                x='date',
                                y='value',
                                color=group_col,
                                title=f"Time Series by {compare_by}",
                                labels={'date': 'Date', 'value': 'Value', group_col: compare_by}
                            )
                        elif time_freq == "Weekly":
                            fig = px.line(
                                ts_data,
                                x='year_week',
                                y='value',
                                color=group_col,
                                title=f"Weekly Time Series by {compare_by}",
                                labels={'year_week': 'Week', 'value': 'Value', group_col: compare_by},
                                markers=True
                            )
                        else:  # Monthly
                            fig = px.line(
                                ts_data,
                                x='year_month',
                                y='value',
                                color=group_col,
                                title=f"Monthly Time Series by {compare_by}",
                                labels={'year_month': 'Month', 'value': 'Value', group_col: compare_by},
                                markers=True
                            )
                        
                        st.plotly_chart(fig, use_container_width=True)
