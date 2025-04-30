"""
Settings page for TrendVision AI application.
Allows users to configure application settings, manage saved reports,
and customize the user experience.
"""

import streamlit as st
import os
import json
from datetime import datetime

import database as db
import utils
from data_sources import load_data_sources

def app():
    """Main function for the settings page."""
    
    st.title("Settings")
    
    # Initialize session state for username if not exists
    if 'username' not in st.session_state:
        st.session_state.username = "default_user"
    
    # Get user preferences from database
    user_prefs = db.get_user_preferences(st.session_state.username)
    
    with st.sidebar:
        st.header("Settings Menu")
        page = st.radio(
            "Select Settings Category",
            ["User Profile", "Appearance", "Data Sources", "Saved Reports", "Export Options"]
        )
    
    if page == "User Profile":
        display_user_profile(user_prefs)
    elif page == "Appearance":
        display_appearance_settings(user_prefs)
    elif page == "Data Sources":
        display_data_source_settings(user_prefs)
    elif page == "Saved Reports":
        display_saved_reports()
    elif page == "Export Options":
        display_export_options(user_prefs)

def display_user_profile(user_prefs):
    """Display and manage user profile settings."""
    st.header("User Profile")
    
    # User information
    username = st.text_input("Username", st.session_state.username)
    email = st.text_input("Email", user_prefs.get("email", ""))
    
    # Save changes
    if st.button("Save Profile"):
        # Update username in session state
        st.session_state.username = username
        
        # Update preferences
        user_prefs["email"] = email
        
        # Save to database
        if db.save_user_preferences(username, user_prefs):
            st.success("Profile saved successfully!")
        else:
            st.error("Failed to save profile. Please try again.")

def display_appearance_settings(user_prefs):
    """Display and manage appearance settings."""
    st.header("Appearance Settings")
    
    # Theme settings
    st.subheader("Theme")
    
    # Dark mode toggle
    dark_mode = st.toggle("Dark Mode", user_prefs.get("dark_mode", False))
    
    # Color scheme
    color_schemes = ["Default", "Blues", "Greens", "Reds", "Purples", "Grayscale"]
    color_scheme = st.selectbox(
        "Color Scheme", 
        color_schemes, 
        index=color_schemes.index(user_prefs.get("color_scheme", "Default"))
    )
    
    # Chart style
    chart_styles = ["Default", "Minimalist", "Bold", "Pastel", "Dark"]
    chart_style = st.selectbox(
        "Chart Style", 
        chart_styles,
        index=chart_styles.index(user_prefs.get("chart_style", "Default"))
    )
    
    # Save changes
    if st.button("Save Appearance Settings"):
        # Update preferences
        user_prefs["dark_mode"] = dark_mode
        user_prefs["color_scheme"] = color_scheme
        user_prefs["chart_style"] = chart_style
        
        # Apply theme
        utils.apply_theme(dark_mode)
        
        # Save to database
        if db.save_user_preferences(st.session_state.username, user_prefs):
            st.success("Appearance settings saved successfully!")
        else:
            st.error("Failed to save settings. Please try again.")

def display_data_source_settings(user_prefs):
    """Display and manage data source settings."""
    st.header("Data Sources")
    
    # Available data sources
    all_sources = load_data_sources()
    
    # Display saved sources
    st.subheader("Saved Data Sources")
    saved_sources = db.get_data_sources(st.session_state.username)
    
    if not saved_sources:
        st.info("You don't have any saved data sources yet.")
    else:
        for i, source in enumerate(saved_sources):
            with st.expander(f"{source['name']} ({source['source_type']})"):
                st.json(source['configuration'])
                if st.button(f"Delete Source", key=f"delete_source_{i}"):
                    # TODO: Implement delete functionality
                    st.info("Delete functionality will be implemented in a future update.")
    
    # Add new data source
    st.subheader("Save Current Data Source")
    
    # Check if a data source is currently loaded
    if 'current_data_source' in st.session_state and st.session_state.current_data_source:
        source_config = st.session_state.current_data_source
        source_type = source_config.get("type", "unknown")
        
        # Display current source info
        st.write(f"Current source type: {source_type}")
        
        # Input for saving
        source_name = st.text_input("Source Name", f"My {source_type.capitalize()} Source")
        
        if st.button("Save Current Source"):
            # Save to database
            source_id = db.save_data_source(
                st.session_state.username,
                source_name,
                source_type,
                source_config
            )
            
            if source_id:
                st.success(f"Data source '{source_name}' saved successfully!")
            else:
                st.error("Failed to save data source. Please try again.")
    else:
        st.info("No data source is currently loaded. Load a data source from the main page first.")

