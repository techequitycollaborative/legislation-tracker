#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legislator Page
Created on Oct 2, 2024

This page of the app contains legislator information.
"""

import numpy as np
import streamlit as st
from db.query import query_table
from utils import aggrid_styler
from utils.utils import to_csv


# Show the page title and description
st.title('Legislators')
st.write(
    '''
    This page shows legislator information for the current legislative session. 
    '''
)

# Load data
def get_and_clean_leg_data():
    """
    Use query_table to load, clean, and cache legislator table.
    """
    # Cache the function that retrieves the data
    @st.cache_data
    def get_legislators():
        # Query the database for bills and history
        legislators = query_table('ca_dev', 'legislator')
        legislators['chamber'] = np.where(legislators['chamber_id']==1,'Assembly','Senate') # change chamber id to actual chamber values
        legislators = legislators.drop(['legislator_id','chamber_id', 'openstates_people_id'],axis=1) # drop these ID columns
        return legislators
    
    # Call the cached function to get the data
    legislators = get_legislators()
    
    return legislators

# Call function
legislators = get_and_clean_leg_data()

# Initialize session state for theme if not set
if 'theme' not in st.session_state:
    st.session_state.theme = 'streamlit'  # Default theme
    
# Create a two-column layout
col1, col2, col3 = st.columns([1, 7, 2])
with col1:
    selected_theme = st.selectbox(
        'Change grid theme:',
        options=['streamlit', 'alpine', 'balham', 'material'],
        index=['streamlit', 'alpine', 'balham', 'material'].index(st.session_state.theme)
    )
    
with col2:    
    st.markdown("")

with col3:
    download_button = st.download_button(key='legislators_download',
                       label='Download Full Data as CSV',
                       data=to_csv(legislators),
                       file_name='legislators.csv',
                       mime='text/csv',
                       use_container_width=True
                        )

# Update session state if the user picks a new theme
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme

# Use the persisted theme
theme = st.session_state.theme

# Display count of total legislators above the table
total_legislators = len(legislators)
st.markdown(f"#### Total legislators: {total_legislators:,}")

# Make the aggrid dataframe
data = aggrid_styler.draw_leg_grid(legislators, theme=theme)





