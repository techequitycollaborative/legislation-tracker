#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Committees Page
Created on May 5, 2025
@author: jessiclassy

Committees page with:
    - Committee table
    - Committee details with text
"""

import numpy as np
import pandas as pd
import streamlit as st
from db.query import Query, COMMITTEE_COLUMNS
from utils import aggrid_styler
from utils.general import to_csv
from utils.committees import display_committee_info_text, initialize_filter_state, display_committee_filters, apply_committee_filters, display_committee_table
from utils.profiling import timer, profile, show_performance_metrics, track_rerun, track_event

# Page title and description
st.title('🗣 Committees')
st.session_state.curr_page = "Committees"

st.expander("About this page", icon="ℹ️", expanded=False).markdown(""" 
- This page shows California Assembly and Senate committee information (upcoming hearings, memberships, links). 
- Click on a committee to view additional details.                                               
""")

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")

############################ LOAD AND PROCESS COMMITTEE DATA #############################
track_rerun("Committees")

# Load committee membership data
@profile("DB - Fetch COMMITTEE table data")
def get_committee_data():
    # Cache the function that retrieves the data
    @st.cache_data(show_spinner="Loading committee data...")
    def committee_cache():
        # Get data
        committee_query = """
            SELECT * FROM public.processed_committee_2025_2026
        """
            
        committee = Query(
            page_name="legislators",
            query=committee_query,
        ).fetch_records()
        
        # Generate chamber name from ID
        committee['chamber'] = np.where(committee['chamber_id']==1,'Assembly','Senate') 

        # Clean up next hearing format
        committee["next_hearing"] = pd.to_datetime(committee['committee_event'], errors='coerce').dt.strftime('%Y-%m-%d')

        # Only show committee hearing date if it's in the future
        committee["next_hearing"] = np.where(pd.to_datetime(committee["next_hearing"]) >= pd.Timestamp.now(), committee["next_hearing"], "No upcoming hearing scheduled")

        # Fill NA values for chair and vice chair
        committee["committee_chair"] = committee["committee_chair"].fillna("*None appointed*")
        committee["committee_vice_chair"] = committee["committee_vice_chair"].fillna("*None appointed*")

        # Count members
        committee["total_members"] = committee["total_members"].fillna(0)

        # Reorder columns
        committee = committee[COMMITTEE_COLUMNS]
        return committee
    
    # Call the cached function to get the data
    committees = committee_cache()
    return committees

committees = get_committee_data()

############################ SESSION STATE #############################

# # Initialize session state for selected committees
if 'selected_committees' not in st.session_state:
    st.session_state.selected_committees = []

# Initialize session state for filters
initialize_filter_state()

############################ FILTERS #############################

# Display filters and get filter values
filter_values = display_committee_filters(committees)
selected_name, selected_chamber, hearing_search, chairperson_search, vice_chairperson_search = filter_values

# Apply filters
filtered_committees = apply_committee_filters(
    committees, 
    selected_name, 
    selected_chamber,
    hearing_search,
    chairperson_search,
    vice_chairperson_search
)

# Update total committees count
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    total_committees = len(filtered_committees)
    st.markdown(f"#### Total committees: {total_committees:,}")
    if len(filtered_committees) < len(committees):
        st.caption(f"(filtered from {len(committees):,} total)")

############################ MAIN TABLE / DATAFRAME #############################

# Display the table
with timer("Committees - draw streamlit df"):
    data = display_committee_table(filtered_committees)

# Access selected rows
if data.selection.rows:
    track_event("Row selected")
    selected_index = data.selection.rows[0]  # Get first selected row index
    selected_bill_data = filtered_committees.iloc[[selected_index]]  # Double brackets to keep as DataFrame for display function
    display_committee_info_text(selected_bill_data)


