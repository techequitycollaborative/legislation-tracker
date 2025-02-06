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
    redirect_uri='https://leg-tracker-wqjxl.ondigitalocean.app/Home',  # Change to 'http://localhost:8501/Home' for local development
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


    # Pages for navigation bar
    pages = [
        {"label": "Bills", "icon": "📝", "description": "Explore and search for legislative bills.", "page": "pages/1_Bills.py"},
        {"label": "Legislators", "icon": "💼", "description": "View information about legislators and their activity.", "page": "pages/2_Legislators.pyy"},
        {"label": "Calendar", "icon": "📅", "description": "Check the legislative calendar for upcoming events.", "page": "pages/3_Calendar.py"},
        {"label": "My Dashboard", "icon": "📌", "description": "Manage and track your selected bills.", "page": "pages/4_Dashboard.py"},
    ]


    # Add pages to the sidebar
    for item in pages:
        st.sidebar.markdown(f"### {item['label']}")
        st.sidebar.markdown(item['description'])
        st.sidebar.markdown("")  # Blank line between pages
        st.sidebar.button(f"Go to {item['label']}", key=item["label"], on_click=lambda page=item["page"]: st.session_state.page_to_load(page))


    # Run the pages
    if 'page_to_load' in st.session_state:
        page = st.session_state.page_to_load
        exec(open(page).read())  # Dynamically load and run the selected page


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




