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
import streamlit as st
from streamlit_google_auth import Authenticate
from utils.auth import fetch_google_credentials_from_droplet



# Add logo
logo = './assets/logo.png'
st.logo(
        logo,
        link="https://techequity.us")

# Ensure the credentials are fetched and available locally
google_credentials_path = fetch_google_credentials_from_droplet()

# Google Authenticator Setup -- cookies are not being stored properly; need to fix this
authenticator = Authenticate(
    secret_credentials_path = google_credentials_path, # replace with 'auth/google_credentials.json' for local development
    cookie_name='my_cookie_name',
    cookie_key='this_is_secret',
    # This is the URL to redirect to after a successful login
    redirect_uri='https://leg-tracker-wqjxl.ondigitalocean.app/home',  # Change to 'http://localhost:8501/home' for local development
    cookie_expiry_days=30,
)

# Authenticate user
authenticator.check_authentification()

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
    # Pages
    login = st.Page(login_page, title='Login', icon='🔑', url_path='login', default=True) # Set page to default so it doesn't appear in the navigation menu. This will also ignore the url path
    home = st.Page('home.py', title='Home', icon='🏠', url_path='home')
    bills = st.Page('bills_topic.py', title='Bills', icon='📝', url_path='bills')
    legislators = st.Page('legislators.py', title='Legislators', icon='💼', url_path='legislators')
    calendar = st.Page('calendar2.py', title='Calendar', icon='📅', url_path='calendar')
    dashboard = st.Page('dashboard.py', title='My Dashboard', icon='📌', url_path='dashboard')

    # Build navigation bar
    pg = st.navigation([login, home, bills, legislators, calendar, dashboard])

    # Run the pages
    pg.run()


    # Add the logout button to the bottom of the navigation bar
    # Adding spaces to push the button to the bottom (this is a hack, could be improved)
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.markdown('')
    st.sidebar.button('Log out', key='logout', on_click=authenticator.logout)




