#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Org Dashboard
Created on March 28, 2025
@author: danyasherbini

Page to add bills to an org's private dashboard
"""

import streamlit as st
import pandas as pd
from utils.aggrid_styler import draw_bill_grid
from utils.general import to_csv
from db.query import get_org_dashboard_bills
from utils.org_dashboard import display_org_dashboard_details
from utils.bill_history import format_bill_history
from utils.profiling import timer, profile, show_performance_metrics, track_rerun

track_rerun("Org Dashboard")

# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'authenticated' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Access user info from session state
org_id = st.session_state.get('org_id')
org_name = st.session_state['org_name']
org_nickname = st.session_state.get('nickname')
user_email = st.session_state['user_email']

# Page title
st.title(f"🏢 {org_nickname}'s Dashboard")

st.expander("About this page", icon="ℹ️", expanded=False).markdown(f"""
- Use this page to track bills relevant to your organization.
- Anyone in your organization with access to the CA Legislation Tracker can view this page and all bills saved to it.
- To add bills to this dashboard, select a bill on the 📝 Bills page and then click the "Add to {org_name} Dashboard" button.
- To add custom advocacy details to a bill, select a bill on this dashboard and edit the "Custom Advocacy Details" section. This data is only editable from this page, but is viewable for bills on your 📌 My Dashboard and viewable to fellow organizations on the 📣 Advocacy Hub page.                                         
""")

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")

# Clear dashboard button -- DISABLED FOR NOW BC IT MIGHT GET MESSY HAVING THIS OPTION WITH MANY USERS SHARING ONE ORG DASHBOARD. but if we want to add it, the clear button on the my dashboard works.
#col1, col2 = st.columns([4, 1])
#with col2:
#    if st.button('Clear Dashboard', width='stretch', type='primary'):
#        st.session_state.selected_bills = []  # Clear session state
#        st.success('Dashboard cleared!')

# Initialize session state for org dashboard bills
if 'org_dashboard_bills' not in st.session_state or st.session_state.org_dashboard_bills is None:
    st.session_state.org_dashboard_bills = pd.DataFrame()  # Initialize as empty DataFrame

with timer("Dashboard - fetch and prepare bills data"):
    # Fetch the user's org's saved bills from the database
    org_db_bills = get_org_dashboard_bills(org_id)

    # Update session state with user's org's dashboard bills
    st.session_state.org_dashboard_bills = org_db_bills

    # Now remove timestamp from date_introduced and bill_event (for formatting purposes in other display areas)
    # KEEP AS Y-M-D FORMAT FOR AG GRID DATE FILTERING TO WORK
    org_db_bills['date_introduced'] = pd.to_datetime(org_db_bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestamp from date introduced
    org_db_bills['bill_event'] = pd.to_datetime(org_db_bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
    org_db_bills['last_updated_on'] = pd.to_datetime(org_db_bills['last_updated_on']).dt.strftime('%Y-%m-%d') # Remove timestamp from last_updated_on

    # Minor data processing to match bills table
    # Wrangle assigned-topic string to a Python list for web app manipulation
    org_db_bills['bill_topic'] = org_db_bills['assigned_topics'].apply(lambda x: set(x.split("; ")) if x else ["Other"])
    org_db_bills = org_db_bills.drop(columns=['assigned_topics'])

    org_db_bills['bill_history'] = org_db_bills['bill_history'].apply(format_bill_history) #Format bill history

    # Default sorting: by upcoming bill_event
    org_db_bills = org_db_bills.sort_values(by='bill_event', ascending=False)

# Mapping between user-friendly labels and internal theme values
theme_options = {
    'narrow': 'streamlit',
    'wide': 'alpine'
}

# Initialize session state for theme if not set
if 'theme' not in st.session_state:
    st.session_state.theme = 'streamlit'  # Default theme

# Reverse mapping to get the label from the internal value
label_from_theme = {v: k for k, v in theme_options.items()}

# Create a two-column layout
col1, col2, col3 = st.columns([1, 7, 2])
with col1:
    selected_label = st.selectbox(
        'Change grid theme:',
        options=list(theme_options.keys()),
        index=list(theme_options.keys()).index(label_from_theme[st.session_state.theme])
    )
    
with col2:    
    st.markdown("")

with col3:
    st.download_button(
            label='Download Data as CSV',
            data=to_csv(org_db_bills),
            file_name='my_bills.csv',
            mime='text/csv',
            width='stretch'
        )
    
# Update session state if the user picks a new theme
selected_theme = theme_options[selected_label]
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme

# Use the persisted theme
theme = st.session_state.theme

# Draw the bill grid table
if not org_db_bills.empty:
    total_org_db_bills = len(org_db_bills)
    st.markdown(f"#### {org_name}'s saved bills: {total_org_db_bills} total bills")
    with timer("Dashboard - draw AgGrid"):
        data = draw_bill_grid(org_db_bills, theme=theme)

    # Display bill details for dashboard bills
    if 'selected_bills' not in st.session_state:
        st.session_state.selected_bills = []
        
    selected_rows = data.selected_rows

    if selected_rows is not None and len(selected_rows) != 0:
            display_org_dashboard_details(selected_rows)

elif org_db_bills.empty:
    st.write('No bills selected yet.')
