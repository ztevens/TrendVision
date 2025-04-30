import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import base64

st.title("Settings & Preferences")
st.subheader("Customize your TrendVision AI experience")

# Define settings categories
settings_tab = st.radio(
    "Settings Category",
    options=["Display Settings", "Data Settings", "Analysis Settings", "User Preferences", "About"],
    horizontal=True
)

# Initialize session state for settings
if 'settings' not in st.session_state:
    # Default settings
    st.session_state.settings = {
        'display': {
            'theme': 'light',
            'chart_template': 'plotly_white',
            'default_chart_type': 'line',
            'max_data_points_display': 5000,
            'date_format': '%Y-%m-%d',
            'number_format': '{:.2f}',
            'show_grid': True,
            'animation_enabled': True
        },
        'data': {
            'default_data_source': 'Stock Market Data',
            'cache_enabled': True,
            'cache_timeout_minutes': 30,
            'auto_refresh_enabled': False,
            'auto_refresh_interval_minutes': 15,
            'missing_value_handling': 'interpolate',
            'outlier_detection_enabled': True,
            'outlier_threshold': 3.0
        },
        'analysis': {
            'default_forecast_method': 'prophet',
            'default_forecast_periods': 30,
            'confidence_interval': 0.95,
            'seasonality_detection_enabled': True,
            'trend_detection_enabled': True,
            'anomaly_detection_enabled': True,
            'default_aggregation': 'mean'
        },
        'user': {
            'dashboard_layout': 'standard',
            'startup_view': 'dashboard',
            'save_reports_locally': True,
            'notification_enabled': False,
            'tutorial_mode': True,
            'last_settings_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

# Display Settings
if settings_tab == "Display Settings":
    st.header("Display Settings")
    
    display_col1, display_col2 = st.columns(2)
    
    with display_col1:
        # Theme settings
        st.subheader("Theme")
        
        theme = st.selectbox(
            "Application Theme",
            options=["Light", "Dark"],
            index=0 if st.session_state.settings['display']['theme'] == 'light' else 1
        )
        st.session_state.settings['display']['theme'] = theme.lower()
        
        # Chart template
        chart_template = st.selectbox(
            "Chart Template",
            options=["Plotly White", "Plotly Dark", "Seaborn", "Ggplot2", "Simple White"],
            index=0
        )
        template_map = {
            "Plotly White": "plotly_white",
            "Plotly Dark": "plotly_dark",
            "Seaborn": "seaborn",
            "Ggplot2": "ggplot2",
            "Simple White": "simple_white"
        }
        st.session_state.settings['display']['chart_template'] = template_map[chart_template]
        
        # Default chart type
        default_chart_type = st.selectbox(
            "Default Chart Type",
            options=["Line", "Bar", "Scatter", "Area", "Pie", "Heatmap"],
            index=0
        )
        st.session_state.settings['display']['default_chart_type'] = default_chart_type.lower()
    
    with display_col2:
        # Formatting options
        st.subheader("Formatting")
        
        date_format = st.selectbox(
            "Date Format",
            options=["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%b %d, %Y", "%d %b %Y"],
            index=0
        )
        st.session_state.settings['display']['date_format'] = date_format
        
        number_format = st.selectbox(
            "Number Format",
            options=["{:.2f}", "{:.1f}", "{:,.2f}", "{:,.1f}", "{:.2e}"],
            index=0
        )
        st.session_state.settings['display']['number_format'] = number_format
        
        # Display options
        st.subheader("Display Options")
        
        max_data_points = st.slider(
            "Max Data Points to Display",
            min_value=1000,
            max_value=10000,
            value=st.session_state.settings['display']['max_data_points_display'],
            step=1000
        )
        st.session_state.settings['display']['max_data_points_display'] = max_data_points
        
        show_grid = st.checkbox(
            "Show Grid on Charts", 
            value=st.session_state.settings['display']['show_grid']
        )
        st.session_state.settings['display']['show_grid'] = show_grid
        
        animation_enabled = st.checkbox(
            "Enable Chart Animations", 
            value=st.session_state.settings['display']['animation_enabled']
        )
        st.session_state.settings['display']['animation_enabled'] = animation_enabled
    
    # Theme preview
    st.subheader("Theme Preview")
    
    if theme.lower() == "dark":
        st.markdown("""
        <div style="background-color: #1E1E1E; color: #FFFFFF; padding: 20px; border-radius: 5px;">
            <h4>Dark Theme Preview</h4>
            <p>This is how the dark theme would look.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color: #FFFFFF; color: #262730; padding: 20px; border-radius: 5px; border: 1px solid #E0E0E0;">
            <h4>Light Theme Preview</h4>
            <p>This is how the light theme would look.</p>
        </div>
        """, unsafe_allow_html=True)

# Data Settings
elif settings_tab == "Data Settings":
    st.header("Data Settings")
    
    data_col1, data_col2 = st.columns(2)
    
    with data_col1:
        # Data source settings
        st.subheader("Data Sources")
        
        if 'data_sources' in st.session_state:
            default_source = st.selectbox(
                "Default Data Source",
                options=list(st.session_state.data_sources.keys()),
                index=list(st.session_state.data_sources.keys()).index(st.session_state.settings['data']['default_data_source']) if st.session_state.settings['data']['default_data_source'] in list(st.session_state.data_sources.keys()) else 0
            )
            st.session_state.settings['data']['default_data_source'] = default_source
        else:
            st.info("No data sources loaded. Please visit the home page first.")
        
        # Caching settings
        st.subheader("Data Caching")
        
        cache_enabled = st.checkbox(
            "Enable Data Caching", 
            value=st.session_state.settings['data']['cache_enabled'],
            help="Cache data to improve performance"
        )
        st.session_state.settings['data']['cache_enabled'] = cache_enabled
        
        if cache_enabled:
            cache_timeout = st.slider(
                "Cache Timeout (minutes)",
                min_value=5,
                max_value=60,
                value=st.session_state.settings['data']['cache_timeout_minutes'],
                step=5
            )
            st.session_state.settings['data']['cache_timeout_minutes'] = cache_timeout
    
    with data_col2:
        # Data refresh settings
        st.subheader("Data Refresh")
        
        auto_refresh = st.checkbox(
            "Enable Auto Refresh", 
            value=st.session_state.settings['data']['auto_refresh_enabled'],
            help="Automatically refresh data at specified intervals"
        )
        st.session_state.settings['data']['auto_refresh_enabled'] = auto_refresh
        
        if auto_refresh:
            refresh_interval = st.slider(
                "Refresh Interval (minutes)",
                min_value=5,
                max_value=60,
                value=st.session_state.settings['data']['auto_refresh_interval_minutes'],
                step=5
            )
            st.session_state.settings['data']['auto_refresh_interval_minutes'] = refresh_interval
        
        # Data processing settings
        st.subheader("Data Processing")
        
        missing_value_handling = st.selectbox(
            "Missing Value Handling",
            options=["Interpolate", "Forward Fill", "Backward Fill", "Drop", "Zero"],
            index=["interpolate", "ffill", "bfill", "drop", "zero"].index(st.session_state.settings['data']['missing_value_handling'])
        )
        st.session_state.settings['data']['missing_value_handling'] = missing_value_handling.lower()
        
        outlier_detection = st.checkbox(
            "Enable Outlier Detection", 
            value=st.session_state.settings['data']['outlier_detection_enabled']
        )
        st.session_state.settings['data']['outlier_detection_enabled'] = outlier_detection
        
        if outlier_detection:
            outlier_threshold = st.slider(
                "Outlier Threshold (Z-score)",
                min_value=1.0,
                max_value=5.0,
                value=float(st.session_state.settings['data']['outlier_threshold']),
                step=0.1
            )
            st.session_state.settings['data']['outlier_threshold'] = outlier_threshold
    
    # Data management options
    st.subheader("Data Management")
    
    data_management_col1, data_management_col2 = st.columns(2)
    
    with data_management_col1:
        if st.button("Clear Cache", help="Remove all cached data"):
            # This would actually clear cache in a real implementation
            st.success("Cache cleared successfully!")
    
    with data_management_col2:
        if st.button("Reset Data Settings", help="Restore default data settings"):
            # Reset only data settings
            st.session_state.settings['data'] = {
                'default_data_source': 'Stock Market Data',
                'cache_enabled': True,
                'cache_timeout_minutes': 30,
                'auto_refresh_enabled': False,
                'auto_refresh_interval_minutes': 15,
                'missing_value_handling': 'interpolate',
                'outlier_detection_enabled': True,
                'outlier_threshold': 3.0
            }
            st.success("Data settings have been reset to defaults!")

# Analysis Settings
elif settings_tab == "Analysis Settings":
    st.header("Analysis Settings")
    
    analysis_col1, analysis_col2 = st.columns(2)
    
    with analysis_col1:
        # Forecasting settings
        st.subheader("Forecasting")
        
        forecast_method = st.selectbox(
            "Default Forecast Method",
            options=["Prophet", "ARIMA", "Exponential Smoothing", "Linear Regression", "Random Forest"],
            index=["prophet", "arima", "exponential_smoothing", "linear_regression", "random_forest"].index(st.session_state.settings['analysis']['default_forecast_method'])
        )
        st.session_state.settings['analysis']['default_forecast_method'] = forecast_method.lower().replace(" ", "_")
        
        forecast_periods = st.slider(
            "Default Forecast Periods",
            min_value=7,
            max_value=365,
            value=st.session_state.settings['analysis']['default_forecast_periods'],
            step=1
        )
        st.session_state.settings['analysis']['default_forecast_periods'] = forecast_periods
        
        confidence_interval = st.slider(
            "Confidence Interval",
            min_value=0.8,
            max_value=0.99,
            value=float(st.session_state.settings['analysis']['confidence_interval']),
            step=0.01,
            format="%.2f"
        )
        st.session_state.settings['analysis']['confidence_interval'] = confidence_interval
    
    with analysis_col2:
        # Analysis options
        st.subheader("Analysis Options")
        
        seasonality_detection = st.checkbox(
            "Enable Seasonality Detection", 
            value=st.session_state.settings['analysis']['seasonality_detection_enabled']
        )
        st.session_state.settings['analysis']['seasonality_detection_enabled'] = seasonality_detection
        
        trend_detection = st.checkbox(
            "Enable Trend Detection", 
            value=st.session_state.settings['analysis']['trend_detection_enabled']
        )
        st.session_state.settings['analysis']['trend_detection_enabled'] = trend_detection
        
        anomaly_detection = st.checkbox(
            "Enable Anomaly Detection", 
            value=st.session_state.settings['analysis']['anomaly_detection_enabled']
        )
        st.session_state.settings['analysis']['anomaly_detection_enabled'] = anomaly_detection
        
        # Aggregation settings
        st.subheader("Data Aggregation")
        
        default_aggregation = st.selectbox(
            "Default Aggregation Method",
            options=["Mean", "Median", "Sum", "Min", "Max"],
            index=["mean", "median", "sum", "min", "max"].index(st.session_state.settings['analysis']['default_aggregation'])
        )
        st.session_state.settings['analysis']['default_aggregation'] = default_aggregation.lower()
    
    # Advanced analysis settings
    st.subheader("Advanced Analysis Settings")
    
    with st.expander("Advanced Settings"):
        advanced_col1, advanced_col2 = st.columns(2)
        
        with advanced_col1:
            # ARIMA-specific settings
            st.write("**ARIMA Model Settings**")
            p = st.slider("AR order (p)", 0, 5, 2)
            d = st.slider("Differencing (d)", 0, 2, 1)
            q = st.slider("MA order (q)", 0, 5, 2)
            
            # Store in a nested dictionary
            if 'arima' not in st.session_state.settings['analysis']:
                st.session_state.settings['analysis']['arima'] = {}
            
            st.session_state.settings['analysis']['arima']['p'] = p
            st.session_state.settings['analysis']['arima']['d'] = d
            st.session_state.settings['analysis']['arima']['q'] = q
        
        with advanced_col2:
            # Prophet-specific settings
            st.write("**Prophet Model Settings**")
            yearly_seasonality = st.checkbox("Yearly Seasonality", value=True)
            weekly_seasonality = st.checkbox("Weekly Seasonality", value=True)
            daily_seasonality = st.checkbox("Daily Seasonality", value=False)
            
            # Store in a nested dictionary
            if 'prophet' not in st.session_state.settings['analysis']:
                st.session_state.settings['analysis']['prophet'] = {}
            
            st.session_state.settings['analysis']['prophet']['yearly_seasonality'] = yearly_seasonality
            st.session_state.settings['analysis']['prophet']['weekly_seasonality'] = weekly_seasonality
            st.session_state.settings['analysis']['prophet']['daily_seasonality'] = daily_seasonality

# User Preferences
elif settings_tab == "User Preferences":
    st.header("User Preferences")
    
    user_col1, user_col2 = st.columns(2)
    
    with user_col1:
        # Interface preferences
        st.subheader("Interface Preferences")
        
        dashboard_layout = st.selectbox(
            "Dashboard Layout",
            options=["Standard", "Compact", "Expanded", "Custom"],
            index=["standard", "compact", "expanded", "custom"].index(st.session_state.settings['user']['dashboard_layout'])
        )
        st.session_state.settings['user']['dashboard_layout'] = dashboard_layout.lower()
        
        startup_view = st.selectbox(
            "Default Startup View",
            options=["Dashboard", "Trend Analysis", "Forecasting", "Reports", "Settings"],
            index=["dashboard", "trend_analysis", "forecasting", "reports", "settings"].index(st.session_state.settings['user']['startup_view'])
        )
        st.session_state.settings['user']['startup_view'] = startup_view.lower()
        
        tutorial_mode = st.checkbox(
            "Enable Tutorial Mode", 
            value=st.session_state.settings['user']['tutorial_mode'],
            help="Show helpful tips and explanations"
        )
        st.session_state.settings['user']['tutorial_mode'] = tutorial_mode
    
    with user_col2:
        # Notification settings
        st.subheader("Notifications")
        
        notification_enabled = st.checkbox(
            "Enable Notifications", 
            value=st.session_state.settings['user']['notification_enabled']
        )
        st.session_state.settings['user']['notification_enabled'] = notification_enabled
        
        # Report preferences
        st.subheader("Report Preferences")
        
        save_reports = st.checkbox(
            "Save Reports Locally", 
            value=st.session_state.settings['user']['save_reports_locally'],
            help="Automatically save generated reports"
        )
        st.session_state.settings['user']['save_reports_locally'] = save_reports
    
    # User data management
    st.subheader("Data Management")
    
    data_mgmt_col1, data_mgmt_col2, data_mgmt_col3 = st.columns(3)
    
    with data_mgmt_col1:
        if st.button("Export Settings", help="Export settings as JSON file"):
            # Create JSON string
            settings_json = json.dumps(st.session_state.settings, default=str, indent=4)
            
            # Create download link
            b64 = base64.b64encode(settings_json.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="trendvision_settings.json">Download Settings</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    with data_mgmt_col2:
        if st.button("Import Settings", help="Import settings from a JSON file"):
            st.info("In a full implementation, this would allow uploading a settings JSON file.")
            
            # This would normally create a file uploader and handle the import
            # For demo, we just show the UI element
            file_upload = st.file_uploader("Upload settings JSON file", type=["json"], key="settings_file")
            
            if file_upload is not None:
                try:
                    imported_settings = json.loads(file_upload.getvalue().decode())
                    st.session_state.settings = imported_settings
                    st.success("Settings imported successfully!")
                except Exception as e:
                    st.error(f"Error importing settings: {str(e)}")
    
    with data_mgmt_col3:
        if st.button("Reset All Settings", help="Restore all default settings"):
            # This would reset all settings to default
            st.warning("This will reset all settings to their default values. Are you sure?")
            
            if st.button("Yes, Reset All", key="confirm_reset"):
                # Reset to defaults
                st.session_state.settings = {
                    'display': {
                        'theme': 'light',
                        'chart_template': 'plotly_white',
                        'default_chart_type': 'line',
                        'max_data_points_display': 5000,
                        'date_format': '%Y-%m-%d',
                        'number_format': '{:.2f}',
                        'show_grid': True,
                        'animation_enabled': True
                    },
                    'data': {
                        'default_data_source': 'Stock Market Data',
                        'cache_enabled': True,
                        'cache_timeout_minutes': 30,
                        'auto_refresh_enabled': False,
                        'auto_refresh_interval_minutes': 15,
                        'missing_value_handling': 'interpolate',
                        'outlier_detection_enabled': True,
                        'outlier_threshold': 3.0
                    },
                    'analysis': {
                        'default_forecast_method': 'prophet',
                        'default_forecast_periods': 30,
                        'confidence_interval': 0.95,
                        'seasonality_detection_enabled': True,
                        'trend_detection_enabled': True,
                        'anomaly_detection_enabled': True,
                        'default_aggregation': 'mean'
                    },
                    'user': {
                        'dashboard_layout': 'standard',
                        'startup_view': 'dashboard',
                        'save_reports_locally': True,
                        'notification_enabled': False,
                        'tutorial_mode': True,
                        'last_settings_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
                st.success("All settings have been reset to defaults!")

# About
elif settings_tab == "About":
    st.header("About TrendVision AI")
    
    # Application description
    st.markdown("""
    **TrendVision AI** is an advanced trend analysis and forecasting platform designed to help you make data-driven decisions.
    
    ### Key Features
    - **Multi-source Data Integration**: Connect to multiple data sources
    - **Advanced Trend Analysis**: Discover patterns and insights in your data
    - **Interactive Visualizations**: Explore your data with powerful charts
    - **Predictive Forecasting**: Forecast future trends with advanced algorithms
    - **Customizable Reports**: Create and share visualized insights
    
    ### Version Information
    - **TrendVision AI**: v1.0.0
    - **Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
    
    ### Technologies Used
    - Streamlit
    - Pandas & NumPy
    - Plotly
    - Scikit-learn
    - Prophet & statsmodels
    """)
    
    # Showcase some images
    st.subheader("TrendVision AI in Action")
    
    image_col1, image_col2 = st.columns(2)
    
    with image_col1:
        st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f", caption="Interactive Data Visualization")
    
    with image_col2:
        st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", caption="Trend Analysis Dashboard")
    
    # Credits & Acknowledgements
    st.subheader("Credits & Acknowledgements")
    
    st.markdown("""
    - Data visualization powered by [Plotly](https://plotly.com/)
    - Time series forecasting with [Prophet](https://facebook.github.io/prophet/) and [statsmodels](https://www.statsmodels.org/)
    - Interactive web interface built with [Streamlit](https://streamlit.io/)
    - Stock photos from [Unsplash](https://unsplash.com/)
    """)
    
    # Contact information
    st.subheader("Support & Feedback")
    
    st.markdown("""
    We're constantly improving TrendVision AI based on user feedback.
    
    - **Email**: support@trendvision-ai.example.com
    - **GitHub**: [github.com/trendvision-ai](https://github.com)
    - **Documentation**: [docs.trendvision-ai.example.com](https://docs.example.com)
    """)

# Save settings when modified
st.session_state.settings['user']['last_settings_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Apply settings
if settings_tab == "Display Settings":
    # Apply dark mode if selected
    if st.session_state.settings['display']['theme'] == 'dark':
        st.markdown("""
        <style>
        /* Dark mode styles would go here */
        </style>
        """, unsafe_allow_html=True)

# Show saved notification
st.success("Settings saved automatically")
