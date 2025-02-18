#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sketching Leg Tracker using Streamlit
Created on Oct 2, 2024
@author: danyasherbini

This script sketches a prototype of the Legislation Tracker app using 
Streamlit, an open-source framework to build data apps in Python.
"""

import os
import platform
import streamlit as st
from streamlit_google_auth import Authenticate
from utils.auth import fetch_google_credentials_from_droplet

# Page configuration
st.set_page_config(
    page_title='CA Legislation Tracker',
    page_icon=':scales:',
    layout='wide',
    initial_sidebar_state='collapsed',
    menu_items={
        'Get help': None,
        'Report a bug': 'https://github.com/techequitycollaborative/legislation-tracker/issues',
        'About': """
        The CA Legislation Tracker is a project by [TechEquity](https://techequity.us). Special thanks to Danya Sherbini and Jessica Wang for their work on this project, as well as former TechEquity volunteers who worked on the previous version of this tool.
        
        Copyright (c) 2025 TechEquity.


        [Terms of Use](https://github.com/techequitycollaborative/legislation-tracker/blob/main/LICENSE)
        """
    }
)

# Add logo
logo = './assets/logo.png'
st.logo(
        logo,
        link="https://techequity.us")

# Ensure the credentials are fetched and available locally
google_credentials_path = fetch_google_credentials_from_droplet()

# Google authenticator setup
authenticator = Authenticate(
    secret_credentials_path = 'auth/google_credentials.json', # replace with 'auth/google_credentials.json' for local development
    cookie_name='my_cookie_name',
    cookie_key='this_is_secret',
    # This is the URL to redirect to after a successful login
    redirect_uri='http://localhost:8501/?nav=home',  # Change to 'http://localhost:8501/?nav=home' for local development
    cookie_expiry_days=30,
)

# Authenticate user
authenticator.check_authentification()

# Extract query parameters
query_params = st.query_params
nav_page = query_params.get("nav", "home")  # Default to "home" if no query param is set

# Define login page as a function
def login_page():
    # Set the login page title + center it
    st.markdown(
    """
    <h3 style="text-align: center;">Login to the CA Legislation Tracker</h3>
    """, 
    unsafe_allow_html=True)
    # Show the login button and handle the login
    authenticator.login()

# If the user is not authenticated, show login page
if not st.session_state.get('connected', False):
    # Show the login page
    login_page()

else:
    # User is authenticated, show the main content
    user_info = st.session_state['user_info']
    user_email = user_info.get('email')  # This will be used as the unique user identifier

    # Add page navigation for the authenticated user
    #login = st.Page(login_page, title='Login', icon='🔑', url_path='login', default=(nav_page == "login")) # turn off login page
    home = st.Page('home.py', title='Home', icon='🏠', url_path='home', default=(nav_page == "home")) # Set page to default so it doesn't appear in the navigation menu. This will also ignore the url path
    bills = st.Page('bills_topic.py', title='Bills', icon='📝', url_path='bills')
    legislators = st.Page('legislators.py', title='Legislators', icon='💼', url_path='legislators')
    calendar = st.Page('calendar2.py', title='Calendar', icon='📅', url_path='calendar')
    dashboard = st.Page('dashboard.py', title='My Dashboard', icon='📌', url_path='dashboard')

    # Build navigation bar
    pg = st.navigation([home, bills, legislators, calendar, dashboard])

    # Clear query parameters after successful login to prevent infinite loops
    if st.session_state.get('connected'):
        st.query_params.clear()

    # Run the correct page based on query parameter navigation
    pg.run()

    # Add the logout button to the bottom of the navigation bar
    st.sidebar.markdown("<br>" * 16, unsafe_allow_html=True)  # Push logout button down
    st.sidebar.button('Log out', key='logout', on_click=authenticator.logout)




