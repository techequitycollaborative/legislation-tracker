#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
home.py
Created on January 23, 2025

Home page for the Legislation Tracker.
"""

import streamlit as st
from utils.css_utils import load_css_with_fallback, DEFAULT_FALLBACK_CSS

# Load custom CSS with fallback
load_css_with_fallback(
    primary_css='styles/home.css',
    fallback_css=DEFAULT_FALLBACK_CSS
)

############################ TITLE & WELCOME TEXT #############################

# Page title
st.title('Welcome to the CA Legislation Tracker!')

############################### ABOUT THE APP ###############################
st.markdown(" ") 
st.markdown('<h3 class="section-header">About</h3>', unsafe_allow_html=True)
st.markdown(" ") 

st.markdown(
"""
The California Legislation Tracker is a custom web application built by [TechEquity](https://techequity.us) to help advocacy organizations enhance their legislative tracking and advocacy efforts. Key features include:
""",
unsafe_allow_html=True)


# Custom HTML for equal height containers with colored bars
col1, col2, col3, col4 = st.columns([1,1,1,1])

with col1:
    st.markdown("""
    <div class="feature-card card-1">
        <div class="feature-title">Live Data Updates</div>
        <div class="feature-description">
            Automatically collects and displays California legislative data and updates in real time.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card card-2">
        <div class="feature-title">Centralized Information Hub</div>
        <div class="feature-description">
            Consolidated bill data in one platform, limiting the need to search across disparate sources.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card card-3">
        <div class="feature-title">Advanced Search & Filters</div>
        <div class="feature-description">
            Search and filter data by various fields in order to more easily find specific bill information.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card card-4">
        <div class="feature-title">Bill Tracking</div>
        <div class="feature-description">
            Track your organization's advocacy work through auto-generated fields and custom data entry.
        </div>
    </div>
    """, unsafe_allow_html=True)

    
############################### PAGE DESCRIPTIONS ################################
st.markdown(" ") 
st.markdown('<h3 class="section-header">Pages</h3>', unsafe_allow_html=True)
st.markdown(" ") 

# Access user info
org_id = st.session_state.get('org_id')
org_name = st.session_state['org_name']

# Grouped pages
grouped_pages = {
    "Legislative Info": {
        "description": "Access legislative data, all in one place.",
        "pages": [
            {"label": "Bills", "icon": "📝", "description": "Search, sort, and filter all bills, and add them to your dashboards for detailed tracking.", "page": "bills.py"},
            {"label": "Legislators", "icon": "💼", "description": "View information about legislators and their staff.", "page": "legislators.py"},
            {"label": "Committees", "icon": "🗣", "description": "View information about committees, their members, and upcoming hearing dates.", "page": "committees.py"},
            {"label": "Calendar", "icon": "📅", "description": "Check the legislative calendar for upcoming legislative deadlines and bill-specific events.", "page": "calendar_page.py"},
        ]
    },
    "Bill Tracking Tools": {
        "description": "Keep track of bills and collaborate across organizations.",
        "pages": [
            {"label": "Advocacy Hub", "icon": "📣", "description": "View custom advocacy information from fellow organizations.", "page": "advocacy_hub.py"},
            {"label": f"{org_name}'s Dashboard", "icon": "🏢", "description": "Collaborate with your team to track bills together on a shared organizational dashboard.", "page": "org_dashboard.py"},
            {"label": "My Dashboard", "icon": "📌", "description": "Manage and track bills you care about on your personal dashboard.", "page": "my_dashboard.py"},
        ]
    }
}

# Render grouped page links
for group, content in grouped_pages.items():
    st.markdown(f"**{group}**")
    st.markdown(f"<span style='color:gray'>{content['description']}</span>", unsafe_allow_html=True)
    
    for item in content["pages"]:
        col1, col_space, col2 = st.columns([1, 0.1, 4])
        with col1:
            st.page_link(item["page"], label=item["label"], icon=item["icon"])
        with col2:
            st.markdown(item["description"])
    
    st.markdown(" ")  # Add space between groups
    

################################ FAQs #################################

st.markdown(" ") 
st.markdown('<h3 class="section-header">FAQs</h3>', unsafe_allow_html=True)
st.markdown(" ")

st.expander("Where is the data in the CA Legislation Tracker sourced from?", expanded=False).markdown("We source data from the OpenStates REST API and directly from the California LegInfo websites.")

st.expander("How often is the CA Legislation Tracker updated?", expanded=False).markdown("""
                                                                                         
The main legislative data (i.e., Bills, Legislators, Committees) is updated twice per day: first between 2-3 AM Pacific Time and again between 2-3 PM Pacific Time. Freshness of data pulled from legislative sources such as LegInfo are subject to the update cadence of those sources, which may vary. Please refer to the "Last Updated" date on the Bills page for the best indication of when the original data was last refreshed.
""")
                                                                                         
st.expander("I noticed some data was incorrect or outdated.", expanded=False).markdown("This is possible. The California legislative websites may contain errors, or may not be updated on a timely basis, so there may be discrepencies from time to time. We do our best to ensure accuracy. We encourage advocacy professionals to double check information such as timing and location of Assembly and Senate meetings and hearings, or other time-sensitive information. If you notice recurring issues, please contact us.")

################################ CONTACT #################################
st.markdown(" ") 
st.markdown('<h3 class="section-header">Contact</h3>', unsafe_allow_html=True)
st.markdown(" ") 

st.markdown("""
**Submit Feedback**
            
If you have a question, comment, or feature request for the CA Legislation Tracker, let us know by filling out our [feedback form](https://docs.google.com/forms/d/e/1FAIpQLSe0z74WPwG7PtXlOOkMolgXvi5QPjIs_s0OVcxzryjdp5HsFA/viewform?usp=dialog).         
""")

st.markdown(" ")


st.markdown("""
**Technical Support**
            
If you require immediate technical assistance or encounter an urgent issue while using the tool, please reach out to us via email so we can provide support:
                                                                                                                               
- Danya Sherbini, Lead Developer (danya@techequity.us)
- Keirstan Schiedeck, Product Manager (keirstan@techequity.us)          
""")