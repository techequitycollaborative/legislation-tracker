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
from db.query import Query, LEGISLATOR_COLUMNS
from utils import aggrid_styler
from utils.general import to_csv, transform_name
from utils.legislators import display_legislator_info_text
from utils.profiling import timer, profile, show_performance_metrics, track_rerun, track_event
from utils.legislators import initialize_filter_state, display_legislator_filters, apply_legislator_filters, display_legislator_table


############################ SESSION STATE #############################

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

# Initialize session state for filters
initialize_filter_state()

############################ PAGE SETUP #############################

# Show the page title and description
st.title('💼 Legislators')

st.expander("About this page", icon="ℹ️", expanded=False).markdown(""" 
- This page shows legislator information for the current legislative session as collected from OpenStates and the [Capitol Codex](https://docs.google.com/spreadsheets/d/1gFeGy72R_-FSFrjXbKCAAvVsvNjyV7t_TUvFoB12vys/edit?gid=1422908451#gid=1422908451) Issues tabs. 
- Click on a legislator to view additional details, such as staff contact information.                                          
""")

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")


############################ LOAD AND PROCESS DATA #############################
track_rerun("Legislators")

# Load data
@profile("DB - Fetch LEGISLATOR table data")
def get_legislator_data():
    """
    Use query_table to load, clean, and cache legislator data
    """
    # Cache the function that retrieves the data
    @st.cache_data(show_spinner="Loading legislator data...")#
    def legislator_cache():
        # Get data
        legislator_query = """
            SELECT * FROM public.processed_legislators_from_snapshot_2025_2026
        """
            
        legislator = Query(
            page_name="legislators",
            query=legislator_query
        ).fetch_records()

        # On-the-fly
        legislator["name"] = legislator["name"].apply(transform_name)
        legislator["last_updated_on"] = pd.to_datetime(legislator['last_updated_on']).dt.strftime('%Y-%m-%d') # Remove timestamp from last_updated_on
        # Sort alphabetically by last name
        legislator = legislator.sort_values(by='name', ascending=True)
        return legislator[LEGISLATOR_COLUMNS]
    
    legislators = legislator_cache()
    
    return legislators

legislators = get_legislator_data()

############################ FILTERS #############################
# Display filters and get filter values
filter_values = display_legislator_filters(legislators)
selected_name, selected_party, selected_chamber = filter_values

# Apply filters
filtered_legislators = apply_legislator_filters(
    legislators, 
    selected_name, 
    selected_party, 
    selected_chamber
)

# Update total legislators count
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    total_legislators = len(filtered_legislators)
    st.markdown(f"#### Total legislators: {total_legislators:,}")
    if len(filtered_legislators) < len(legislators):
        st.caption(f"(filtered from {len(legislators):,} total)")

############################ MAIN TABLE / DATAFRAME #############################

cols = st.columns([4, 6]) 

with cols[0]:  # Left panel - Browse
    st.subheader("Legislator Directory")
    # Display the table
    with timer("Legislators - draw streamlit df"):
        data = display_legislator_table(filtered_legislators)

with cols[1]:  # Right panel - Detail View
    # Access selected rows
    if data.selection.rows:
        track_event("Row selected")
        selected_index = data.selection.rows[0]  # Get first selected row index
        selected_legislator_data = filtered_legislators.iloc[[selected_index]]  # Double brackets to keep as DataFrame for display function
        display_legislator_info_text(selected_legislator_data)
        
    else:
        st.markdown("#")
        st.markdown("#")
        st.markdown("#")
        st.markdown("""
                    <div style="text-align: center"> 
                    <b><i>No current selection.</i> </b>
                    </div>
        """, unsafe_allow_html=True)



