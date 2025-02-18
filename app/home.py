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
Tired of clicking through endless rabbit holes on California legislative websites? Or scrolling through long PDF files? You're in luck! The CA Legislation Tracker serves as a comprehensive source for California bill data, pulling from various sources and updating in real time. 
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
- **Build Your Dashboard:** Add bills to your personalized dashboard for quick access.
""",
unsafe_allow_html=True)
    
# Pages
st.markdown("### Pages")

pages = [
        {"label": "Bills", "icon": "📝", "description": "Search, sort, and filter bills.", "page": "bills_topic.py"},
        {"label": "Legislators", "icon": "💼", "description": "View information about legislators and their activity.", "page": "legislators.py"},
        {"label": "Calendar", "icon": "📅", "description": "Check the legislative calendar for upcoming events.", "page": "calendar2.py"},
        {"label": "My Dashboard", "icon": "📌", "description": "Manage and track your selected bills.", "page": "dashboard.py"},
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
Add some FAQs here.
""")
