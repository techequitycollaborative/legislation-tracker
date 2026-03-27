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
from db.query import get_org_dashboard_bills, get_custom_bill_details_with_timestamp
from utils.org_dashboard import display_org_dashboard_details
from utils.bill_history import format_bill_history
from utils.profiling import timer, profile, track_rerun, track_event
from utils.table_display import initialize_filter_state, display_bill_filters, apply_bill_filters, display_bills_table
import hashlib, json

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

# Display any pending toast message from a previous rerun
if '_toast' in st.session_state:
    st.toast(st.session_state.pop('_toast'), icon='✅')

if '_toast_warning' in st.session_state:
    st.toast(st.session_state.pop('_toast_warning'), icon='⚠️')

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

    # Sort bills by last updated date, with most recently updated bills at the top
    org_db_bills['last_updated_on'] = pd.to_datetime(org_db_bills['last_updated_on']).dt.strftime('%Y-%m-%d')
    org_db_bills = org_db_bills.sort_values(by='last_updated_on', ascending=False)
    
    return org_db_bills

if st.session_state.org_dashboard_bills.empty:
    st.session_state.org_dashboard_bills = load_org_dashboard_table()

############################ FILTERS #############################
# Display filters and get filter values
filters = display_bill_filters(
    st.session_state.org_dashboard_bills,
    show_date_filters=False,
    show_keyword_search=False,
    show_org_position=True,
    show_assigned_to=True
)
filtered_bills = apply_bill_filters(st.session_state.org_dashboard_bills, filter_dict=filters)


# Create a hash of the filters to detect changes and reset selected bill if filters change. 
# We use a hash here because the filter dict can be complex and contain unhashable types, so we convert it to a JSON string first (with sorted keys for consistency) and then hash that string.
def _filters_hash(f):
    return hashlib.md5(json.dumps(f, default=str, sort_keys=True).encode()).hexdigest()

current_hash = _filters_hash(filters)
if st.session_state.get('_last_filter_hash') != current_hash:
    st.session_state['_last_filter_hash'] = current_hash
    st.session_state.pop('selected_bill_id', None)

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

    selected = data.selection

    if selected is not None and selected.rows:
        track_event("Row selected")
        selected_index = selected.rows[0]
        newly_selected_id = filtered_bills.iloc[selected_index]['openstates_bill_id']
        
        # If user switched to a different bill, bust the custom details cache
        # so the form loads fresh data for the new bill rather than serving
        # the previous bill's cached response
        if newly_selected_id != st.session_state.get('selected_bill_id'):
            get_custom_bill_details_with_timestamp.clear()
        
        # Persist selection by bill ID (not row index) so it survives reruns
        st.session_state['selected_bill_id'] = newly_selected_id

    else:
        # No row selected (deselect or initial load) — clear the details panel
        st.session_state.pop('selected_bill_id', None)

    # Look up the selected bill by ID from session state.
    # Using ID instead of row index means the correct bill stays selected
    # even if the table re-sorts or filters change between reruns.
    selected_id = st.session_state.get('selected_bill_id')
    if selected_id is not None:
        selected_bill_data = filtered_bills[
            filtered_bills['openstates_bill_id'] == selected_id
        ]
        if not selected_bill_data.empty:
            display_org_dashboard_details(selected_bill_data)

elif st.session_state.org_dashboard_bills.empty:
    st.write('No bills added yet.')

