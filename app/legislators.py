#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legislator Page
Created on Oct 2, 2024
@author: danyasherbini

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
    This page shows California legislators for the 2025-2026 legislative session. 
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

# Create two columns
col1, col2 = st.columns([4.5, 1.25])  # Adjust column widths as needed
with col1:
    st.markdown("") # Blank space
with col2: # Align download button to right side
    download_button = st.download_button(key='legislators_download',
                       label='Download Full Data as CSV',
                       data=to_csv(legislators),
                       file_name='legislators.csv',
                       mime='text/csv',
                       use_container_width=True
                        )

# Make the aggrid dataframe
data = aggrid_styler.draw_leg_grid(legislators)





