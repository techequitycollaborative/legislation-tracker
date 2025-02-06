#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing out My Dashboard
Created on Dec 2, 2024
@author: danyasherbini

Page to add bills to user's private dashboard
"""

import streamlit as st
import pandas as pd
from utils.aggrid_styler import draw_bill_grid
from utils.utils import format_bill_history, get_bill_topics, keywords, to_csv
from db.query import get_my_dashboard_bills
from utils.dashboard_utils import display_dashboard_details


# Page title
st.title('Dashboard')

# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'user_info' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Access user info
user_info = st.session_state['user_info']
user_email = st.session_state["user_info"].get("email")

# Clear dashboard button
col1, col2 = st.columns([4, 1])
with col2:
    if st.button('Clear Dashboard', use_container_width=True, type='primary'):
        st.session_state.selected_bills = []  # Clear session state
        st.success('Dashboard cleared!')

# Fetch the user's saved bills from the database
db_bills = get_my_dashboard_bills(user_email)

# Minor data processing to match bills table
db_bills['date_introduced'] = pd.to_datetime(db_bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestampe from date introduced
db_bills = get_bill_topics(db_bills, keyword_dict= keywords)  # Get bill topics
db_bills['bill_history'] = db_bills['bill_history'].apply(format_bill_history) #Format bill history

if not db_bills.empty:
    st.write('Your saved bills:')
    data = draw_bill_grid(db_bills)

    # Display bill details for dashboard bills
    if 'selected_bills' not in st.session_state:
        st.session_state.selected_bills = []
        
    selected_rows = data.selected_rows

    if selected_rows is not None and len(selected_rows) != 0:
            display_dashboard_details(selected_rows)

    # Buttom to download selected bills
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("")

    with col2:
        st.download_button(
                label='Download Data as CSV',
                data=to_csv(db_bills),
                file_name='my_bills.csv',
                mime='text/csv',
                use_container_width=True
            )

else:
    st.write('No bills selected yet.')


