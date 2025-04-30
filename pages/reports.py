import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64

# Import custom modules
from data_processor import process_data, filter_data
from visualization import create_visualization
from forecasting import forecast_trend
from utils import format_large_number, export_data

st.title("Custom Reports")
st.subheader("Create and share visualized insights")

# Check if data is loaded
if 'current_data' not in st.session_state or st.session_state.current_data is None:
    st.info("Please load data from the home page first")
    
    # Show sample report images
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://images.unsplash.com/photo-1495592822108-9e6261896da8", caption="Data Visualization Report")
    with col2:
        st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f", caption="Business Intelligence Dashboard")
    
    st.markdown("""
    This page allows you to create custom reports:
    
    - **Report Templates**: Choose from multiple report layouts
    - **Visualization Selection**: Pick the charts and insights to include
    - **Export Options**: Share reports in multiple formats
    - **Scheduled Reports**: Set up automated report generation
    - **Custom Branding**: Add your logo and customize report appearance
    
    Please load a dataset from the home page to get started.
    """)
else:
    # Get the current data
    data = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data
    
    # Sidebar for report options
    with st.sidebar:
        st.header("Report Options")
        
        report_template = st.selectbox(
            "Report Template",
            options=["Executive Summary", "Detailed Analysis", "KPI Dashboard", "Trend Report", "Custom"],
            index=0
        )
        
        time_period = st.selectbox(
            "Time Period",
            options=["All Data", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "Custom"],
            index=0
        )
        
        if time_period == "Custom":
            # Get min and max dates from data
            min_date = data['date'].min()
            max_date = data['date'].max()
            
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
                filtered_data = filter_data(data, start_date, end_date)
                data = filtered_data
        elif time_period != "All Data":
            # Filter data based on selected time period
            end_date = data['date'].max()
            
            if time_period == "Last 7 Days":
                start_date = end_date - timedelta(days=7)
            elif time_period == "Last 30 Days":
                start_date = end_date - timedelta(days=30)
            elif time_period == "Last 90 Days":
                start_date = end_date - timedelta(days=90)
            elif time_period == "Last Year":
                start_date = end_date - timedelta(days=365)
            
            filtered_data = filter_data(data, start_date, end_date)
            data = filtered_data
        
        # Visualization options
        st.header("Visualizations to Include")
        
        include_trend = st.checkbox("Trend Analysis", value=True)
        include_forecast = st.checkbox("Forecast", value=True)
        include_distribution = st.checkbox("Distribution Analysis", value=True)
        include_comparison = st.checkbox("Comparison", value=True)
        include_statistics = st.checkbox("Statistical Summary", value=True)
        
        # Report format options
        st.header("Export Options")
        
        report_format = st.selectbox(
            "Report Format",
            options=["Interactive HTML", "PDF", "Excel", "Image"],
            index=0
        )
        
        include_data_table = st.checkbox("Include Data Table", value=True)
        
        # Generate report button
        generate_report = st.button("Generate Report", key="generate_report_button")
    
    # Main content area - Report Builder
    st.header(f"{report_template} Report")
    
    if time_period != "All Data":
        st.subheader(f"Period: {time_period}")
    
    # Display report based on template and options selected
    if report_template == "Executive Summary":
        # Executive summary layout
        
        # Key metrics section
        st.subheader("Key Metrics")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            if 'value' in data.columns:
                current_value = data['value'].iloc[-1]
                previous_value = data['value'].iloc[-2] if len(data) > 1 else 0
                pct_change = ((current_value - previous_value) / previous_value) * 100 if previous_value != 0 else 0
                
                st.metric(
                    "Current Value", 
                    f"{current_value:.2f}",
                    f"{pct_change:.1f}%"
                )
        
        with metric_col2:
            if 'value' in data.columns:
                avg_value = data['value'].mean()
                st.metric("Average Value", f"{avg_value:.2f}")
        
        with metric_col3:
            if 'value' in data.columns:
                trend_direction = "Up" if data['value'].iloc[-1] > data['value'].iloc[0] else "Down"
                trend_change = ((data['value'].iloc[-1] - data['value'].iloc[0]) / data['value'].iloc[0]) * 100 if data['value'].iloc[0] != 0 else 0
                
                st.metric(
                    "Overall Trend", 
                    trend_direction,
                    f"{trend_change:.1f}%"
                )
        
        with metric_col4:
            # Records count or another relevant metric
            st.metric("Total Records", format_large_number(len(data)))
        
        # Main visualization
        if include_trend:
            st.subheader("Trend Analysis")
            
            fig_trend = create_visualization(
                data,
                visualization_type='trend',
                chart_type='line'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Forecast if requested
        if include_forecast and 'forecast_data' in st.session_state and st.session_state.forecast_data is not None:
            st.subheader("Forecast")
            
            # Create combined plot of historical and forecast data
            fig_forecast = go.Figure()
            
            # Add historical data
            fig_forecast.add_trace(
                go.Scatter(
                    x=data['date'],
                    y=data['value'],
                    mode='lines',
                    name='Historical Data',
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
            
            # Add confidence intervals if available
            if 'upper' in st.session_state.forecast_data.columns and 'lower' in st.session_state.forecast_data.columns:
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
                title='Historical Data and Forecast',
                xaxis_title='Date',
                yaxis_title='Value',
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Summary statistics if requested
        if include_statistics:
            st.subheader("Statistical Summary")
            
            stat_col1, stat_col2 = st.columns(2)
            
            with stat_col1:
                # Display basic statistics
                if 'value' in data.columns:
                    stats = data['value'].describe()
                    
                    st.write("Value Statistics:")
                    st.write(f"Count: {stats['count']:.0f}")
                    st.write(f"Mean: {stats['mean']:.2f}")
                    st.write(f"Std Dev: {stats['std']:.2f}")
                    st.write(f"Min: {stats['min']:.2f}")
                    st.write(f"Max: {stats['max']:.2f}")
            
            with stat_col2:
                # Display percentiles
                if 'value' in data.columns:
                    st.write("Percentiles:")
                    st.write(f"25%: {stats['25%']:.2f}")
                    st.write(f"50% (Median): {stats['50%']:.2f}")
                    st.write(f"75%: {stats['75%']:.2f}")
                    
                    # Calculate additional statistics
                    skewness = data['value'].skew()
                    kurtosis = data['value'].kurtosis()
                    
                    st.write(f"Skewness: {skewness:.2f}")
                    st.write(f"Kurtosis: {kurtosis:.2f}")
    
    elif report_template == "Detailed Analysis":
        # Detailed analysis layout
        
        # Overview section
        st.subheader("Data Overview")
        
        overview_col1, overview_col2 = st.columns([2, 1])
        
        with overview_col1:
            # Main trend visualization
            fig_main = create_visualization(
                data,
                visualization_type='trend',
                chart_type='line'
            )
            
            st.plotly_chart(fig_main, use_container_width=True)
        
        with overview_col2:
            # Key statistics
            if 'value' in data.columns:
                stats = data['value'].describe()
                
                st.write("Summary Statistics:")
                for stat, value in stats.items():
                    st.write(f"**{stat}:** {value:.2f}" if isinstance(value, float) else f"**{stat}:** {value}")
                
                # Additional metrics
                first_value = data['value'].iloc[0]
                last_value = data['value'].iloc[-1]
                change = last_value - first_value
                pct_change = (change / first_value) * 100 if first_value != 0 else 0
                
                st.write(f"**Total Change:** {change:.2f} ({pct_change:.1f}%)")
                
                # Volatility
                volatility = data['value'].std() / data['value'].mean() * 100
                st.write(f"**Volatility:** {volatility:.1f}%")
        
        # Trend analysis section if requested
        if include_trend:
            st.subheader("Advanced Trend Analysis")
            
            trend_tabs = st.tabs(["Time Series", "Seasonality", "Moving Averages"])
            
            with trend_tabs[0]:
                # Time series with annotations for key events
                fig_ts = px.line(
                    data,
                    x='date',
                    y='value',
                    title='Time Series Analysis',
                    labels={'date': 'Date', 'value': 'Value'}
                )
                
                # Find local maxima and minima for annotations
                from scipy.signal import find_peaks
                
                if len(data) > 10:
                    peaks, _ = find_peaks(data['value'], distance=max(5, len(data)//10))
                    troughs, _ = find_peaks(-data['value'], distance=max(5, len(data)//10))
                    
                    # Add peak annotations
                    for peak in peaks[:5]:  # Limit to top 5
                        fig_ts.add_annotation(
                            x=data['date'].iloc[peak],
                            y=data['value'].iloc[peak],
                            text="Peak",
                            showarrow=True,
                            arrowhead=1
                        )
                    
                    # Add trough annotations
                    for trough in troughs[:5]:  # Limit to top 5
                        fig_ts.add_annotation(
                            x=data['date'].iloc[trough],
                            y=data['value'].iloc[trough],
                            text="Trough",
                            showarrow=True,
                            arrowhead=1
                        )
                
                st.plotly_chart(fig_ts, use_container_width=True)
            
            with trend_tabs[1]:
                # Seasonality analysis
                try:
                    # Group by day of week
                    data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
                    day_names = {
                        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
                        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
                    }
                    data['day_name'] = data['day_of_week'].map(day_names)
                    
                    # Group by month
                    data['month'] = pd.to_datetime(data['date']).dt.month
                    month_names = {
                        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
                    }
                    data['month_name'] = data['month'].map(month_names)
                    
                    # Create seasonality plots
                    seasonal_col1, seasonal_col2 = st.columns(2)
                    
                    with seasonal_col1:
                        # Day of week seasonality
                        day_data = data.groupby('day_name')['value'].mean().reset_index()
                        
                        # Set correct order of days
                        day_data['day_order'] = day_data['day_name'].map({
                            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
                            'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
                        })
                        day_data = day_data.sort_values('day_order')
                        
                        fig_day = px.bar(
                            day_data,
                            x='day_name',
                            y='value',
                            title='Day of Week Pattern',
                            labels={'day_name': 'Day', 'value': 'Average Value'}
                        )
                        
                        st.plotly_chart(fig_day, use_container_width=True)
                    
                    with seasonal_col2:
                        # Monthly seasonality
                        month_data = data.groupby('month_name')['value'].mean().reset_index()
                        
                        # Set correct order of months
                        month_data['month_order'] = month_data['month_name'].map({
                            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                        })
                        month_data = month_data.sort_values('month_order')
                        
                        fig_month = px.line(
                            month_data,
                            x='month_name',
                            y='value',
                            title='Monthly Pattern',
                            labels={'month_name': 'Month', 'value': 'Average Value'},
                            markers=True
                        )
                        
                        st.plotly_chart(fig_month, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Error in seasonality analysis: {str(e)}")
            
            with trend_tabs[2]:
                # Moving averages analysis
                ma_col1, ma_col2 = st.columns([3, 1])
                
                with ma_col1:
                    # Calculate multiple moving averages
                    data['MA7'] = data['value'].rolling(window=7).mean()
                    data['MA30'] = data['value'].rolling(window=30).mean()
                    data['MA90'] = data['value'].rolling(window=90).mean() if len(data) >= 90 else None
                    
                    # Plot moving averages
                    fig_ma = go.Figure()
                    
                    # Add original data
                    fig_ma.add_trace(
                        go.Scatter(
                            x=data['date'],
                            y=data['value'],
                            mode='lines',
                            name='Original',
                            line=dict(color='blue', width=1)
                        )
                    )
                    
                    # Add 7-day MA
                    fig_ma.add_trace(
                        go.Scatter(
                            x=data['date'],
                            y=data['MA7'],
                            mode='lines',
                            name='7-Day MA',
                            line=dict(color='red', width=2)
                        )
                    )
                    
                    # Add 30-day MA
                    fig_ma.add_trace(
                        go.Scatter(
                            x=data['date'],
                            y=data['MA30'],
                            mode='lines',
                            name='30-Day MA',
                            line=dict(color='green', width=2)
                        )
                    )
                    
                    # Add 90-day MA if available
                    if 'MA90' in data.columns and data['MA90'].notna().any():
                        fig_ma.add_trace(
                            go.Scatter(
                                x=data['date'],
                                y=data['MA90'],
                                mode='lines',
                                name='90-Day MA',
                                line=dict(color='purple', width=2)
                            )
                        )
                    
                    fig_ma.update_layout(
                        title='Moving Averages Analysis',
                        xaxis_title='Date',
                        yaxis_title='Value',
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig_ma, use_container_width=True)
                
                with ma_col2:
                    st.write("Moving Averages Interpretation")
                    
                    # Compare short-term vs long-term trends
                    last_ma7 = data['MA7'].iloc[-1] if 'MA7' in data.columns and data['MA7'].notna().any() else None
                    last_ma30 = data['MA30'].iloc[-1] if 'MA30' in data.columns and data['MA30'].notna().any() else None
                    
                    if last_ma7 is not None and last_ma30 is not None:
                        if last_ma7 > last_ma30:
                            st.success("Short-term trend is above long-term trend, indicating potential upward momentum.")
                        elif last_ma7 < last_ma30:
                            st.warning("Short-term trend is below long-term trend, indicating potential downward pressure.")
                        else:
                            st.info("Short-term and long-term trends are aligned.")
                    
                    # Volatility analysis
                    if 'value' in data.columns and 'MA30' in data.columns:
                        # Calculate deviation from MA30
                        data['deviation'] = data['value'] - data['MA30']
                        recent_volatility = data['deviation'].iloc[-30:].std() if len(data) >= 30 else data['deviation'].std()
                        overall_volatility = data['deviation'].std()
                        
                        if recent_volatility < overall_volatility * 0.8:
                            st.success("Recent volatility is lower than historical levels.")
                        elif recent_volatility > overall_volatility * 1.2:
                            st.warning("Recent volatility is higher than historical levels.")
                        else:
                            st.info("Volatility remains consistent with historical patterns.")
        
        # Distribution analysis if requested
        if include_distribution:
            st.subheader("Distribution Analysis")
            
            dist_col1, dist_col2 = st.columns(2)
            
            with dist_col1:
                # Histogram
                fig_hist = px.histogram(
                    data,
                    x='value',
                    nbins=30,
                    title='Value Distribution',
                    labels={'value': 'Value', 'count': 'Frequency'}
                )
                
                fig_hist.update_layout(showlegend=False)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with dist_col2:
                # Box plot by time period (month or quarter)
                if len(data) >= 90:  # If enough data, group by quarter
                    if 'quarter' not in data.columns:
                        data['quarter'] = pd.to_datetime(data['date']).dt.quarter
                        data['year'] = pd.to_datetime(data['date']).dt.year
                        data['year_quarter'] = data['year'].astype(str) + '-Q' + data['quarter'].astype(str)
                    
                    fig_box = px.box(
                        data,
                        x='year_quarter',
                        y='value',
                        title='Value Distribution by Quarter',
                        labels={'year_quarter': 'Quarter', 'value': 'Value'}
                    )
                else:  # If less data, group by month
                    if 'month' not in data.columns:
                        data['month'] = pd.to_datetime(data['date']).dt.month
                        data['year'] = pd.to_datetime(data['date']).dt.year
                        data['year_month'] = data['year'].astype(str) + '-' + data['month'].astype(str).str.zfill(2)
                    
                    fig_box = px.box(
                        data,
                        x='year_month',
                        y='value',
                        title='Value Distribution by Month',
                        labels={'year_month': 'Month', 'value': 'Value'}
                    )
                
                st.plotly_chart(fig_box, use_container_width=True)
        
        # Forecast section if requested
        if include_forecast and 'forecast_data' in st.session_state and st.session_state.forecast_data is not None:
            st.subheader("Detailed Forecast Analysis")
            
            forecast_data = st.session_state.forecast_data
            
            # Forecast visualization
            fig_forecast = go.Figure()
            
            # Add historical data
            fig_forecast.add_trace(
                go.Scatter(
                    x=data['date'],
                    y=data['value'],
                    mode='lines',
                    name='Historical Data',
                    line=dict(color='blue')
                )
            )
            
            # Add forecast data
            fig_forecast.add_trace(
                go.Scatter(
                    x=forecast_data['date'],
                    y=forecast_data['forecast'],
                    mode='lines',
                    name='Forecast',
                    line=dict(dash='dash', color='red')
                )
            )
            
            # Add confidence intervals if available
            if 'upper' in forecast_data.columns and 'lower' in forecast_data.columns:
                fig_forecast.add_trace(
                    go.Scatter(
                        x=forecast_data['date'],
                        y=forecast_data['upper'],
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    )
                )
                fig_forecast.add_trace(
                    go.Scatter(
                        x=forecast_data['date'],
                        y=forecast_data['lower'],
                        mode='lines',
                        line=dict(width=0),
                        fillcolor='rgba(255, 0, 0, 0.2)',
                        fill='tonexty',
                        name='Confidence Interval'
                    )
                )
            
            fig_forecast.update_layout(
                title='Forecast with Confidence Intervals',
                xaxis_title='Date',
                yaxis_title='Value',
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Forecast statistics
            forecast_stats_col1, forecast_stats_col2 = st.columns(2)
            
            with forecast_stats_col1:
                # Basic forecast statistics
                st.write("Forecast Statistics:")
                st.write(f"Forecast Periods: {len(forecast_data)}")
                st.write(f"Average Forecast: {forecast_data['forecast'].mean():.2f}")
                st.write(f"Minimum Forecast: {forecast_data['forecast'].min():.2f}")
                st.write(f"Maximum Forecast: {forecast_data['forecast'].max():.2f}")
                
                # Calculate trend
                first_forecast = forecast_data['forecast'].iloc[0]
                last_forecast = forecast_data['forecast'].iloc[-1]
                forecast_change = last_forecast - first_forecast
                forecast_pct_change = (forecast_change / first_forecast) * 100 if first_forecast != 0 else 0
                
                st.write(f"Forecast Trend: {forecast_change:.2f} ({forecast_pct_change:.1f}%)")
            
            with forecast_stats_col2:
                # Confidence interval information if available
                if 'upper' in forecast_data.columns and 'lower' in forecast_data.columns:
                    # Calculate average interval width
                    interval_width = (forecast_data['upper'] - forecast_data['lower']).mean()
                    relative_width = interval_width / forecast_data['forecast'].mean() * 100
                    
                    st.write("Confidence Interval Information:")
                    st.write(f"Average Interval Width: {interval_width:.2f}")
                    st.write(f"Relative Width: {relative_width:.1f}%")
                    
                    # Interval growth
                    first_width = forecast_data['upper'].iloc[0] - forecast_data['lower'].iloc[0]
                    last_width = forecast_data['upper'].iloc[-1] - forecast_data['lower'].iloc[-1]
                    width_change = ((last_width / first_width) - 1) * 100 if first_width != 0 else 0
                    
                    st.write(f"Interval Growth: {width_change:.1f}%")
                    
                    # Uncertainty assessment
                    if relative_width < 20:
                        st.success("Low forecast uncertainty")
                    elif relative_width < 50:
                        st.info("Moderate forecast uncertainty")
                    else:
                        st.warning("High forecast uncertainty")
    
    elif report_template == "KPI Dashboard":
        # KPI Dashboard layout
        
        # Title and description
        st.markdown("### Key Performance Indicators")
        
        # Main KPI cards in 4 columns
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        with kpi_col1:
            if 'value' in data.columns:
                current_value = data['value'].iloc[-1]
                previous_value = data['value'].iloc[-2] if len(data) > 1 else 0
                pct_change = ((current_value - previous_value) / previous_value) * 100 if previous_value != 0 else 0
                
                st.metric(
                    "Current Value", 
                    f"{current_value:.2f}",
                    f"{pct_change:.1f}%",
                    delta_color="normal"
                )
        
        with kpi_col2:
            if 'value' in data.columns:
                # Calculate period-over-period change
                if len(data) >= 60:  # If we have enough data, compare month-over-month
                    current_month = data.iloc[-30:]['value'].mean()
                    previous_month = data.iloc[-60:-30]['value'].mean()
                    mom_change = ((current_month - previous_month) / previous_month) * 100 if previous_month != 0 else 0
                    
                    st.metric(
                        "Month-over-Month", 
                        f"{current_month:.2f}",
                        f"{mom_change:.1f}%",
                        delta_color="normal"
                    )
                else:  # Otherwise show week-over-week
                    current_week = data.iloc[-7:]['value'].mean() if len(data) >= 7 else data['value'].mean()
                    previous_week = data.iloc[-14:-7]['value'].mean() if len(data) >= 14 else data['value'].mean()
                    wow_change = ((current_week - previous_week) / previous_week) * 100 if previous_week != 0 else 0
                    
                    st.metric(
                        "Week-over-Week", 
                        f"{current_week:.2f}",
                        f"{wow_change:.1f}%",
                        delta_color="normal"
                    )
        
        with kpi_col3:
            if 'value' in data.columns:
                # Calculate volatility (coefficient of variation)
                mean_value = data['value'].mean()
                std_value = data['value'].std()
                cv = (std_value / mean_value) * 100 if mean_value != 0 else 0
                
                # Compare recent volatility to historical
                recent_cv = (data['value'].iloc[-30:].std() / data['value'].iloc[-30:].mean()) * 100 if len(data) >= 30 and data['value'].iloc[-30:].mean() != 0 else cv
                cv_change = recent_cv - cv
                
                st.metric(
                    "Volatility (CV)", 
                    f"{recent_cv:.1f}%",
                    f"{cv_change:.1f}%",
                    delta_color="inverse"  # Lower volatility is generally better
                )
        
        with kpi_col4:
            if 'value' in data.columns:
                # Calculate trend strength using R-squared of linear fit
                import numpy as np
                from scipy import stats
                
                x = np.arange(len(data))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, data['value'])
                r_squared = r_value**2
                
                # Direction of trend
                trend_direction = "Up" if slope > 0 else "Down" if slope < 0 else "Flat"
                
                st.metric(
                    "Trend Strength", 
                    f"{r_squared:.2f}",
                    trend_direction
                )
        
        # Main visualizations
        main_viz_col1, main_viz_col2 = st.columns(2)
        
        with main_viz_col1:
            # Main trend visualization
            if include_trend:
                fig_trend = create_visualization(
                    data,
                    visualization_type='trend',
                    chart_type='line'
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
        
        with main_viz_col2:
            # Distribution or forecast visualization
            if include_distribution:
                fig_dist = create_visualization(
                    data,
                    visualization_type='distribution',
                    chart_type='histogram'
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
            elif include_forecast and 'forecast_data' in st.session_state and st.session_state.forecast_data is not None:
                # Simple forecast visualization
                forecast_data = st.session_state.forecast_data
                
                fig_forecast = go.Figure()
                
                # Add historical data
                fig_forecast.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['value'],
                        mode='lines',
                        name='Historical',
                        line=dict(color='blue')
                    )
                )
                
                # Add forecast data
                fig_forecast.add_trace(
                    go.Scatter(
                        x=forecast_data['date'],
                        y=forecast_data['forecast'],
                        mode='lines',
                        name='Forecast',
                        line=dict(dash='dash', color='red')
                    )
                )
                
                fig_forecast.update_layout(
                    title='Forecast',
                    xaxis_title='Date',
                    yaxis_title='Value',
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Secondary KPIs and visualizations
        secondary_viz_col1, secondary_viz_col2, secondary_viz_col3 = st.columns(3)
        
        with secondary_viz_col1:
            # Period comparison 
            if 'date' in data.columns:
                # Group by month or week depending on data size
                if len(data) >= 90:  # Monthly for larger datasets
                    if 'month' not in data.columns:
                        data['month'] = pd.to_datetime(data['date']).dt.month
                        data['year'] = pd.to_datetime(data['date']).dt.year
                        data['year_month'] = data['year'].astype(str) + '-' + data['month'].astype(str).str.zfill(2)
                    
                    period_data = data.groupby('year_month')['value'].mean().reset_index()
                    x_title = 'Month'
                    title = 'Monthly Average'
                else:  # Weekly for smaller datasets
                    data['week'] = pd.to_datetime(data['date']).dt.isocalendar().week
                    data['year'] = pd.to_datetime(data['date']).dt.isocalendar().year
                    data['year_week'] = data['year'].astype(str) + '-W' + data['week'].astype(str).str.zfill(2)
                    
                    period_data = data.groupby('year_week')['value'].mean().reset_index()
                    x_title = 'Week'
                    title = 'Weekly Average'
                
                fig_period = px.bar(
                    period_data.tail(10),  # Show last 10 periods
                    x='year_month' if 'year_month' in period_data.columns else 'year_week',
                    y='value',
                    title=title,
                    labels={
                        'year_month' if 'year_month' in period_data.columns else 'year_week': x_title, 
                        'value': 'Average Value'
                    }
                )
                
                st.plotly_chart(fig_period, use_container_width=True)
        
        with secondary_viz_col2:
            # Day of week pattern
            if 'date' in data.columns:
                if 'day_of_week' not in data.columns:
                    data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
                    day_names = {
                        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
                        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
                    }
                    data['day_name'] = data['day_of_week'].map(day_names)
                
                day_data = data.groupby('day_name')['value'].mean().reset_index()
                
                # Set correct order of days
                day_data['day_order'] = day_data['day_name'].map({
                    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
                    'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
                })
                day_data = day_data.sort_values('day_order')
                
                fig_day = px.bar(
                    day_data,
                    x='day_name',
                    y='value',
                    title='Day of Week Pattern',
                    labels={'day_name': 'Day', 'value': 'Average Value'}
                )
                
                st.plotly_chart(fig_day, use_container_width=True)
        
        with secondary_viz_col3:
            # Outlier detection
            if 'value' in data.columns:
                # Calculate Z-scores
                mean = data['value'].mean()
                std = data['value'].std()
                data['z_score'] = (data['value'] - mean) / std
                
                # Identify outliers
                threshold = 2.5  # Z-score threshold for outliers
                data['is_outlier'] = abs(data['z_score']) > threshold
                outliers = data[data['is_outlier']]
                
                # Create scatter plot with outliers highlighted
                fig_outliers = go.Figure()
                
                # Add normal data points
                fig_outliers.add_trace(
                    go.Scatter(
                        x=data[~data['is_outlier']]['date'],
                        y=data[~data['is_outlier']]['value'],
                        mode='markers',
                        name='Normal',
                        marker=dict(
                            color='blue',
                            size=5
                        )
                    )
                )
                
                # Add outliers
                if len(outliers) > 0:
                    fig_outliers.add_trace(
                        go.Scatter(
                            x=outliers['date'],
                            y=outliers['value'],
                            mode='markers',
                            name='Outliers',
                            marker=dict(
                                color='red',
                                size=10,
                                line=dict(
                                    color='black',
                                    width=1
                                )
                            )
                        )
                    )
                
                fig_outliers.update_layout(
                    title=f'Outlier Detection (Z-score > {threshold})',
                    xaxis_title='Date',
                    yaxis_title='Value'
                )
                
                st.plotly_chart(fig_outliers, use_container_width=True)
                
                if len(outliers) > 0:
                    st.info(f"Detected {len(outliers)} outliers ({len(outliers)/len(data)*100:.1f}% of data)")
                else:
                    st.success("No significant outliers detected")
        
        # Data table if requested
        if include_data_table:
            st.subheader("Data Table")
            
            # Create a display version of the data
            display_data = data[['date', 'value']].copy()
            display_data['date'] = display_data['date'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(display_data.sort_values('date', ascending=False).head(100), use_container_width=True)
    
    elif report_template == "Trend Report":
        # Trend Report layout
        
        # Header section
        st.markdown("### Trend Analysis Report")
        st.markdown(f"**Period:** {data['date'].min().strftime('%Y-%m-%d')} to {data['date'].max().strftime('%Y-%m-%d')}")
        
        # Main trend visualization
        if include_trend:
            fig_trend = create_visualization(
                data,
                visualization_type='trend',
                chart_type='line'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Trend metrics
        trend_col1, trend_col2, trend_col3, trend_col4 = st.columns(4)
        
        with trend_col1:
            # Overall change
            if 'value' in data.columns:
                first_value = data['value'].iloc[0]
                last_value = data['value'].iloc[-1]
                change = last_value - first_value
                pct_change = (change / first_value) * 100 if first_value != 0 else 0
                
                st.metric(
                    "Overall Change", 
                    f"{change:.2f}",
                    f"{pct_change:.1f}%"
                )
        
        with trend_col2:
            # Trend direction and strength
            if 'value' in data.columns:
                # Calculate trend using linear regression
                import numpy as np
                from scipy import stats
                
                x = np.arange(len(data))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, data['value'])
                
                # Annualized rate of change
                if len(data) > 1:
                    days_elapsed = (data['date'].iloc[-1] - data['date'].iloc[0]).days
                    if days_elapsed > 0:
                        annualized_change = ((1 + pct_change/100) ** (365/days_elapsed) - 1) * 100
                    else:
                        annualized_change = 0
                else:
                    annualized_change = 0
                
                st.metric(
                    "Annual Rate", 
                    f"{annualized_change:.1f}%",
                    "p-value: {:.3f}".format(p_value)
                )
        
        with trend_col3:
            # Volatility
            if 'value' in data.columns:
                mean_value = data['value'].mean()
                std_value = data['value'].std()
                cv = (std_value / mean_value) * 100 if mean_value != 0 else 0
                
                st.metric("Volatility (CV)", f"{cv:.1f}%")
        
        with trend_col4:
            # Consistency
            if 'value' in data.columns and len(data) > 1:
                # Calculate consistency as percentage of days with same direction as overall trend
                diffs = data['value'].diff().dropna()
                positive_days = (diffs > 0).sum()
                negative_days = (diffs < 0).sum()
                total_days = len(diffs)
                
                if change > 0:  # Upward trend
                    consistency = (positive_days / total_days) * 100 if total_days > 0 else 0
                elif change < 0:  # Downward trend
                    consistency = (negative_days / total_days) * 100 if total_days > 0 else 0
                else:  # No change
                    consistency = 0
                
                st.metric("Consistency", f"{consistency:.1f}%")
        
        # Trend components analysis
        st.subheader("Trend Components")
        
        try:
            # Try to decompose the time series
            from statsmodels.tsa.seasonal import seasonal_decompose
            from plotly.subplots import make_subplots
            
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
                    subplot_titles=("Trend Component", "Seasonal Component", "Residual Component"),
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
                    title_text="Time Series Decomposition",
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add component interpretation
                component_col1, component_col2, component_col3 = st.columns(3)
                
                with component_col1:
                    st.subheader("Trend Analysis")
                    
                    # Trend strength
                    trend_variance = result.trend.var()
                    total_variance = result.observed.var()
                    trend_strength = trend_variance / total_variance if total_variance > 0 else 0
                    
                    st.write(f"Trend Strength: {trend_strength:.2f}")
                    
                    # Trend direction
                    trend_start = result.trend.dropna().iloc[0]
                    trend_end = result.trend.dropna().iloc[-1]
                    trend_change = ((trend_end - trend_start) / trend_start) * 100 if trend_start != 0 else 0
                    
                    if trend_change > 5:
                        st.success(f"Strong upward trend: +{trend_change:.1f}%")
                    elif trend_change > 1:
                        st.info(f"Slight upward trend: +{trend_change:.1f}%")
                    elif trend_change < -5:
                        st.error(f"Strong downward trend: {trend_change:.1f}%")
                    elif trend_change < -1:
                        st.warning(f"Slight downward trend: {trend_change:.1f}%")
                    else:
                        st.info("No significant trend detected")
                
                with component_col2:
                    st.subheader("Seasonality Analysis")
                    
                    # Seasonality strength
                    seasonal_variance = result.seasonal.var()
                    seasonal_strength = seasonal_variance / total_variance if total_variance > 0 else 0
                    
                    st.write(f"Seasonal Strength: {seasonal_strength:.2f}")
                    
                    # Seasonal pattern description
                    seasonal_range = result.seasonal.max() - result.seasonal.min()
                    seasonal_impact = (seasonal_range / result.observed.mean()) * 100
                    
                    if seasonal_strength > 0.3:
                        st.success(f"Strong seasonal pattern detected")
                    elif seasonal_strength > 0.1:
                        st.info(f"Moderate seasonal pattern detected")
                    else:
                        st.write("Weak or no seasonal pattern")
                    
                    st.write(f"Seasonal Impact: ±{seasonal_impact/2:.1f}%")
                
                with component_col3:
                    st.subheader("Residual Analysis")
                    
                    # Residual strength (noise)
                    residual_variance = result.resid.var()
                    residual_strength = residual_variance / total_variance if total_variance > 0 else 0
                    
                    st.write(f"Noise Level: {residual_strength:.2f}")
                    
                    # Check for autocorrelation in residuals
                    from statsmodels.stats.diagnostic import acorr_ljungbox
                    
                    try:
                        lb_test = acorr_ljungbox(result.resid.dropna(), lags=[10])
                        p_value = lb_test.iloc[0, 1]  # p-value from Ljung-Box test
                        
                        if p_value < 0.05:
                            st.warning(f"Residuals show autocorrelation (p={p_value:.3f})")
                        else:
                            st.success(f"Residuals appear random (p={p_value:.3f})")
                    except:
                        # Fallback if test fails
                        st.write("Could not perform autocorrelation test on residuals")
                
            else:
                st.warning(f"Not enough data for decomposition with period={period}. Need at least {2*period} data points.")
        
        except Exception as e:
            st.error(f"Error in trend decomposition: {str(e)}")
            
            # Fall back to simple trend analysis
            st.write("Using simple trend analysis instead of decomposition:")
            
            # Calculate rolling mean and standard deviation
            if len(data) >= 7:
                data['rolling_mean'] = data['value'].rolling(window=7).mean()
                data['rolling_std'] = data['value'].rolling(window=7).std()
                
                fig_trend = go.Figure()
                
                # Add original data
                fig_trend.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['value'],
                        mode='lines',
                        name='Original Data',
                        line=dict(color='blue', width=1)
                    )
                )
                
                # Add rolling mean
                fig_trend.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['rolling_mean'],
                        mode='lines',
                        name='Trend (7-day MA)',
                        line=dict(color='red', width=2)
                    )
                )
                
                # Add confidence bands
                fig_trend.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['rolling_mean'] + 2*data['rolling_std'],
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    )
                )
                
                fig_trend.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['rolling_mean'] - 2*data['rolling_std'],
                        mode='lines',
                        line=dict(width=0),
                        fillcolor='rgba(255, 0, 0, 0.1)',
                        fill='tonexty',
                        name='±2σ Band'
                    )
                )
                
                fig_trend.update_layout(
                    title='Trend Analysis with Moving Average',
                    xaxis_title='Date',
                    yaxis_title='Value'
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
        
        # Forecast section if requested
        if include_forecast and 'forecast_data' in st.session_state and st.session_state.forecast_data is not None:
            st.subheader("Forecast Analysis")
            
            forecast_data = st.session_state.forecast_data
            
            # Create combined plot
            fig_forecast = go.Figure()
            
            # Add historical data
            fig_forecast.add_trace(
                go.Scatter(
                    x=data['date'],
                    y=data['value'],
                    mode='lines',
                    name='Historical Data',
                    line=dict(color='blue')
                )
            )
            
            # Add forecast data
            fig_forecast.add_trace(
                go.Scatter(
                    x=forecast_data['date'],
                    y=forecast_data['forecast'],
                    mode='lines',
                    name='Forecast',
                    line=dict(dash='dash', color='red')
                )
            )
            
            # Add confidence intervals if available
            if 'upper' in forecast_data.columns and 'lower' in forecast_data.columns:
                fig_forecast.add_trace(
                    go.Scatter(
                        x=forecast_data['date'],
                        y=forecast_data['upper'],
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    )
                )
                fig_forecast.add_trace(
                    go.Scatter(
                        x=forecast_data['date'],
                        y=forecast_data['lower'],
                        mode='lines',
                        line=dict(width=0),
                        fillcolor='rgba(255, 0, 0, 0.2)',
                        fill='tonexty',
                        name='Confidence Interval'
                    )
                )
            
            fig_forecast.update_layout(
                title='Trend Forecast',
                xaxis_title='Date',
                yaxis_title='Value',
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Forecast interpretation
            st.subheader("Forecast Interpretation")
            
            forecast_col1, forecast_col2 = st.columns(2)
            
            with forecast_col1:
                # Calculate forecast trend
                first_forecast = forecast_data['forecast'].iloc[0]
                last_forecast = forecast_data['forecast'].iloc[-1]
                forecast_change = last_forecast - first_forecast
                forecast_pct_change = (forecast_change / first_forecast) * 100 if first_forecast != 0 else 0
                
                if forecast_pct_change > 10:
                    st.success(f"Strong upward trend forecast: +{forecast_pct_change:.1f}%")
                elif forecast_pct_change > 2:
                    st.info(f"Moderate upward trend forecast: +{forecast_pct_change:.1f}%")
                elif forecast_pct_change < -10:
                    st.error(f"Strong downward trend forecast: {forecast_pct_change:.1f}%")
                elif forecast_pct_change < -2:
                    st.warning(f"Moderate downward trend forecast: {forecast_pct_change:.1f}%")
                else:
                    st.info(f"Stable trend forecast: {forecast_pct_change:.1f}%")
                
                # Forecast average
                forecast_avg = forecast_data['forecast'].mean()
                historical_avg = data['value'].mean()
                avg_change = ((forecast_avg - historical_avg) / historical_avg) * 100 if historical_avg != 0 else 0
                
                st.write(f"Average forecast value: {forecast_avg:.2f} ({avg_change:+.1f}% vs. historical)")
            
            with forecast_col2:
                # Forecast certainty information if available
                if 'upper' in forecast_data.columns and 'lower' in forecast_data.columns:
                    # Calculate average interval width
                    interval_width = (forecast_data['upper'] - forecast_data['lower']).mean()
                    relative_width = interval_width / forecast_data['forecast'].mean() * 100 if forecast_data['forecast'].mean() != 0 else 0
                    
                    if relative_width < 20:
                        st.success(f"High forecast certainty (±{relative_width/2:.1f}%)")
                    elif relative_width < 50:
                        st.info(f"Moderate forecast certainty (±{relative_width/2:.1f}%)")
                    else:
                        st.warning(f"Low forecast certainty (±{relative_width/2:.1f}%)")
                    
                    # Interval growth
                    first_width = forecast_data['upper'].iloc[0] - forecast_data['lower'].iloc[0]
                    last_width = forecast_data['upper'].iloc[-1] - forecast_data['lower'].iloc[-1]
                    width_growth = ((last_width / first_width) - 1) * 100 if first_width != 0 else 0
                    
                    st.write(f"Forecast uncertainty increases by {width_growth:.1f}% over the forecast period")
        
        # Cyclical patterns section
        if include_comparison:
            st.subheader("Cyclical Patterns")
            
            cycle_col1, cycle_col2 = st.columns(2)
            
            with cycle_col1:
                # Day of week pattern
                if 'date' in data.columns:
                    if 'day_of_week' not in data.columns:
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
            
            with cycle_col2:
                # Monthly pattern
                if 'date' in data.columns:
                    if 'month' not in data.columns:
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
    
    elif report_template == "Custom":
        # Custom Report layout - more flexible with user options
        
        # Let the user choose sections to include
        st.subheader("Custom Report Builder")
        
        # Choose sections
        sections = []
        
        if include_trend:
            sections.append("trend_analysis")
        
        if include_forecast:
            sections.append("forecast")
        
        if include_distribution:
            sections.append("distribution")
        
        if include_comparison:
            sections.append("comparison")
        
        if include_statistics:
            sections.append("statistics")
        
        if not sections:
            st.warning("Please select at least one visualization type to include in the report")
        else:
            # Add sections based on user selection
            for section in sections:
                if section == "trend_analysis":
                    st.subheader("Trend Analysis")
                    
                    # Let user choose chart type
                    trend_chart_type = st.selectbox(
                        "Trend Chart Type",
                        options=["Line", "Area", "Bar", "Scatter"],
                        index=0,
                        key="trend_chart_type"
                    )
                    
                    # Create trend visualization
                    fig_trend = create_visualization(
                        data,
                        visualization_type='trend',
                        chart_type=trend_chart_type.lower()
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                    # Add trend metrics
                    if 'value' in data.columns:
                        trend_metrics_col1, trend_metrics_col2, trend_metrics_col3 = st.columns(3)
                        
                        with trend_metrics_col1:
                            first_value = data['value'].iloc[0]
                            last_value = data['value'].iloc[-1]
                            change = last_value - first_value
                            pct_change = (change / first_value) * 100 if first_value != 0 else 0
                            
                            st.metric(
                                "Overall Change", 
                                f"{change:.2f}",
                                f"{pct_change:.1f}%"
                            )
                        
                        with trend_metrics_col2:
                            # Calculate trend using linear regression
                            import numpy as np
                            from scipy import stats
                            
                            x = np.arange(len(data))
                            slope, intercept, r_value, p_value, std_err = stats.linregress(x, data['value'])
                            
                            trend_direction = "Up" if slope > 0 else "Down" if slope < 0 else "Flat"
                            trend_strength = r_value**2  # R-squared
                            
                            st.metric(
                                "Trend Strength", 
                                f"{trend_strength:.2f}",
                                trend_direction
                            )
                        
                        with trend_metrics_col3:
                            volatility = data['value'].std() / data['value'].mean() * 100 if data['value'].mean() != 0 else 0
                            st.metric("Volatility", f"{volatility:.1f}%")
                
                elif section == "forecast":
                    st.subheader("Forecast Analysis")
                    
                    if 'forecast_data' in st.session_state and st.session_state.forecast_data is not None:
                        forecast_data = st.session_state.forecast_data
                        
                        # Create combined plot of historical and forecast data
                        fig_forecast = go.Figure()
                        
                        # Add historical data
                        fig_forecast.add_trace(
                            go.Scatter(
                                x=data['date'],
                                y=data['value'],
                                mode='lines',
                                name='Historical Data',
                                line=dict(color='blue')
                            )
                        )
                        
                        # Add forecast data
                        fig_forecast.add_trace(
                            go.Scatter(
                                x=forecast_data['date'],
                                y=forecast_data['forecast'],
                                mode='lines',
                                name='Forecast',
                                line=dict(dash='dash', color='red')
                            )
                        )
                        
                        # Add confidence intervals if available
                        if 'upper' in forecast_data.columns and 'lower' in forecast_data.columns:
                            fig_forecast.add_trace(
                                go.Scatter(
                                    x=forecast_data['date'],
                                    y=forecast_data['upper'],
                                    mode='lines',
                                    line=dict(width=0),
                                    showlegend=False
                                )
                            )
                            fig_forecast.add_trace(
                                go.Scatter(
                                    x=forecast_data['date'],
                                    y=forecast_data['lower'],
                                    mode='lines',
                                    line=dict(width=0),
                                    fillcolor='rgba(255, 0, 0, 0.2)',
                                    fill='tonexty',
                                    name='Confidence Interval'
                                )
                            )
                        
                        fig_forecast.update_layout(
                            title='Historical Data and Forecast',
                            xaxis_title='Date',
                            yaxis_title='Value',
                            hovermode="x unified"
                        )
                        
                        st.plotly_chart(fig_forecast, use_container_width=True)
                        
                        # Add forecast metrics
                        forecast_metrics_col1, forecast_metrics_col2 = st.columns(2)
                        
                        with forecast_metrics_col1:
                            first_forecast = forecast_data['forecast'].iloc[0]
                            last_forecast = forecast_data['forecast'].iloc[-1]
                            forecast_change = last_forecast - first_forecast
                            forecast_pct_change = (forecast_change / first_forecast) * 100 if first_forecast != 0 else 0
                            
                            st.metric(
                                "Forecast Change", 
                                f"{forecast_change:.2f}",
                                f"{forecast_pct_change:.1f}%"
                            )
                        
                        with forecast_metrics_col2:
                            last_actual = data['value'].iloc[-1]
                            first_forecast = forecast_data['forecast'].iloc[0]
                            transition_gap = first_forecast - last_actual
                            transition_pct = (transition_gap / last_actual) * 100 if last_actual != 0 else 0
                            
                            st.metric(
                                "Forecast vs. Current", 
                                f"{first_forecast:.2f}",
                                f"{transition_pct:.1f}%"
                            )
                    else:
                        st.info("No forecast data available. Generate a forecast on the Forecasting page first.")
                
                elif section == "distribution":
                    st.subheader("Distribution Analysis")
                    
                    # Let user choose distribution chart type
                    dist_chart_type = st.selectbox(
                        "Distribution Chart Type",
                        options=["Histogram", "Box Plot", "Violin Plot", "Scatter"],
                        index=0,
                        key="dist_chart_type"
                    )
                    
                    if dist_chart_type == "Histogram":
                        # Create histogram
                        fig_hist = px.histogram(
                            data,
                            x='value',
                            nbins=30,
                            title='Value Distribution',
                            labels={'value': 'Value', 'count': 'Frequency'}
                        )
                        
                        # Add KDE curve
                        from scipy.stats import gaussian_kde
                        
                        kde = gaussian_kde(data['value'].dropna())
                        x_range = np.linspace(min(data['value']), max(data['value']), 100)
                        y_kde = kde(x_range)
                        
                        # Scale KDE to match histogram height
                        hist_heights = np.histogram(data['value'].dropna(), bins=30)[0]
                        max_hist_height = max(hist_heights)
                        scaling_factor = max_hist_height / max(y_kde)
                        
                        fig_hist.add_trace(
                            go.Scatter(
                                x=x_range,
                                y=y_kde * scaling_factor,
                                mode='lines',
                                name='Density',
                                line=dict(color='red', width=2)
                            )
                        )
                        
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    elif dist_chart_type == "Box Plot":
                        # Create box plot by month or quarter
                        if len(data) >= 90:  # If enough data, group by quarter
                            if 'quarter' not in data.columns:
                                data['quarter'] = pd.to_datetime(data['date']).dt.quarter
                                data['year'] = pd.to_datetime(data['date']).dt.year
                                data['year_quarter'] = data['year'].astype(str) + '-Q' + data['quarter'].astype(str)
                            
                            fig_box = px.box(
                                data,
                                x='year_quarter',
                                y='value',
                                title='Value Distribution by Quarter',
                                labels={'year_quarter': 'Quarter', 'value': 'Value'}
                            )
                        else:  # If less data, group by month
                            if 'month' not in data.columns:
                                data['month'] = pd.to_datetime(data['date']).dt.month
                                data['year'] = pd.to_datetime(data['date']).dt.year
                                data['year_month'] = data['year'].astype(str) + '-' + data['month'].astype(str).str.zfill(2)
                            
                            fig_box = px.box(
                                data,
                                x='year_month',
                                y='value',
                                title='Value Distribution by Month',
                                labels={'year_month': 'Month', 'value': 'Value'}
                            )
                        
                        st.plotly_chart(fig_box, use_container_width=True)
                    
                    elif dist_chart_type == "Violin Plot":
                        # Create violin plot by day of week
                        if 'day_of_week' not in data.columns:
                            data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
                            day_names = {
                                0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
                                3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
                            }
                            data['day_name'] = data['day_of_week'].map(day_names)
                        
                        fig_violin = px.violin(
                            data,
                            x='day_name',
                            y='value',
                            box=True,
                            title='Value Distribution by Day of Week',
                            labels={'day_name': 'Day', 'value': 'Value'}
                        )
                        
                        st.plotly_chart(fig_violin, use_container_width=True)
                    
                    elif dist_chart_type == "Scatter":
                        # Create scatter plot of values over time with color by density
                        fig_scatter = px.scatter(
                            data,
                            x='date',
                            y='value',
                            color='value',
                            title='Value Distribution Over Time',
                            labels={'date': 'Date', 'value': 'Value'},
                            color_continuous_scale='Viridis'
                        )
                        
                        st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    # Add distribution statistics
                    if 'value' in data.columns:
                        stats = data['value'].describe()
                        
                        dist_stats_col1, dist_stats_col2, dist_stats_col3 = st.columns(3)
                        
                        with dist_stats_col1:
                            st.metric("Mean", f"{stats['mean']:.2f}")
                            st.metric("Median", f"{stats['50%']:.2f}")
                        
                        with dist_stats_col2:
                            st.metric("Std Dev", f"{stats['std']:.2f}")
                            skewness = data['value'].skew()
                            st.metric("Skewness", f"{skewness:.2f}")
                        
                        with dist_stats_col3:
                            st.metric("Min", f"{stats['min']:.2f}")
                            st.metric("Max", f"{stats['max']:.2f}")
                
                elif section == "comparison":
                    st.subheader("Comparative Analysis")
                    
                    # Let user choose comparison type
                    comparison_type = st.selectbox(
                        "Comparison Type",
                        options=["Time Period", "Categories", "Correlation"],
                        index=0,
                        key="comparison_type"
                    )
                    
                    if comparison_type == "Time Period":
                        # Compare different time periods
                        
                        # Group by appropriate period based on data size
                        if len(data) >= 365:  # Compare months
                            if 'month' not in data.columns:
                                data['month'] = pd.to_datetime(data['date']).dt.month
                                data['year'] = pd.to_datetime(data['date']).dt.year
                                data['year_month'] = data['year'].astype(str) + '-' + data['month'].astype(str).str.zfill(2)
                            
                            # Group by month
                            period_data = data.groupby('year_month')['value'].mean().reset_index()
                            x_col = 'year_month'
                            title = 'Monthly Comparison'
                            x_label = 'Month'
                        elif len(data) >= 60:  # Compare weeks
                            if 'week' not in data.columns:
                                data['week'] = pd.to_datetime(data['date']).dt.isocalendar().week
                                data['year'] = pd.to_datetime(data['date']).dt.isocalendar().year
                                data['year_week'] = data['year'].astype(str) + '-W' + data['week'].astype(str).str.zfill(2)
                            
                            # Group by week
                            period_data = data.groupby('year_week')['value'].mean().reset_index()
                            x_col = 'year_week'
                            title = 'Weekly Comparison'
                            x_label = 'Week'
                        else:  # Compare days
                            # Group by date
                            period_data = data.groupby('date')['value'].mean().reset_index()
                            x_col = 'date'
                            title = 'Daily Comparison'
                            x_label = 'Date'
                        
                        fig_period = px.line(
                            period_data,
                            x=x_col,
                            y='value',
                            title=title,
                            labels={x_col: x_label, 'value': 'Average Value'},
                            markers=True
                        )
                        
                        st.plotly_chart(fig_period, use_container_width=True)
                    
                    elif comparison_type == "Categories":
                        # Compare between categories if categorical columns exist
                        # First, identify potential category columns
                        categorical_cols = []
                        for col in data.columns:
                            if col not in ['date', 'value'] and data[col].nunique() <= 10:
                                categorical_cols.append(col)
                        
                        if categorical_cols:
                            category_col = st.selectbox(
                                "Select Category",
                                options=categorical_cols,
                                index=0,
                                key="category_col"
                            )
                            
                            # Create comparison visualization
                            fig_cat = px.box(
                                data,
                                x=category_col,
                                y='value',
                                title=f'Value Comparison by {category_col}',
                                labels={category_col: category_col, 'value': 'Value'}
                            )
                            
                            st.plotly_chart(fig_cat, use_container_width=True)
                            
                            # Add category statistics
                            cat_stats = data.groupby(category_col)['value'].agg(['mean', 'median', 'std', 'min', 'max']).reset_index()
                            
                            st.write("Category Statistics:")
                            st.dataframe(cat_stats.round(2), use_container_width=True)
                        else:
                            # Create comparison by time-based categories
                            if 'day_of_week' not in data.columns:
                                data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
                                day_names = {
                                    0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
                                    3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
                                }
                                data['day_name'] = data['day_of_week'].map(day_names)
                            
                            # Compare weekdays vs weekends
                            data['is_weekend'] = data['day_of_week'].isin([5, 6])
                            data['day_type'] = data['is_weekend'].map({True: 'Weekend', False: 'Weekday'})
                            
                            fig_day_type = px.box(
                                data,
                                x='day_type',
                                y='value',
                                title='Weekday vs Weekend Comparison',
                                labels={'day_type': 'Day Type', 'value': 'Value'},
                                color='day_type'
                            )
                            
                            st.plotly_chart(fig_day_type, use_container_width=True)
                            
                            # Add comparison statistics
                            day_type_stats = data.groupby('day_type')['value'].agg(['mean', 'median', 'std']).reset_index()
                            
                            st.write("Day Type Comparison:")
                            st.dataframe(day_type_stats.round(2), use_container_width=True)
                    
                    elif comparison_type == "Correlation":
                        # Create correlation analysis if we have other numeric columns
                        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                        
                        if len(numeric_cols) > 1:
                            st.write("Correlation between numeric variables:")
                            
                            # Calculate correlation matrix
                            corr_matrix = data[numeric_cols].corr()
                            
                            # Create heatmap
                            fig_corr = px.imshow(
                                corr_matrix,
                                text_auto=True,
                                title='Correlation Matrix',
                                color_continuous_scale='RdBu_r',
                                zmin=-1, zmax=1
                            )
                            
                            st.plotly_chart(fig_corr, use_container_width=True)
                        else:
                            # Create autocorrelation plot for time series
                            from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
                            import matplotlib.pyplot as plt
                            
                            # Create figure with subplots
                            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                            
                            # Plot ACF and PACF
                            plot_acf(data['value'].dropna(), lags=min(20, len(data)//2), ax=ax1, title="Autocorrelation")
                            plot_pacf(data['value'].dropna(), lags=min(20, len(data)//2), ax=ax2, title="Partial Autocorrelation")
                            
                            plt.tight_layout()
                            st.pyplot(fig)
                            
                            st.write("Autocorrelation interprets how a value is correlated with past values in the time series.")
                            st.write("Significant spikes suggest patterns that repeat at those lag intervals.")
                
                elif section == "statistics":
                    st.subheader("Statistical Summary")
                    
                    if 'value' in data.columns:
                        # Create basic statistics table
                        stats = data['value'].describe()
                        
                        # Format stats for display
                        stats_formatted = pd.DataFrame({
                            'Statistic': stats.index,
                            'Value': stats.values
                        })
                        
                        # Add additional statistics
                        skewness = data['value'].skew()
                        kurtosis = data['value'].kurtosis()
                        
                        additional_stats = pd.DataFrame({
                            'Statistic': ['skewness', 'kurtosis'],
                            'Value': [skewness, kurtosis]
                        })
                        
                        stats_formatted = pd.concat([stats_formatted, additional_stats])
                        
                        # Format numeric values
                        stats_formatted['Value'] = stats_formatted['Value'].apply(
                            lambda x: f"{x:.2f}" if isinstance(x, float) else x
                        )
                        
                        # Display statistics
                        st.dataframe(stats_formatted.set_index('Statistic'), use_container_width=True)
                        
                        # Statistical visualizations
                        stat_col1, stat_col2 = st.columns(2)
                        
                        with stat_col1:
                            # Q-Q plot for normality check
                            from scipy import stats as scipy_stats
                            
                            fig_qq = go.Figure()
                            
                            # Calculate theoretical quantiles
                            values = data['value'].dropna().values
                            values_sorted = np.sort(values)
                            n = len(values_sorted)
                            p = np.arange(1, n + 1) / (n + 1)
                            theoretical_quantiles = scipy_stats.norm.ppf(p)
                            
                            # Add scatter points
                            fig_qq.add_trace(
                                go.Scatter(
                                    x=theoretical_quantiles,
                                    y=values_sorted,
                                    mode='markers',
                                    name='Data',
                                    marker=dict(
                                        color='blue',
                                        size=5
                                    )
                                )
                            )
                            
                            # Add reference line
                            min_x = min(theoretical_quantiles)
                            max_x = max(theoretical_quantiles)
                            
                            # Find line of best fit
                            slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(
                                theoretical_quantiles, values_sorted
                            )
                            
                            fig_qq.add_trace(
                                go.Scatter(
                                    x=[min_x, max_x],
                                    y=[intercept + slope * min_x, intercept + slope * max_x],
                                    mode='lines',
                                    name='Reference Line',
                                    line=dict(
                                        color='red',
                                        dash='dash'
                                    )
                                )
                            )
                            
                            fig_qq.update_layout(
                                title='Q-Q Plot (Test for Normality)',
                                xaxis_title='Theoretical Quantiles',
                                yaxis_title='Sample Quantiles'
                            )
                            
                            st.plotly_chart(fig_qq, use_container_width=True)
                        
                        with stat_col2:
                            # Histogram with fitted distributions
                            from scipy import stats as scipy_stats
                            
                            # Create histogram
                            hist, bin_edges = np.histogram(data['value'].dropna(), bins=30, density=True)
                            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                            
                            fig_dist = go.Figure()
                            
                            # Add histogram
                            fig_dist.add_trace(
                                go.Bar(
                                    x=bin_centers,
                                    y=hist,
                                    name='Data',
                                    marker_color='blue',
                                    opacity=0.7
                                )
                            )
                            
                            # Fit normal distribution
                            mean, std = scipy_stats.norm.fit(data['value'].dropna())
                            x = np.linspace(min(data['value']), max(data['value']), 100)
                            y_norm = scipy_stats.norm.pdf(x, mean, std)
                            
                            fig_dist.add_trace(
                                go.Scatter(
                                    x=x,
                                    y=y_norm,
                                    mode='lines',
                                    name='Normal',
                                    line=dict(color='red')
                                )
                            )
                            
                            # Add other distributions (e.g., lognormal if appropriate)
                            if min(data['value']) > 0:  # Lognormal only defined for positive values
                                shape, loc, scale = scipy_stats.lognorm.fit(data['value'].dropna())
                                y_lognorm = scipy_stats.lognorm.pdf(x, shape, loc, scale)
                                
                                fig_dist.add_trace(
                                    go.Scatter(
                                        x=x,
                                        y=y_lognorm,
                                        mode='lines',
                                        name='Log-Normal',
                                        line=dict(color='green')
                                    )
                                )
                            
                            fig_dist.update_layout(
                                title='Fitted Probability Distributions',
                                xaxis_title='Value',
                                yaxis_title='Density'
                            )
                            
                            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Include data table if requested
            if include_data_table:
                st.subheader("Data Table")
                
                # Create a display version of the data
                display_data = data[['date', 'value']].copy()
                display_data['date'] = display_data['date'].dt.strftime('%Y-%m-%d')
                
                # Sort by date (newest first)
                display_data = display_data.sort_values('date', ascending=False)
                
                # Limit to 100 rows for display
                st.dataframe(display_data.head(100), use_container_width=True)
    
    # Export report functionality
    if generate_report:
        st.subheader("Generated Report")
        
        if report_format == "Interactive HTML":
            # Create HTML report
            st.info("Preparing Interactive HTML Report...")
            
            # This feature would typically generate an HTML file with embedded Plotly visualizations
            # For demo purposes, we'll create a simple HTML string
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{report_template} Report</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                    .header {{ background-color: #f8f9fa; padding: 20px; margin-bottom: 20px; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .chart {{ width: 100%; height: 500px; margin-bottom: 30px; }}
                    .metrics {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
                    .metric-card {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; width: 22%; }}
                    h1, h2, h3 {{ color: #333; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{report_template} Report</h1>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Period: {data['date'].min().strftime('%Y-%m-%d')} to {data['date'].max().strftime('%Y-%m-%d')}</p>
                </div>
                <div class="container">
                    <!-- Charts would be embedded here using Plotly.js -->
                    <div id="main-chart" class="chart"></div>
                    
                    <!-- More content would be added dynamically -->
                </div>
            </body>
            </html>
            """
            
            # Provide download link
            html_bytes = html_content.encode()
            b64 = base64.b64encode(html_bytes).decode()
            
            href = f'<a href="data:text/html;base64,{b64}" download="{report_template.lower().replace(" ", "_")}_report.html">Download HTML Report</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        elif report_format == "PDF":
            # For PDF export, we'd typically use a library like ReportLab or weasyprint
            # Here we'll just show a mockup of what it would do
            
            st.info("PDF export functionality would generate a downloadable PDF report.")
            st.warning("This is a placeholder - in a production environment, this would generate an actual PDF file using a library like ReportLab.")
            
            # Mock PDF generation - in a real app this would create an actual PDF
            pdf_data = b"Sample PDF content - this would be a real PDF in production"
            b64 = base64.b64encode(pdf_data).decode()
            
            href = f'<a href="data:application/pdf;base64,{b64}" download="{report_template.lower().replace(" ", "_")}_report.pdf">Download PDF Report (Demo)</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        elif report_format == "Excel":
            # Create Excel report
            st.info("Generating Excel Report...")
            
            # Create Excel file in memory
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Write data sheet
                data.to_excel(writer, sheet_name='Data', index=False)
                
                # Add statistics sheet
                if 'value' in data.columns:
                    stats_df = pd.DataFrame({
                        'Statistic': ['Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Skewness', 'Kurtosis'],
                        'Value': [
                            len(data),
                            data['value'].mean(),
                            data['value'].median(),
                            data['value'].std(),
                            data['value'].min(),
                            data['value'].max(),
                            data['value'].skew(),
                            data['value'].kurtosis()
                        ]
                    })
                    
                    stats_df.to_excel(writer, sheet_name='Statistics', index=False)
                
                # Add summary sheet
                if 'date' in data.columns:
                    # Create monthly summary if enough data
                    if 'month' not in data.columns:
                        data['month'] = pd.to_datetime(data['date']).dt.month
                        data['year'] = pd.to_datetime(data['date']).dt.year
                        data['year_month'] = data['year'].astype(str) + '-' + data['month'].astype(str).str.zfill(2)
                    
                    summary_df = data.groupby('year_month')['value'].agg(['mean', 'median', 'std', 'min', 'max', 'count']).reset_index()
                    summary_df.to_excel(writer, sheet_name='Monthly Summary', index=False)
                
                # Add forecast sheet if available
                if 'forecast_data' in st.session_state and st.session_state.forecast_data is not None:
                    st.session_state.forecast_data.to_excel(writer, sheet_name='Forecast', index=False)
            
            # Provide download link
            excel_data = output.getvalue()
            b64 = base64.b64encode(excel_data).decode()
            
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{report_template.lower().replace(" ", "_")}_report.xlsx">Download Excel Report</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        elif report_format == "Image":
            # For image export, we'd capture screenshots of the charts
            # Here we'll just show a mockup of what it would do
            
            st.info("Image export functionality would generate downloadable images of each visualization.")
            st.warning("This is a placeholder - in a production environment, this would generate actual image files.")
            
            # Mock image generation - in a real app this would create actual images
            image_data = b"Sample image content - this would be a real image in production"
            b64 = base64.b64encode(image_data).decode()
            
            href = f'<a href="data:image/png;base64,{b64}" download="report_visualization.png">Download Sample Visualization (Demo)</a>'
            st.markdown(href, unsafe_allow_html=True)
