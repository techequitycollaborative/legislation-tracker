#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My Dashboard
Created on Dec 2, 2024
@author: danyasherbini

Page to add bills to user's private dashboard
"""

import streamlit as st
import pandas as pd
from utils.aggrid_styler import draw_bill_grid
from utils.general import to_csv
from db.query import get_my_dashboard_bills, clear_all_my_dashboard_bills
from utils.my_dashboard import display_dashboard_details
from utils.bill_history import format_bill_history


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
print(db_bills)
# Update session state with user's dashboard bills
#st.session_state.dashboard_bills = db_bills

# Now remove timestamp from date_introduced and bill_event (for formatting purposes in other display areas)
# KEEP AS Y-M-D FORMAT FOR AG GRID DATE FILTERING TO WORK
db_bills['date_introduced'] = pd.to_datetime(db_bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestamp from date introduced
db_bills['bill_event'] = pd.to_datetime(db_bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
db_bills['last_updated_on'] = pd.to_datetime(db_bills['last_updated_on']).dt.strftime('%Y-%m-%d') # Remove timestamp from last_updated_on

# Minor data processing to match bills table
# Convert assigned_topics into string for AgGrid. AgGrid cannot hash Python lists or sets.
db_bills['bill_topic'] = db_bills['assigned_topics'].apply(lambda x: "; ".join(x.split("; ")) if pd.notna(x) and x.strip() else "Other")
    
# Drop the original assigned_topics column from the display table
db_bills = db_bills.drop(columns=['assigned_topics'])

#Format bill history
db_bills['bill_history'] = db_bills['bill_history'].apply(format_bill_history) 

# Default sorting: by upcoming bill_event
db_bills = db_bills.sort_values(by='bill_event', ascending=False)

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


