#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
Created on Oct 2, 2024

This is the main script of the Legislation Tracker. To run the app locally, run: 'streamlit run main.py'
"""

import streamlit as st
import datetime
from utils.authentication import login_page, signup_page, logout, get_organization_by_id, is_user_in_working_group


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

        Copyright (c) {datetime.datetime.now().year} TechEquity. [Terms of Use](https://github.com/techequitycollaborative/legislation-tracker/blob/main/LICENSE)
        """
    }
)

# Add logo
logo = './assets/logo.png'
st.logo(
        logo,
        #link="https://calegtracker.org/home"
        )

# Extract query parameters
query_params = st.query_params
nav_page = query_params.get("nav", "home")  # Default to "home" if no query param is set

# Check if the user has triggered a logout and rerun if necessary -- TURNED OFF BC THIS IS HANDLED IN THE LOGOUT() FUNCTION DIRECTLY!
#if "logged_out" in st.session_state and st.session_state.logged_out:
#    st.session_state.clear()
#    st.rerun()  # Use experimental_rerun() to restart execution

# Main authentication flow
if 'authenticated' not in st.session_state:
    # Logic for checking if the user is logged in in order to keep them logged in across sessions via cookies -- TURNED OFF FOR NOW BC THIS IS STILL IN DEVELOPMENT!!
    #email = get_logged_in_user()
    #if email:
    #    user = get_user(email)
    #    if user:
    #        st.session_state['authenticated'] = True
    #        st.session_state['user_id'] = user[0]
    #        st.session_state['user_name'] = user[1]
    #        st.session_state['user_email'] = user[2]
    #        st.session_state['org_id'] = user[4]
    #        org = get_organization_by_id(user[4])
    #        if org:
    #            st.session_state['org_name'] = org[1]
    #        st.rerun()
    
    if st.session_state.get('show_signup', False):
        signup_page()
    else:
        login_page()

else:
    # Get org and user info
    org_id = st.session_state.get('org_id')
    user_org = st.session_state.get('org_name')
    user_org_nickname = st.session_state.get('nickname')
    org_info = get_organization_by_id(org_id) if org_id else None
    user_name = st.session_state['user_name']
    first_name = user_name.split()[0] # get first name from user name
    
    # Check if the user is in the Working Group
    user_email = st.session_state.get('user_email')
    user_in_working_group = is_user_in_working_group(user_email)
    st.session_state['working_group'] = user_in_working_group  # Store in session state for easy access

    # Create grouped navigation structure
    pages = {
        "": [
            st.Page('home.py', title='Home', icon='🏠', url_path='home', default=(nav_page == "home")), 
        ],
        "Legislative Info": [
            st.Page('bills.py', title='Bills', icon='📝', url_path='bills'),
            st.Page('legislators.py', title='Legislators', icon='💼', url_path='legislators'),
            st.Page('committees.py', title='Committees', icon='🗣', url_path='committees'),
            st.Page('calendar_page.py', title='Calendar', icon='📅', url_path='calendar'),
        ],
        "Bill Tracking Tools": [
            st.Page('advocacy_hub.py', title='Advocacy Hub', icon='📣', url_path='advocacy_hub'),
            st.Page(
                'org_dashboard.py',
                title=f"{user_org_nickname} Dashboard" if org_info else "Organization Dashboard",
                icon='🏢',
                url_path='org_dashboard',
                default=False
            ),
            st.Page('my_dashboard.py', title='My Dashboard', icon='📌', url_path='my_dashboard'),
        ] + (
            [st.Page('ai_wg_dashboard.py', title='AI Working Group Dashboard', icon='🤝', url_path='ai_working_group_dashboard')]
            if user_in_working_group else []
        ),
    }

    # Build grouped sidebar navigation
    pg = st.navigation(pages)

    # Clear query parameters after successful login to prevent infinite loops
    if st.session_state.get('connected'):
        st.query_params.clear()

    # Run the correct page based on query parameter navigation
    pg.run()

    # Additional navigation bar items
    st.sidebar.markdown("### Account")
    st.sidebar.markdown(f"**User:** {user_name}")
    st.sidebar.markdown(f"**Email:** {user_email}")
    st.sidebar.markdown(f"**Organization:** {user_org_nickname}")
    
    # Add the logout button to the bottom of the navigation bar
    #st.sidebar.markdown("<br>" * 16, unsafe_allow_html=True)
    if st.sidebar.button('Log out', key='logout'):
        logout()