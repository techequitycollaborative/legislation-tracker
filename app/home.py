#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
home.py
Created on January 23, 2025

Home page for the Legislation Tracker.
"""

import streamlit as st

############################ TITLE & WELCOME TEXT #############################

# Page title
st.title('Welcome to the California Legislation Tracker')

st.markdown("""
Tired of clicking through endless rabbit holes on California legislative websites? Or scrolling through long PDF files? You're in luck! The CA Legislation Tracker is a comprehensive source for California bill data, pulling from various sources and updating in real time. 
""")


############################ HOW TO USE THE APP #############################
st.divider()
st.header("How to Use This App")

# key features
st.markdown(
"""
### Key Features
- **Explore Bills:** Use the search and filtering tools to find bills relevant to your work.
- **Track Progress:** Monitor the status and history of bills in real time.
- **Build Your Dashboard:** Add bills to your private dashboard for quick access.
""",
unsafe_allow_html=True)
    
# Pages
st.markdown("### Pages")

# Access user info
org_id = st.session_state.get('org_id')
org_name = st.session_state['org_name']

pages = [
        {"label": "Bills", "icon": "📝", "description": "Search, sort, and filter bills.", "page": "bills.py"},
        {"label": "Legislators", "icon": "💼", "description": "View information about legislators and their activity.", "page": "legislators.py"},
        {"label": "Committees", "icon": "🗣", "description": "View information about committees and their activity.", "page": "committees.py"},
        {"label": "Calendar", "icon": "📅", "description": "Check the legislative calendar for upcoming events.", "page": "calendar_page.py"},
        {"label": "My Dashboard", "icon": "📌", "description": "Manage and track your selected bills.", "page": "my_dashboard.py"},
        {"label": f"{org_name}'s Dashboard", "icon": "🏢", "description": "Collaborate with your team to track bills together.", "page": "org_dashboard.py"},
    ]

# Loop through pages and display them as streamlit page_link buttons
for item in pages:
    col1, col_space, col2 = st.columns([1, 0.1, 4])  # Thin blank column between the two
    with col1:
        st.page_link(item["page"], label=item["label"], icon=item["icon"])
    with col2:
        st.markdown(item["description"])



############################# ABOUT TECH EQUITY ###############################
st.divider()

st.markdown("""
## FAQs
""")

st.expander("Where is the data sourced from?", expanded=False).markdown("We source data from the OpenStates REST API and directly from the California LegInfo websites.")

st.expander("How often is the data updated?", expanded=False).markdown("Data is updated twice per day: first between 2-3 AM Pacific Time and again between 2-3 PM Pacific Time.")

st.expander("I noticed some data was incorrect or outdated.", expanded=False).markdown("This is possible. The California legislative websites may contain errors, or may not be updated on a timely basis, so there may be discrepencies from time to time. We do our best to ensure accuracy. However, we encourage advocacy professionals to double check information such as timing and location of Assembly and Senate meetings and hearings, or other time-sensitive information. If you notice recurring issues, please contact info@techequity.us.")

