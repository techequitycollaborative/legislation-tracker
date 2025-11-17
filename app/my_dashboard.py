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
from db.query import get_my_dashboard_bills, clear_all_my_dashboard_bills
from utils.my_dashboard import display_dashboard_details
from utils.bill_history import format_bill_history
from utils.profiling import timer, profile, show_performance_metrics, track_rerun, track_event
from utils.table_display import initialize_filter_state, display_bill_filters, apply_bill_filters, display_bills_table

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

# Clear dashboard button
col1, col2 = st.columns([4, 1])
with col2:
    if st.button('Clear Dashboard', use_container_width=True, type='primary'):
        clear_all_my_dashboard_bills(user_email)  # Actually remove the bills from the DB
        st.session_state.selected_bills = []
        st.session_state.dashboard_bills = pd.DataFrame()  # Clear in-memory DataFrame
        st.success('Dashboard cleared!')

# Initialize session state for dashboard bills
if 'dashboard_bills' not in st.session_state or st.session_state.dashboard_bills is None:
    st.session_state.dashboard_bills = pd.DataFrame()  # Initialize as empty DataFrame

# Load bills data for the my dashboard
@profile("DB - Fetch MY DASHBOARD table data")
def load_my_dashboard_table():
    # Fetch the user's saved bills from the database
    db_bills = get_my_dashboard_bills(user_email)

    # Now remove timestamp from date_introduced and bill_event (for formatting purposes in other display areas)
    # KEEP AS Y-M-D FORMAT FOR AG GRID DATE FILTERING TO WORK
    db_bills['date_introduced'] = pd.to_datetime(db_bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestamp from date introduced
    db_bills['bill_event'] = pd.to_datetime(db_bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
    db_bills['last_updated_on'] = pd.to_datetime(db_bills['last_updated_on']).dt.strftime('%Y-%m-%d') # Remove timestamp from last_updated_on

    # Minor data processing to match bills table
    # Wrangle assigned-topic string to a Python list for web app manipulation
    db_bills['bill_topic'] = db_bills['assigned_topics'].apply(lambda x: set(x.split("; ")) if x else ["Other"])
    db_bills = db_bills.drop(columns=['assigned_topics'])
    db_bills['bill_history'] = db_bills['bill_history'].apply(format_bill_history) #Format bill history

    # Default sorting: by upcoming bill_event
    #db_bills = db_bills.sort_values(by='bill_event', ascending=False)
    return db_bills

with st.spinner("Loading your dashboard..."):
    db_bills = load_my_dashboard_table()


############################ FILTERS #############################
# Display filters and get filter values
filter_values = display_bill_filters(db_bills, show_date_filters=True)
selected_topics, selected_statuses, author_search, bill_number_search, date_from, date_to = filter_values

# Apply filters
filtered_bills = apply_bill_filters(
    db_bills, 
    selected_topics, 
    selected_statuses, 
    author_search, 
    bill_number_search, 
    date_from, 
    date_to
)

# Update total bills count
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    total_bills = len(filtered_bills)
    st.markdown(f"#### Total bills: {total_bills:,}")
    if len(filtered_bills) < len(db_bills):
        st.caption(f"(filtered from {len(db_bills):,} total)")

############################ MAIN TABLE / DATAFRAME #############################

if not db_bills.empty:
    with timer("My dashboard - draw streamlit df"):
        data = display_bills_table(filtered_bills)

    # Access selected rows
    if data.selection.rows:
        track_event("Row selected")
        selected_index = data.selection.rows[0]  # Get first selected row index
        selected_bill_data = filtered_bills.iloc[[selected_index]]  # Double brackets to keep as DataFrame for display function
        display_dashboard_details(selected_bill_data)

elif db_bills.empty:
    st.write('No bills added yet.')


    


