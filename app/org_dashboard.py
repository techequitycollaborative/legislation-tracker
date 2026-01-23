#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Org Dashboard: With Streamlit Dataframe
Created on Nov 17, 2025
@author: danyasherbini

Private dashboard for an organization, populated with bills from Bills page
"""

import streamlit as st
import pandas as pd
from db.query import get_org_dashboard_bills
from utils.org_dashboard import display_org_dashboard_details
from utils.bill_history import format_bill_history
from utils.profiling import timer, profile, track_rerun, track_event
from utils.table_display import initialize_filter_state, display_bill_filters, apply_bill_filters, display_bills_table


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

# Load bills data for the org dashboard
@profile("DB - Fetch ORG DASHBOARD table data")
@st.cache_data(show_spinner="Loading your dashboard...", ttl=30) # Cache dashboard data and refresh every 30 seconds
def load_org_dashboard_table():
    # Get data
    org_db_bills = get_org_dashboard_bills(org_id)

    # Update session state with user's org's dashboard bills
    st.session_state.org_dashboard_bills = org_db_bills

    # DON'T NEED TO FORMAT DATES FOR STREAMLIT NATIVE TABLES; THIS IS HANDLED IN COLUMN CONFIG WITH DATE COLUMN
    # Now remove timestamp from date_introduced and bill_event (for formatting purposes in other display areas)
    # KEEP AS Y-M-D FORMAT FOR AG GRID DATE FILTERING TO WORK
    #org_db_bills['date_introduced'] = pd.to_datetime(org_db_bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestamp from date introduced
    #org_db_bills['bill_event'] = pd.to_datetime(org_db_bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
    #org_db_bills['last_updated_on'] = pd.to_datetime(org_db_bills['last_updated_on']).dt.strftime('%Y-%m-%d') # Remove timestamp from last_updated_on

    # Minor data processing to match bills table
    # Wrangle assigned-topic string to a Python list for web app manipulation
    org_db_bills['bill_topic'] = org_db_bills['assigned_topics'].apply(lambda x: set(x.split("; ")) if x else ["Other"])
    org_db_bills = org_db_bills.drop(columns=['assigned_topics'])

    org_db_bills['bill_history'] = org_db_bills['bill_history'].apply(format_bill_history) #Format bill history

    # Default sorting: by upcoming bill_event
    org_db_bills = org_db_bills.sort_values(by='bill_event', ascending=False)
    
    return org_db_bills

st.session_state.org_dashboard_bills = load_org_dashboard_table()

############################ FILTERS #############################
# Display filters and get filter values
filters = display_bill_filters(
    st.session_state.org_dashboard_bills,
    show_date_filters=False,
    show_keyword_search=False
)
filtered_bills = apply_bill_filters(st.session_state.org_dashboard_bills, filter_dict=filters)

# Update total bills count
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    total_bills = len(filtered_bills)
    st.markdown(f"#### Total bills: {total_bills:,}")
    if len(filtered_bills) < len(st.session_state.org_dashboard_bills):
        st.caption(f"(filtered from {len(st.session_state.org_dashboard_bills):,} total)")

############################ MAIN TABLE / DATAFRAME #############################

if not st.session_state.org_dashboard_bills.empty:
    with timer("Org dashboard - draw streamlit df"):
        data = display_bills_table(filtered_bills)

    # Assign variable to selection property
    selected = data.selection

    # Access selected rows
    if selected != None and selected.rows:
        track_event("Row selected")
        selected_index = selected.rows[0]  # Get first selected row index
        selected_bill_data = filtered_bills.iloc[[selected_index]]  # Double brackets to keep as DataFrame for display function
        display_org_dashboard_details(selected_bill_data)

elif st.session_state.org_dashboard_bills.empty:
    st.write('No bills added yet.')

