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
from utils.utils import format_bill_history, get_bill_topics, keywords, to_csv, get_bill_topics_multiple
from db.query import get_my_dashboard_bills, clear_all_my_dashboard_bills
from utils.display_utils import display_dashboard_details, format_bill_history_dashboard


# Page title
st.title('Dashboard')

# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'authenticated' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Access user info
#user_info = st.session_state['user_info']
#user_email = st.session_state["user_info"].get("email")
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

# Fetch the user's saved bills from the database
db_bills = get_my_dashboard_bills(user_email)

# Update session state with user's dashboard bills
st.session_state.dashboard_bills = db_bills

# Minor data processing to match bills table
db_bills['date_introduced'] = pd.to_datetime(db_bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestampe from date introduced
db_bills['bill_event'] = pd.to_datetime(db_bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
db_bills = get_bill_topics_multiple(db_bills, keyword_dict= keywords)  # Get bill topics
db_bills['bill_history'] = db_bills['bill_history'].apply(format_bill_history) #Format bill history

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
            data=to_csv(db_bills),
            file_name='my_bills.csv',
            mime='text/csv',
            use_container_width=True
        )

# Update session state if the user picks a new theme
selected_theme = theme_options[selected_label]
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme

# Use the persisted theme
theme = st.session_state.theme

if not db_bills.empty:
    total_db_bills = len(db_bills)
    st.markdown(f"#### {first_name}'s saved bills: {total_db_bills} total bills")
    data = draw_bill_grid(db_bills, theme=theme)

    # Display bill details for dashboard bills
    if 'selected_bills' not in st.session_state:
        st.session_state.selected_bills = []
        
    selected_rows = data.selected_rows

    if selected_rows is not None and len(selected_rows) != 0:
            display_dashboard_details(selected_rows)

elif db_bills.empty:
    st.write('No bills selected yet.')


