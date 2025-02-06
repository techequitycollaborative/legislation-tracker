#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Welcome Page
Created on January 23, 2025
@author: danyasherbini

Welcome page for the legislation tracker
"""


import streamlit as st

############################ TITLE & WELCOME TEXT #############################

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



############################# ABOUT TECH EQUITY ###############################
st.divider()

st.markdown("""
## About TechEquity
TechEquity was founded in 2016 to answer a simple but ambitious question: what would it take for the growth of the tech industry to benefit everyone? We raise public consciousness about economic equity issues resulting from the tech industry’s products and practices and advocate for change that ensures tech’s evolution benefits everyone.
If you'd like to learn more about us, visit [our website](https://techequity.us).
""")
