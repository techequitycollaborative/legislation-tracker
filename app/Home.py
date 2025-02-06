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
    redirect_uri='https://leg-tracker-wqjxl.ondigitalocean.app/Home',  # Change to 'http://localhost:8501/welcome' for local development
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

    ############################ START OF WELCOME CONTENT #############################

    # Page title
    st.title('Welcome')


    st.markdown("""
    ## About the California Legislation Tracker
    Although information about California legislative bills is publicly available, it's spread across numerous state senate and assembly websites, making it difficult to parse or collect. The legislation tracker serves as a comprehensive source for California bill data, pulling data from various sources and updating in real time. 
    """)


    ############################ HOW TO USE THE APP #############################
    st.divider()
    st.header("How to Use This App")

    # key features
    st.markdown(
    """
    ### Key Features:
    - **Explore Bills:** Use the search and filtering tools to find legislative bills that matter to you.
    - **Track Progress:** Monitor the status and history of selected bills in real time.
    - **Build Your Dashboard:** Add bills to your personalized dashboard for quick access.
    """,
    unsafe_allow_html=True)
        
    # Pages
    st.markdown("### Pages:")

    pages = [
        {"label": "Bills", "icon": "📝", "description": "Explore and search for legislative bills.", "page": "pages/1_📝 Bills.py"},
        {"label": "Legislators", "icon": "💼", "description": "View information about legislators and their activity.", "page": "pages/2_💼 Legislators.pyy"},
        {"label": "Calendar", "icon": "📅", "description": "Check the legislative calendar for upcoming events.", "page": "pages/3_📅 Calendar.py"},
        {"label": "My Dashboard", "icon": "📌", "description": "Manage and track your selected bills.", "page": "pages/4_📌 My Dashboard.py"},
    ]

    # Loop through and display the data in columns
    for item in pages:
        col1, col_space, col2 = st.columns([1, 0.1, 4])  # Thin blank column between the two
        with col1:
            st.page_link(item["page"], label=item["label"], icon=item["icon"])
        with col2:
            st.markdown(item["description"])

    # Add pages to the sidebar
    for item in pages:
        st.sidebar.markdown(f"### {item['label']}")
        st.sidebar.markdown(item['description'])
        st.sidebar.markdown("")  # Blank line between pages
        st.sidebar.button(f"Go to {item['label']}", key=item["label"], on_click=lambda page=item["page"]: st.session_state.page_to_load(page))


    ############################# ABOUT TECH EQUITY ###############################
    st.divider()

    st.markdown("""
    ## About TechEquity
    TechEquity was founded in 2016 to answer a simple but ambitious question: what would it take for the growth of the tech industry to benefit everyone? We raise public consciousness about economic equity issues resulting from the tech industry’s products and practices and advocate for change that ensures tech’s evolution benefits everyone.
    If you'd like to learn more about us, visit [our website](https://techequity.us).
    """)
    
    ############################# END OF WELCOME CONTENT ###############################

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


