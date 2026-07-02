#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My Dashboard: With Streamlit Dataframe
Created on Nov 17, 2025
@author: danyasherbini

Private dashboard for the individual user, populated with bills from Bills page
"""

import streamlit as st
#st.write(st.__version__) --> for debugging conflicting streamlit versions
import pandas as pd
from db.query import Query, get_my_dashboard_bills, clear_all_my_dashboard_bills
from utils.my_dashboard import display_dashboard_details
from utils.bill_history import format_bill_history
from utils.profiling import timer, profile, track_rerun, track_event
from utils.table_display import initialize_filter_state, display_bill_filters, apply_bill_filters, display_bills_table, filters_hash
track_rerun("My Dashboard")

# Page title
st.title('📌 My Dashboard')

st.expander("About this page", icon="ℹ️", expanded=False).markdown(f"""
- Use this page to track bills relevant to you.
- Only you can view this page and all bills saved to it.
- To add bills to this dashboard, select a bill on the 📝 Bills page and then click the "Add to My Dashboard" button.
- To add custom advocacy details to a bill, go to your 🏢 Organization Dashboard. Custom advocacy details are viewable on this page, but editable only from your 🏢 Organization Dashboard.
""")

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")

# Toast handler
if '_toast' in st.session_state:
    st.toast(st.session_state.pop('_toast'), icon='✅')

# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'authenticated' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Initialize session state for filters
initialize_filter_state()

# Access user info
user_email = st.session_state['user_email']
user_name = st.session_state['user_name']
first_name = user_name.split()[0]  # Get the first name for a more personal greeting

# Initialize session state for dashboard bills
if 'my_dashboard_bills' not in st.session_state or st.session_state.my_dashboard_bills is None:
    st.session_state.my_dashboard_bills = pd.DataFrame()

# Load bills data for the my dashboard
@profile("DB - Fetch MY DASHBOARD table data")
def load_my_dashboard_table():
    # Fetch the user's saved bills from the database
    db_bills = get_my_dashboard_bills(user_email)
    
    # Minor data processing to match bills table
    # Wrangle assigned-topic string to a Python list for web app manipulation
    db_bills['bill_topic'] = db_bills['assigned_topics'].apply(lambda x: set(x.split("; ")) if x else ["Other"])
    db_bills = db_bills.drop(columns=['assigned_topics'])
    db_bills['bill_history'] = db_bills['bill_history'].apply(format_bill_history) #Format bill history

    # Default sorting: by last updated date
    db_bills = db_bills.sort_values(by='last_updated_on', ascending=False)
    
    return db_bills

if st.session_state.my_dashboard_bills.empty:
    st.session_state.my_dashboard_bills = load_my_dashboard_table()

############################ FILTERS #############################
# Display filters and get filter values
filters = display_bill_filters(
    st.session_state.my_dashboard_bills,
    show_date_filters=False,
    show_keyword_search=False
)
filtered_bills = apply_bill_filters(st.session_state.my_dashboard_bills, filter_dict=filters)


############################ BILLS COUNT + CLEAR DASHBOARD BUTTON #############################
# Update total bills count
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    total_bills = len(filtered_bills)
    st.markdown(f"#### Total bills: {total_bills:,}")
    if len(filtered_bills) < len(st.session_state.my_dashboard_bills):
        st.caption(f"(filtered from {len(st.session_state.my_dashboard_bills):,} total)")

with col2:
    st.markdown("")  # Empty middle column for spacing

# Clear dashboard button
with col3:
    if st.button('Clear Dashboard', width='stretch', type='primary', help="Remove all bills from your dashboard. This action cannot be undone."):
        clear_all_my_dashboard_bills()
        st.session_state.selected_bills = []
        st.session_state.my_dashboard_bills = pd.DataFrame()  # Clear in-memory DataFrame
        st.session_state['_toast'] = 'Dashboard cleared!'  # toast instead of st.success()
        st.rerun()

# Add additional space between button and table
st.markdown(" ")

############################ MAIN TABLE / DATAFRAME #############################

if not st.session_state.my_dashboard_bills.empty:
    with timer("My dashboard - draw streamlit df"):
        data = display_bills_table(filtered_bills)

    selected = data.selection

    # Detect filter changes and clear selection if filters have changed
    current_hash = filters_hash(filters)
    if st.session_state.get('_my_filter_hash') != current_hash:
        st.session_state['_my_filter_hash'] = current_hash
        st.session_state.pop('selected_bill_id_my', None)

    if selected is not None and selected.rows:
        track_event("Row selected")
        selected_index = selected.rows[0]
        newly_selected_id = filtered_bills.iloc[selected_index]['openstates_bill_id']

        # Persist selection by bill ID (not row index) so it survives reruns
        st.session_state['selected_bill_id_my'] = newly_selected_id

    else:
        # No row selected (deselect or initial load) — clear the details panel
        st.session_state.pop('selected_bill_id_my', None)

    # Look up the selected bill by ID from session state.
    # Using ID instead of row index means the correct bill stays selected even if the table re-sorts or filters change between reruns.
    selected_id = st.session_state.get('selected_bill_id_my')
    if selected_id is not None:
        selected_bill_data = filtered_bills[
            filtered_bills['openstates_bill_id'] == selected_id
        ]
        if not selected_bill_data.empty:
            display_dashboard_details(selected_bill_data)

else:
    st.write('No bills added yet.')


