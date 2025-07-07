#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legislator Page
Created on Oct 2, 2024

This page of the app contains legislator information.
"""

import numpy as np
import pandas as pd
import streamlit as st
from db.query import query_table, LEGISLATOR_COLUMNS
from utils import aggrid_styler
from utils.utils import to_csv, transform_name
from utils.legislators import display_legislator_info_text

# Ensure user info exists in the session (i.e. ensure the user is logged in)
# if 'authenticated' not in st.session_state:
#     st.error("User not authenticated. Please log in.")
#     st.stop()  # Stop execution if the user is not authenticated

# # Access user info from session state
org_id = st.session_state.get('org_id')
org_name = st.session_state['org_name']
user_email = st.session_state['user_email']

# Initialize pointers in session state to manage display details
if 'selected_person' not in st.session_state:
    st.session_state.selected_person = None
if 'contact_df' not in st.session_state:
    st.session_state.contact_df = pd.DataFrame()
    st.session_state.filtered_df = pd.DataFrame()

# Show the page title and description
st.title('Legislators')
st.write(
    '''
    This page shows legislator information for the current legislative session as collected from OpenStates and the [Capitol Codex](https://docs.google.com/spreadsheets/d/1gFeGy72R_-FSFrjXbKCAAvVsvNjyV7t_TUvFoB12vys/edit?gid=1422908451#gid=1422908451) Issues tabs. 
    '''
)

# Load data
def get_legislator_data():
    """
    Use query_table to load, clean, and cache legislator data
    """
    # Cache the function that retrieves the data
    @st.cache_data
    def legislator_cache():
        legislator = query_table('public', 'processed_legislators_from_snapshot_2025_2026')
        legislator["name"] = legislator["name"].apply(transform_name)
        legislator["last_updated_on"] = pd.to_datetime(legislator['last_updated_on']).dt.strftime('%Y-%m-%d') # Remove timestamp from last_updated_on
        return legislator[LEGISLATOR_COLUMNS]
    legislators = legislator_cache()
    return legislators

legislators = get_legislator_data()

### THEME MENU
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

# Create a three-column layout
col1, col2, col3 = st.columns([1, 7, 2])
with col1:
    selected_label = st.selectbox(
        'Change grid theme:',
        options=list(theme_options.keys()),
        index=list(theme_options.keys()).index(label_from_theme[st.session_state.theme])
    )
    
with col2:    
    st.markdown("")

### Download button
with col3:
    download_button = st.download_button(key='legislators_download',
                       label='Download Legislators as CSV',
                       data=to_csv(legislators),
                       file_name='legislators.csv',
                       mime='text/csv',
                       use_container_width=True
                        )

# Update session state if the user picks a new theme
selected_theme = theme_options[selected_label]
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme

# Use the persisted theme
theme = st.session_state.theme

### TABLE CONTENT

# Display count of total legislators above the table
total_legislators = len(legislators)
st.markdown(f"#### Total legislators: {total_legislators:,}")

cols = st.columns([4, 6]) 

with cols[0]:  # Left panel - Browse
    st.subheader("Legislator Directory")
    # Make the aggrid dataframe
    data = aggrid_styler.draw_leg_grid(legislators, theme=theme)

    selected_rows = data.selected_rows

with cols[1]:  # Right panel - Detail View
    if selected_rows is not None and len(selected_rows) > 0:
        display_legislator_info_text(selected_rows)

