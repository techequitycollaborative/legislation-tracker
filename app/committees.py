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
from db.query import query_table, COMMITTEE_COLUMNS
from utils import aggrid_styler
from utils.general import to_csv
from utils.committees import display_committee_info_text

# Page title and description
st.title('🗣 Committees')

st.expander("About this page", icon="ℹ️", expanded=False).markdown(""" 
- This page shows California Assembly and Senate committee information (upcoming hearings, memberships, links). 
- Click on a committee to view additional details.                                               
""")

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")

############################ LOAD AND PROCESS COMMITTEE DATA #############################
# Load committee membership data
def get_committee_data():
    """
    Use query_table to load, clean, and cache committee data.
    """
    # Cache the function that retrieves the data
    @st.cache_data
    def committee_cache():
        # Query the database for processed committees
        committee = query_table('public', 'processed_committee_2025_2026')

        # Generate chamber name from ID
        committee['chamber'] = np.where(committee['chamber_id']==1,'Assembly','Senate') 

        # Clean up next hearing format
        committee["next_hearing"] = pd.to_datetime(committee['committee_event'], errors='coerce').dt.strftime('%Y-%m-%d')

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

# # Initialize session state for selected committees
if 'selected_committees' not in st.session_state:
    st.session_state.selected_committees = []

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
        data=to_csv(committees),
        file_name='committees.csv',
        mime='text/csv',
        use_container_width=True
    )

# Update session state if the user picks a new theme
selected_theme = theme_options[selected_label]
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme

# Use the persisted theme
theme = st.session_state.theme

# # Display the aggrid table
data = aggrid_styler.draw_committee_grid(committees, theme=theme)
    
selected_rows = data.selected_rows

if selected_rows is not None and len(selected_rows) != 0:
        display_committee_info_text(selected_rows)


