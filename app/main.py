#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
Created on Oct 2, 2024

This is the main script of the Legislation Tracker. To run the app locally, run: 'streamlit run main.py'
"""

import streamlit as st
import datetime
from utils.authentication import login_page, signup_page, logout, get_organization_by_id


# Get the current year
current_year = datetime.datetime.now().year

# Page configuration
st.set_page_config(
    page_title='CA Legislation Tracker',
    page_icon=':scales:',
    layout='wide',
    initial_sidebar_state='collapsed',
    menu_items={
        'Get help': 'mailto:info@techequity.us',
        'Report a bug': 'https://github.com/techequitycollaborative/legislation-tracker/issues',
        'About': f"""
        The CA Legislation Tracker is a project by [TechEquity](https://techequity.us). 

        **Developer Credits**: Danya Sherbini, Jessica Wang
        
        Special thanks to Matt Brooks and the team of volunteers who contributed to the previous version of this tool.

        Copyright (c) {current_year} TechEquity. [Terms of Use](https://github.com/techequitycollaborative/legislation-tracker/blob/main/LICENSE)
        """
    }
)

# Add logo
logo = './assets/logo.png'
st.logo(
        logo,
        link="https://techequity.us")

# Extract query parameters
query_params = st.query_params
nav_page = query_params.get("nav", "home")  # Default to "home" if no query param is set

# Check if the user has triggered a logout and rerun if necessary
if "logged_out" in st.session_state and st.session_state.logged_out:
    st.session_state.clear()
    st.rerun()  # Use experimental_rerun() to restart execution

# Main authentication flow remains largely the same
if 'authenticated' not in st.session_state:
    if st.session_state.get('show_signup', False):
        signup_page()
    else:
        login_page()
else:
    # Get org_id from session state
    org_id = st.session_state.get('org_id')
    user_org = st.session_state.get('user_org')
    
    # Get organization info using the correct function
    org_info = get_organization_by_id(org_id) if org_id else None

    # Add page navigation for the authenticated user
    home = st.Page('home.py', title='Home', icon='🏠', url_path='home', default=(nav_page == "home")) 
    bills = st.Page('bills.py', title='Bills', icon='📝', url_path='bills')
    legislators = st.Page('legislators.py', title='Legislators', icon='💼', url_path='legislators')
    calendar = st.Page('calendar_page.py', title='Calendar', icon='📅', url_path='calendar')
    dashboard = st.Page('my_dashboard.py', title='My Dashboard', icon='📌', url_path='my_dashboard')

    if org_info:
        org_dashboard = st.Page("org_dashboard.py", title=f"{org_info[1]} Dashboard", icon="🏢", url_path="org_dashboard")
    else:
        org_dashboard = st.Page("org_dashboard.py", title="Organization Dashboard", icon="🏢", url_path="org_dashboard", default=False)

    # Build navigation bar
    pg = st.navigation([home, bills, legislators, calendar, dashboard, org_dashboard])

    # Clear query parameters after successful login to prevent infinite loops
    if st.session_state.get('connected'):
        st.query_params.clear()

    # Run the correct page based on query parameter navigation
    pg.run()

    # Add the logout button to the bottom of the navigation bar
    st.sidebar.markdown("<br>" * 16, unsafe_allow_html=True)  # Push logout button down
    if st.sidebar.button('Log out', key='logout'):
        logout()