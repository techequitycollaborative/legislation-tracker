#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sketching Leg Tracker using Streamlit
Created on Oct 2, 2024
@author: danyasherbini

This script sketches a prototype of the Legislation Tracker app using 
Streamlit, an open-source framework to build data apps in Python.
"""

import streamlit as st
from streamlit_google_auth import Authenticate

# Set page config
st.set_page_config(page_title='Legislation Tracker', layout='wide')

# Add logo
logo = './assets/logo.png'
st.logo(
        logo,
        link="https://techequity.us")

# Google Authenticator Setup -- cookies are not being stored properly; need to fix this
authenticator = Authenticate(
    secret_credentials_path='google_credentials.json',
    cookie_name='my_cookie_name',
    cookie_key='this_is_secret',
    redirect_uri='http://localhost:8501',  # Change this for production
    cookie_expiry_days=30,
)

# Authenticate user
authenticator.check_authentification()

# If the user is not authenticated, show login page
if not st.session_state.get('connected', False):
    # Set the login page title + center it
    st.markdown(
    """
    <h3 style="text-align: center;">Login to the CA Legislation Tracker</h3>
    """, 
    unsafe_allow_html=True)
    # Show the login button and handle the login
    authenticator.login()

else:
    # User is authenticated, show the main content
    user_info = st.session_state['user_info']
    user_email = user_info.get('email')  # This will be used as the unique user identifier


    # Add page navigation for the authenticated user
    # Pages
    welcome = st.Page('welcome.py', title='Welcome', icon='📜')
    bills_tabs_expander = st.Page('bills_tabs.py', title='Bills - Tabs + Expander', icon='📝')
    bills_tabs_dialog = st.Page('bills_tabs_dialog.py', title='Bills - Tabs + Dialog', icon='📝')
    bills_multi = st.Page('bills_multiselect.py', title='Bills - Multiselect + Text', icon='📝')
    bills_topic = st.Page('bills_topic.py', title='Bills', icon='📝')
    legislators = st.Page('legislators.py', title='Legislators', icon='💼')
    calendar = st.Page('calendar2.py', title='Calendar', icon='📅')
    dashboard = st.Page('dashboard.py', title='My Dashboard', icon='📌')

    # Build navigation bar
    pg = st.navigation([welcome, bills_topic, legislators, calendar, dashboard])

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