def display_saved_reports():
    """Display and manage saved reports."""
    st.header("Saved Reports")
    
    # Get saved reports from database
    reports = db.get_reports(st.session_state.username)
    
    if not reports:
        st.info("You don't have any saved reports yet.")
    else:
        # Display reports
        for i, report in enumerate(reports):
            with st.expander(f"{report['title']} - {report['visualization_type']}"):
                st.write(f"**Description:** {report['description'] or 'No description'}")
                st.write(f"**Created:** {report['created_at'].strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Last Updated:** {report['updated_at'].strftime('%Y-%m-%d %H:%M')}")
                
                # View configuration button
                if st.button(f"View Configuration", key=f"view_config_{i}"):
                    st.json(report['configuration'])
                
                # Load report button
                if st.button(f"Load Report", key=f"load_report_{i}"):
                    # Set the configuration in session state
                    st.session_state.report_config = report['configuration']
                    st.success("Report loaded! Go to the appropriate analysis page to view it.")
                
                # Delete report button
                if st.button(f"Delete Report", key=f"delete_report_{i}"):
                    # TODO: Implement delete functionality
                    st.info("Delete functionality will be implemented in a future update.")
    
    # Save current report/visualization
    st.subheader("Save Current Report")
    
    if 'current_visualization' in st.session_state and st.session_state.current_visualization:
        # Report details
        report_title = st.text_input("Report Title", "My Report")
        report_description = st.text_area("Description", "")
        
        if st.button("Save Current Report"):
            # Get current configuration
            config = {
                "data_source": st.session_state.get("current_data_source", {}),
                "visualization_type": st.session_state.get("current_visualization_type", "trend"),
                "chart_type": st.session_state.get("current_chart_type", "line"),
                "start_date": st.session_state.get("start_date", "").strftime("%Y-%m-%d") if isinstance(st.session_state.get("start_date"), datetime) else "",
                "end_date": st.session_state.get("end_date", "").strftime("%Y-%m-%d") if isinstance(st.session_state.get("end_date"), datetime) else "",
                "processing_operations": st.session_state.get("processing_operations", [])
            }
            
            # Save to database
            report_id = db.save_report(
                st.session_state.username,
                report_title,
                report_description,
                config,
                st.session_state.get("current_visualization_type", "trend")
            )
            
            if report_id:
                st.success(f"Report '{report_title}' saved successfully!")
            else:
                st.error("Failed to save report. Please try again.")
    else:
        st.info("No visualization is currently active. Create a visualization first.")

def display_export_options(user_prefs):
    """Display and manage export options."""
    st.header("Export Options")
    
    # File format options
    st.subheader("Default Export Format")
    
    formats = ["CSV", "Excel", "JSON", "Image (PNG)", "PDF"]
    default_format = st.selectbox(
        "Default Format", 
        formats,
        index=formats.index(user_prefs.get("default_export_format", "CSV"))
    )
    
    # Image export resolution
    st.subheader("Image Export Settings")
    
    width = st.number_input(
        "Default Width (pixels)", 
        min_value=500, 
        max_value=3000, 
        value=user_prefs.get("export_width", 1200)
    )
    
    height = st.number_input(
        "Default Height (pixels)", 
        min_value=500, 
        max_value=3000, 
        value=user_prefs.get("export_height", 800)
    )
    
    # Save changes
    if st.button("Save Export Settings"):
        # Update preferences
        user_prefs["default_export_format"] = default_format
        user_prefs["export_width"] = width
        user_prefs["export_height"] = height
        
        # Save to database
        if db.save_user_preferences(st.session_state.username, user_prefs):
            st.success("Export settings saved successfully!")
        else:
            st.error("Failed to save settings. Please try again.")

# Run the app
if __name__ == "__main__":
    app()