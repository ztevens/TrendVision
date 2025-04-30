"""
TrendVision AI - Social Media Trend Analysis and Content Ideation Platform

This application helps social media creators and marketers identify trends,
analyze their performance data, and generate content ideas tailored to
their specific platforms and objectives.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Import local modules
from data_sources import load_data_sources, get_data_from_source, handle_uploaded_data
from data_processor import process_data, filter_data
from visualization import create_visualization
from forecasting import forecast_trend
from trend_analyzer import analyze_trend_data
from ai_content_generator import generate_content_ideas_with_ai, check_ai_availability
from utils import format_large_number, export_data, apply_theme

# App configuration
st.set_page_config(
    page_title="TrendVision AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "data_sources" not in st.session_state:
    # Load predefined data sources
    st.session_state.data_sources = load_data_sources()

if "current_data" not in st.session_state:
    st.session_state.current_data = None

if "forecast_data" not in st.session_state:
    st.session_state.forecast_data = None

if "trend_analysis" not in st.session_state:
    st.session_state.trend_analysis = None

if "content_ideas" not in st.session_state:
    st.session_state.content_ideas = None

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "last_update" not in st.session_state:
    st.session_state.last_update = None

if "api_available" not in st.session_state:
    st.session_state.api_available = check_ai_availability()

# Apply theme based on dark mode setting
apply_theme(st.session_state.dark_mode)

# Sidebar for data source selection and controls
st.sidebar.title("TrendVision AI")
st.sidebar.image("https://img.icons8.com/fluency/96/000000/trend.png", width=80)

st.sidebar.header("Data Source")
# Data source selection
data_source = st.sidebar.selectbox(
    "Select Data Source",
    options=list(st.session_state.data_sources.keys()),
    index=0
)

# Load data button
if st.sidebar.button("Load Data"):
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
        st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate trend analysis
        st.session_state.trend_analysis = analyze_trend_data(data)
        
        st.sidebar.success(f"Data loaded successfully at {st.session_state.last_update}")

# Date range selector (only if data is loaded)
if st.session_state.current_data is not None:
    st.sidebar.header("Date Range")
    
    # Get min and max dates from data
    min_date = st.session_state.current_data['date'].min()
    max_date = st.session_state.current_data['date'].max()
    
    date_range = st.sidebar.date_input(
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
        
        # Update trend analysis with filtered data
        st.session_state.trend_analysis = analyze_trend_data(filtered_data)

# Forecast settings
st.sidebar.header("Forecast Settings")
forecast_enabled = st.sidebar.checkbox("Enable Forecasting", value=False)

if forecast_enabled:
    forecast_days = st.sidebar.slider("Forecast Period (Days)", 7, 90, 30)
    forecast_method = st.sidebar.selectbox(
        "Forecast Method",
        options=["Prophet", "ARIMA", "Exponential Smoothing", "Linear Regression"],
        index=0
    )
    
    if st.sidebar.button("Generate Forecast"):
        if st.session_state.current_data is not None:
            with st.spinner("Generating forecast..."):
                forecast_data = forecast_trend(
                    st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data,
                    method=forecast_method.lower().replace(" ", "_"),
                    periods=forecast_days
                )
                st.session_state.forecast_data = forecast_data
                st.sidebar.success(f"Forecast generated for {forecast_days} days")

# AI content suggestions
st.sidebar.header("AI Content Suggestions")

# Check if AI is available (Anthropic API key is set up)
ai_available = check_ai_availability()
st.session_state.api_available = ai_available

if ai_available["anthropic"]:
    if st.sidebar.button("Generate Content Ideas"):
        if st.session_state.trend_analysis:
            with st.spinner("Generating AI content ideas..."):
                content_ideas = generate_content_ideas_with_ai(
                    st.session_state.trend_analysis.get("platform", "Unknown"),
                    st.session_state.trend_analysis.get("metric", "Unknown"),
                    st.session_state.trend_analysis,
                    api_provider="anthropic"
                )
                st.session_state.content_ideas = content_ideas
                if content_ideas.get("status") == "success":
                    st.sidebar.success("Content ideas generated successfully!")
                else:
                    st.sidebar.error(content_ideas.get("message", "Error generating content ideas"))
else:
    st.sidebar.info("AI-powered content suggestions are not available right now.")

# Settings section
st.sidebar.header("Settings")

# Dark mode toggle
dark_mode = st.sidebar.checkbox("Dark Mode", value=st.session_state.dark_mode)
if dark_mode != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_mode
    apply_theme(dark_mode)
    st.rerun()

# API key management
with st.sidebar.expander("API Keys"):
    openai_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key for AI content suggestions")
    if openai_key:
        st.session_state.OPENAI_API_KEY = openai_key
        st.session_state.api_available = check_ai_availability()
    
    anthropic_key = st.text_input("Anthropic API Key", type="password", help="Enter your Anthropic API key for AI content suggestions")
    if anthropic_key:
        st.session_state.ANTHROPIC_API_KEY = anthropic_key
        st.session_state.api_available = check_ai_availability()
    
    if st.button("Save API Keys"):
        st.session_state.api_available = check_ai_availability()
        st.success("API keys saved successfully!")

# Main content area
if st.session_state.current_data is None:
    # Welcome screen with introduction
    st.title("Welcome to TrendVision AI")
    st.subheader("Social Media Trend Analysis & Content Idea Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7", caption="Social Media Strategy")
        
        st.markdown("""
        ### How TrendVision AI Helps You:
        
        - **Identify Emerging Trends**: Discover what's gaining traction across platforms
        - **Analyze Performance**: Understand what's working and why
        - **Generate Content Ideas**: Get AI-powered content suggestions tailored to your platform
        - **Forecast Future Performance**: Predict engagement trends for better planning
        - **Optimize Your Strategy**: Make data-driven decisions to improve results
        """)
    
    with col2:
        st.image("https://images.unsplash.com/photo-1533750349088-cd871a92f312", caption="Content Creation Strategy")
        
        st.markdown("""
        ### Get Started in 3 Steps:
        
        1. **Select a Data Source** from the sidebar
        2. **Load Data** to analyze trends and patterns
        3. **Generate Content Ideas** tailored to your platform and goals
        
        For the best experience, connect your own data sources or use our simulations to explore different platforms.
        
        Need AI-powered suggestions? Add your OpenAI or Anthropic API key in the Settings panel.
        """)
    
    # Features showcase
    st.header("Key Features")
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.subheader("📊 Trend Analysis")
        st.write("Identify emerging patterns and insights across platforms")
        
        st.subheader("🚀 Performance Forecasting")
        st.write("Predict future trends with advanced algorithms")
    
    with feature_col2:
        st.subheader("💡 Content Ideas")
        st.write("Get platform-specific content suggestions that resonate")
        
        st.subheader("📈 Engagement Optimization")
        st.write("Learn what drives engagement for your specific audience")
    
    with feature_col3:
        st.subheader("🗓️ Posting Strategy")
        st.write("Discover optimal posting times and content mix")
        
        st.subheader("🔍 Competitor Insights")
        st.write("Benchmark your performance against industry trends")

else:
    # Display data analysis and trend insights
    st.title("Social Media Trend Analysis")
    
    # Get the data to display
    data_to_display = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.current_data
    
    # Display basic info about the analysis
    trend_analysis = st.session_state.trend_analysis
    
    if trend_analysis and trend_analysis["status"] == "success":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Platform", trend_analysis["platform"])
        
        with col2:
            st.metric("Metric", trend_analysis["metric"])
        
        with col3:
            if "insights" in trend_analysis and "overall_trend" in trend_analysis["insights"]:
                overall_trend = trend_analysis["insights"]["overall_trend"]
                direction = overall_trend["direction"].upper()
                change = f"{overall_trend['percent_change']}%"
                st.metric("Trend Direction", direction, change)
            else:
                st.metric("Trend Direction", "N/A")
    
    # Visualizations row
    st.header("Performance Visualization")
    
    # Trend visualization
    fig = create_visualization(
        data_to_display,
        visualization_type='trend',
        chart_type='line',
        forecast_data=st.session_state.forecast_data
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights section
    st.header("Trend Insights")
    
    if trend_analysis and trend_analysis["status"] == "success":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Performance Analysis")
            
            if "insights" in trend_analysis:
                insights = trend_analysis["insights"]
                
                if "overall_trend" in insights:
                    st.markdown(f"**Overall Trend:** {insights['overall_trend']['interpretation']}")
                
                if "volatility" in insights:
                    st.markdown(f"**Volatility Analysis:** {insights['volatility']['interpretation']}")
                
                if "seasonality" in insights:
                    seasonality = insights["seasonality"]
                    st.markdown(f"**Best Day for Content:** {seasonality['best_day']}")
                    st.markdown(f"**Worst Day for Content:** {seasonality['worst_day']}")
                    st.markdown(f"**Day Variance:** {seasonality['day_variance']}% difference between best and worst day")
        
        with col2:
            st.subheader("Platform Trends")
            
            if "trend_patterns" in trend_analysis:
                patterns = trend_analysis["trend_patterns"]
                
                st.markdown("**Current Trends:**")
                for trend in patterns.get("current_trends", []):
                    st.markdown(f"• {trend}")
                
                st.markdown("**Emerging Trends:**")
                for trend in patterns.get("emerging_trends", []):
                    st.markdown(f"• {trend}")
    
    # Content recommendations section
    st.header("Content Recommendations")
    
    if trend_analysis and "recommendations" in trend_analysis:
        recommendations = trend_analysis["recommendations"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Content Strategies")
            
            if "content_strategies" in recommendations:
                strategies = recommendations["content_strategies"]
                for strategy in strategies:
                    st.markdown(f"• {strategy}")
            
            st.subheader("Posting Tips")
            
            if "posting_tips" in recommendations:
                tips = recommendations["posting_tips"]
                for tip in tips:
                    st.markdown(f"• {tip}")
        
        with col2:
            st.subheader("Content Ideas")
            
            if "content_ideas" in recommendations:
                ideas = recommendations["content_ideas"]
                for idea in ideas:
                    st.markdown(f"• {idea}")
    
    # AI-generated content ideas section
    if st.session_state.content_ideas and st.session_state.content_ideas.get("status") == "success":
        st.header("AI-Generated Content Suggestions")
        
        ideas = st.session_state.content_ideas.get("ideas", {})
        
        ai_col1, ai_col2 = st.columns(2)
        
        with ai_col1:
            st.subheader("Content Ideas")
            
            if "content_ideas" in ideas:
                for i, idea in enumerate(ideas["content_ideas"][:5], 1):
                    with st.expander(f"{i}. {idea.get('title', f'Idea {i}')}"):
                        st.markdown(idea.get("description", ""))
                        if "best_formats" in idea:
                            st.markdown(f"**Best formats:** {', '.join(idea['best_formats'])}")
            
            st.subheader("Content Series Ideas")
            
            if "content_series_ideas" in ideas:
                for idea in ideas["content_series_ideas"]:
                    st.markdown(f"• {idea}")
        
        with ai_col2:
            st.subheader("Hashtag Suggestions")
            
            if "hashtag_suggestions" in ideas:
                hashtags = ideas["hashtag_suggestions"]
                hashtag_html = " ".join([f"<span style='background-color:#e6f3ff; padding:5px; margin:5px; border-radius:3px;'>{tag}</span>" for tag in hashtags])
                st.markdown(hashtag_html, unsafe_allow_html=True)
            
            st.subheader("Posting Schedule")
            
            if "posting_schedule" in ideas:
                schedule = ideas["posting_schedule"]
                if "best_days" in schedule:
                    st.markdown(f"**Best days:** {', '.join(schedule['best_days'])}")
                if "best_times" in schedule:
                    st.markdown(f"**Best times:** {', '.join(schedule['best_times'])}")
                if "frequency" in schedule:
                    st.markdown(f"**Recommended frequency:** {schedule['frequency']}")
            
            st.subheader("Trend Insights")
            
            if "trend_insights" in ideas:
                for insight in ideas["trend_insights"]:
                    st.markdown(f"• {insight}")
    
    # Data table section
    with st.expander("View Data"):
        st.dataframe(data_to_display, use_container_width=True)
        
        # Export options
        st.subheader("Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox(
                "Export Format",
                options=["CSV", "Excel", "JSON"],
                index=0
            )
        
        with col2:
            if st.button("Export Data"):
                export_data(data_to_display, format=export_format.lower())