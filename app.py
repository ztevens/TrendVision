"""
TrendVision AI - Social Media Content Ideas Generator

This application helps social media creators and marketers generate high-quality
content ideas tailored to their specific platforms and objectives.
"""

import os
import streamlit as st
from datetime import datetime
import io
import base64
import random

# Import modules
from utils import apply_theme
from data_sources import load_data_sources, get_data_from_source
from data_processor import filter_data
from trend_analyzer import analyze_trend_data
from ai_content_generator import generate_content_ideas_with_ai, check_ai_availability

# Set page config
st.set_page_config(
    page_title="TrendVision AI",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'email' not in st.session_state:
    st.session_state.email = ""
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'data_sources' not in st.session_state:
    st.session_state.data_sources = load_data_sources()
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'trend_analysis' not in st.session_state:
    st.session_state.trend_analysis = None
if 'content_ideas' not in st.session_state:
    st.session_state.content_ideas = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if 'last_login' not in st.session_state:
    st.session_state.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if 'current_data_source' not in st.session_state:
    st.session_state.current_data_source = None
if 'selected_platform' not in st.session_state:
    st.session_state.selected_platform = "Instagram"
if 'selected_metric' not in st.session_state:
    st.session_state.selected_metric = "Engagement"

# Apply theme based on dark mode setting
apply_theme(st.session_state.dark_mode)

# Sidebar for user account and settings
# Create an SVG icon for the app
trend_icon = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTIgNTEyIiBmaWxsPSIjMDBiNGZmIj48cGF0aCBkPSJNNDk2IDM4NGgtMTYwdi02NGgxNjBjOC44IDAgMTYtNy4yIDE2LTE2di0zMmMwLTguOC03LjItMTYtMTYtMTZoLTE2MHYtNjRoMTYwYzguOCAwIDE2LTcuMiAxNi0xNnYtMzJjMC04LjgtNy4yLTE2LTE2LTE2SDMwNFY2NGMwLTguOC03LjItMTYtMTYtMTZoLTMyYy04LjggMC0xNiA3LjItMTYgMTZ2NjRIMTZjLTguOCAwLTE2IDcuMi0xNiAxNnYzMmMwIDguOCA3LjIgMTYgMTYgMTZoMjI0djY0SDE2Yy04LjggMC0xNiA3LjItMTYgMTZ2MzJjMCA4LjggNy4yIDE2IDE2IDE2aDIyNHY2NEgyMTZjLTguOCAwLTE2IDcuMi0xNiAxNnYzMmMwIDguOCA3LjIgMTYgMTYgMTZoMjgwYzguOCAwIDE2LTcuMiAxNi0xNnYtMzJjMC04LjgtNy4yLTE2LTE2LTE2eiIvPjwvc3ZnPg=="
st.sidebar.image(trend_icon, width=80)

st.sidebar.header("Account")

# Login/Registration Form
if not st.session_state.is_logged_in:
    login_tab, register_tab = st.sidebar.tabs(["Login", "Register"])
    
    with login_tab:
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Sign In", key="signin_button"):
            # Simple mock login - in a real app, you would check credentials in a database
            st.session_state.user_name = "User" # Would get this from the database
            st.session_state.email = login_email
            st.session_state.is_logged_in = True
            st.session_state.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
    
    with register_tab:
        new_name = st.text_input("Full Name", key="register_name")
        new_email = st.text_input("Email", key="register_email")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Create Account", key="register_button"):
            if new_password != confirm_password:
                st.sidebar.error("Passwords don't match!")
            elif not new_email or not new_name or not new_password:
                st.sidebar.error("Please fill all fields!")
            else:
                # In a real app, you would save the user to a database
                st.session_state.user_name = new_name
                st.session_state.email = new_email
                st.session_state.is_logged_in = True
                st.session_state.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.sidebar.success("Account created successfully!")
                st.rerun()
else:
    # Show user info and logout button if logged in
    st.sidebar.write(f"Welcome, **{st.session_state.user_name}**!")
    st.sidebar.write(f"Email: {st.session_state.email}")
    
    if st.sidebar.button("Sign Out"):
        st.session_state.is_logged_in = False
        st.rerun()

# Content Idea Generator
st.sidebar.header("Content Idea Generator")

# Platform selection
available_platforms = ["Instagram", "TikTok", "YouTube", "LinkedIn", "Twitter", "Facebook"]
selected_platform = st.sidebar.selectbox(
    "Select Platform",
    options=available_platforms,
    index=available_platforms.index(st.session_state.selected_platform) if st.session_state.selected_platform in available_platforms else 0
)

# Store selection in session state
st.session_state.selected_platform = selected_platform

# Content type/metric selection
available_metrics = ["Engagement", "Growth", "Reach", "Viral Potential"]
selected_metric = st.sidebar.selectbox(
    "Content Goal",
    options=available_metrics,
    index=available_metrics.index(st.session_state.selected_metric) if st.session_state.selected_metric in available_metrics else 0
)

# Store selection in session state
st.session_state.selected_metric = selected_metric

# Optional industry selection for more specific ideas
industries = ["Technology", "Fashion", "Food & Beverage", "Health & Wellness", "Travel", "Entertainment", "Education", "Finance", "Sports", "Beauty"]
selected_industry = st.sidebar.selectbox("Industry (Optional)", ["Any"] + industries)

# Check if AI is available (Anthropic API key is set up)
ai_available = check_ai_availability()
st.session_state.api_available = ai_available

# Generate Button
if st.sidebar.button("✨ Generate Ideas", use_container_width=True):
    # Simulate loading data from backend - this would normally be handled invisibly
    with st.spinner("Analyzing trends and generating content ideas..."):
        # Get data using a simulation
        data_source = "Social Media Trends"
        data = get_data_from_source(st.session_state.data_sources[data_source])
        
        # Save data and generate analysis in the background
        st.session_state.current_data = data
        st.session_state.trend_analysis = analyze_trend_data(data)
        
        # Generate content ideas
        if ai_available["anthropic"]:
            content_ideas = generate_content_ideas_with_ai(
                st.session_state.selected_platform, 
                st.session_state.selected_metric,
                st.session_state.trend_analysis,
                api_provider="anthropic"
            )
            st.session_state.content_ideas = content_ideas
            
            if content_ideas.get("status") != "success":
                st.sidebar.error("Error generating content ideas. Please try again.")
        else:
            st.sidebar.error("AI service is not available. Please check your settings.")

# Settings section
st.sidebar.header("Settings")

# Dark mode toggle
dark_mode = st.sidebar.checkbox("Dark Mode", value=st.session_state.dark_mode)
if dark_mode != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_mode
    apply_theme(dark_mode)
    st.rerun()

# About section with app info
with st.sidebar.expander("About"):
    st.markdown("""
    **TrendVision AI** helps content creators generate trending content ideas 
    tailored to specific platforms. Our AI analyzes thousands of trending posts
    to suggest content that will resonate with your audience.
    
    Built with Streamlit and powered by Anthropic Claude AI.
    
    Version: 2.0.0
    """)

# Main content area
if not st.session_state.is_logged_in:
    # Welcome screen for visitors
    st.title("TrendVision AI")
    st.subheader("AI-Powered Content Ideas for Social Media Success")
    
    # Hero section
    hero_col1, hero_col2 = st.columns([3, 2])
    
    with hero_col1:
        st.markdown("""
        ### Never Run Out of Content Ideas Again
        
        TrendVision AI analyzes thousands of trending posts across social platforms to generate
        personalized content ideas tailored to your specific goals and audience.
        
        **Get started by creating an account or signing in →**
        """)
        
        st.info("📱 Supporting all major platforms: Instagram, TikTok, YouTube, LinkedIn, Twitter, and Facebook")
    
    with hero_col2:
        st.image("https://images.unsplash.com/photo-1611162616475-46b635cb6868", 
                 caption="AI-powered content suggestions")
    
    # Benefit section
    st.header("Why Choose TrendVision AI?")
    
    benefit_col1, benefit_col2, benefit_col3 = st.columns(3)
    
    with benefit_col1:
        st.markdown("### 🚀 Stay Ahead of Trends")
        st.markdown("Our AI constantly monitors what's trending across platforms so you're always ahead of the curve.")
    
    with benefit_col2:
        st.markdown("### 💡 Platform-Optimized Ideas")
        st.markdown("Get ideas specifically tailored to perform well on your chosen platform with format-specific suggestions.")
    
    with benefit_col3:
        st.markdown("### 📈 Grow Your Audience")
        st.markdown("Focus your content strategy on specific goals like engagement, growth, or viral potential.")
    
    # Testimonials
    st.header("Trusted by Content Creators Worldwide")
    
    testimonial_col1, testimonial_col2 = st.columns(2)
    
    with testimonial_col1:
        st.markdown("""
        > "TrendVision AI transformed my content strategy. I went from posting whatever came to mind to having a strategic approach backed by data. My engagement is up 327% since I started using it!"
        
        **Sarah J., Instagram Influencer (142K followers)**
        """)
    
    with testimonial_col2:
        st.markdown("""
        > "As a social media manager handling 5 different brand accounts, TrendVision AI has been a game-changer. It's like having a research team working for you 24/7."
        
        **Mark T., Social Media Agency Director**
        """)
    
    # Brands section
    st.markdown("### Powering Content Strategies For")
    brand_col1, brand_col2, brand_col3, brand_col4 = st.columns(4)
    with brand_col1:
        st.markdown("**SocialBoost Agency**")
    with brand_col2:
        st.markdown("**ContentPro Studios**")
    with brand_col3:
        st.markdown("**ViralNation**")
    with brand_col4:
        st.markdown("**TrendSetters Media**")

    # Features section
    st.header("Key Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.image("https://images.unsplash.com/photo-1611162618071-b39a2ec055fb", caption="Platform-specific content ideas")
        
        st.markdown("""
        ### Platform-Optimized Content Ideas
        
        * Format-specific suggestions tailored to each platform
        * Hashtag recommendations to maximize reach
        * Caption templates and hooks that drive engagement
        * Content series ideas for consistent posting
        """)
    
    with feature_col2:
        st.image("https://images.unsplash.com/photo-1560472355-536de3962603", caption="Data-driven content strategy")
        
        st.markdown("""
        ### AI-Powered Trend Analysis
        
        * Identify emerging topics before they peak
        * Understand what's resonating with audiences now
        * Get seasonal content recommendations
        * Optimize posting time and frequency
        """)
    
    # CTA
    st.markdown("---")
    st.markdown("### Ready to transform your content strategy?")
    
    cta_col1, cta_col2, cta_col3 = st.columns([2, 2, 1])
    with cta_col1:
        st.info("Create an account to start generating ideas")
    with cta_col2:
        st.success("Already have an account? Sign in")

elif 'content_ideas' in st.session_state and st.session_state.content_ideas and st.session_state.content_ideas.get("status") == "success":
    # Show generated content ideas
    st.title(f"Content Ideas for {st.session_state.selected_platform}")
    
    # Header with info about the generated ideas
    st.markdown(f"### Optimized for: **{st.session_state.selected_metric}**")
    if selected_industry != "Any":
        st.markdown(f"Industry: **{selected_industry}**")
    
    st.markdown("---")
    
    # Display the content ideas
    content_ideas = st.session_state.content_ideas.get("content_ideas", [])
    
    if content_ideas:
        idea_cols = st.columns(2)
        
        for i, idea in enumerate(content_ideas):
            col_idx = i % 2
            
            with idea_cols[col_idx]:
                with st.container(border=True):
                    st.subheader(f"{i+1}. {idea.get('title', f'Idea {i+1}')}")
                    st.markdown(idea.get("description", ""))
                    
                    if "best_formats" in idea:
                        st.markdown("**Best Formats:**")
                        formats = idea.get("best_formats", [])
                        for fmt in formats:
                            st.markdown(f"✓ {fmt}")
                    
                    if "hashtags" in idea:
                        st.markdown("**Suggested Hashtags:**")
                        hashtags = idea.get("hashtags", [])
                        hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                        st.code(hashtag_text)
                    
                    st.markdown("---")
    else:
        st.info("No content ideas were generated. Try adjusting your platform or goal selection.")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Generate New Ideas", use_container_width=True):
            # This would trigger the generation process again
            st.rerun()
    
    with col2:
        if st.button("💾 Save Ideas", use_container_width=True):
            st.success("Ideas saved to your account!")
    
    with col3:
        if st.button("📤 Export Ideas", use_container_width=True):
            st.download_button(
                label="Download as Text",
                data="\n\n".join([f"{i+1}. {idea.get('title', '')}\n{idea.get('description', '')}" for i, idea in enumerate(content_ideas)]),
                file_name="content_ideas.txt",
                mime="text/plain"
            )

else:
    # Show dashboard for logged-in users without generated content
    st.title(f"Welcome back, {st.session_state.user_name}! 👋")
    st.caption(f"Last login: {st.session_state.last_login}")
    
    st.markdown("## Your AI Content Assistant")
    
    # Instructions
    st.info("**To generate content ideas:**\n1. Select your platform in the sidebar\n2. Choose your content goal\n3. Click 'Generate Ideas'")
    
    # Featured platforms
    st.markdown("### Featured Platforms")
    platform_col1, platform_col2, platform_col3 = st.columns(3)
    
    platform_images = {
        "Instagram": "https://images.unsplash.com/photo-1611262588024-d12430b98920",
        "TikTok": "https://images.unsplash.com/photo-1633675254053-d96c7668c3b8",
        "YouTube": "https://images.unsplash.com/photo-1611162616475-46b635cb6868",
    }
    
    with platform_col1:
        st.image(platform_images["Instagram"], caption="Instagram")
        if st.button("Generate for Instagram", key="insta_button"):
            st.session_state.selected_platform = "Instagram"
            st.rerun()
    
    with platform_col2:
        st.image(platform_images["TikTok"], caption="TikTok")
        if st.button("Generate for TikTok", key="tiktok_button"):
            st.session_state.selected_platform = "TikTok"
            st.rerun()
    
    with platform_col3:
        st.image(platform_images["YouTube"], caption="YouTube")
        if st.button("Generate for YouTube", key="youtube_button"):
            st.session_state.selected_platform = "YouTube"
            st.rerun()
    
    # Trending Topics Preview
    st.markdown("### Current Trending Topics")
    st.caption("Based on our AI analysis across all platforms")
    
    # Simulated trending topics
    trending_topics = [
        "Sustainable living hacks", 
        "Day-in-the-life content", 
        "Creator economy insights",
        "AI tools for productivity", 
        "Mindfulness practices", 
        "Behind-the-scenes content",
        "Personal finance tips", 
        "Skill-sharing tutorials", 
        "Authentic storytelling"
    ]
    
    trend_cols = st.columns(3)
    for i, topic in enumerate(trending_topics):
        with trend_cols[i % 3]:
            st.markdown(f"• {topic}")
    
    # Recent Activity
    st.markdown("### Your Recent Activity")
    
    # Simulated recent activity
    if random.random() > 0.5:
        st.info("Generate your first content ideas to see your activity here!")
    else:
        st.markdown("**Last Generated:**")
        st.markdown("Instagram content ideas focused on Engagement (4 days ago)")
        
        st.markdown("**Popular Topic:**")
        st.markdown("Your most-used topic: Behind-the-scenes content")