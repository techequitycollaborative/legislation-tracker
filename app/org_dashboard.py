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
from utils.utils import format_bill_history, get_bill_topics, keywords, to_csv
from db.query import get_org_dashboard_bills
from utils.display_utils import display_org_dashboard_details, format_bill_history_dashboard


# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'authenticated' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Access user info
org_id = st.session_state.get('org_id')
org_name = st.session_state['org_name']
user_email = st.session_state['user_email']

# Page title
st.title(f"{org_name}'s Dashboard")

# Clear dashboard button -- DISABLED FOR NOW BC IT MIGHT GET MESSY HAVING THIS OPTION WITH MANY USERS SHARING ONE ORG DASHBOARD. but if we want to add it, the clear button on the my dashboard works.
#col1, col2 = st.columns([4, 1])
#with col2:
#    if st.button('Clear Dashboard', use_container_width=True, type='primary'):
#        st.session_state.selected_bills = []  # Clear session state
#        st.success('Dashboard cleared!')

# Initialize session state for org dashboard bills
if 'org_dashboard_bills' not in st.session_state or st.session_state.org_dashboard_bills is None:
    st.session_state.org_dashboard_bills = pd.DataFrame()  # Initialize as empty DataFrame

# Fetch the user's org's saved bills from the database
org_db_bills = get_org_dashboard_bills(org_id)

# Update session state with user's org's dashboard bills
st.session_state.org_dashboard_bills = org_db_bills

# Minor data processing to match bills table
org_db_bills['date_introduced'] = pd.to_datetime(org_db_bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestampe from date introduced
org_db_bills['bill_event'] = pd.to_datetime(org_db_bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
org_db_bills = get_bill_topics(org_db_bills, keyword_dict= keywords)  # Get bill topics

# Buttom to download selected bills
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("")

with col2:
    st.download_button(
            label='Download Data as CSV',
            data=to_csv(org_db_bills),
            file_name='my_bills.csv',
            mime='text/csv',
            use_container_width=True
        )

# Draw the bill grid table
if not org_db_bills.empty:
    st.markdown(f"{org_name}'s saved bills:")
    data = draw_bill_grid(org_db_bills)

    # Display bill details for dashboard bills
    if 'selected_bills' not in st.session_state:
        st.session_state.selected_bills = []
        
    selected_rows = data.selected_rows

    if selected_rows is not None and len(selected_rows) != 0:
            display_org_dashboard_details(selected_rows)

elif org_db_bills.empty:
    st.write('No bills selected yet.')





