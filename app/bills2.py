#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bills Page: Multi-Select
Created on Dec 4, 2024
@author: danyasherbini

This page displays bill info, using a multi-select widget that allows users to filter bills by topic.
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
from utils import aggrid_styler
from utils.utils import display_bill_info, to_csv, format_bill_history, ensure_set

# Set working directory
PATH = '/Users/danyasherbini/Documents/GitHub/lt-streamlit'
os.chdir(PATH)

# Page title and description
st.title('Bills')
st.write(
    '''
    This page shows California bills for the 2023-2024 legislative session. 
    Please note that the page may take a few moments to load.
    '''
)

############################ LOAD AND SET UP DATA #############################

@st.cache_data
def load_bill_data():
    # Load bill data
    bills = pd.read_csv('/Users/danyasherbini/Documents/GitHub/lt-streamlit/data/bills.csv')
    bills['chamber'] = np.where(bills['origin_chamber_id'] == 1, 'Assembly', 'Senate')
    
    # Load and merge bill history data
    bill_history = pd.read_csv('/Users/danyasherbini/Documents/GitHub/lt-streamlit/data/bill_history.csv')
    bills = pd.merge(bills, bill_history, how='left', on='bill_id')
    
    # Rename columns and format
    bills = bills.rename(columns={'history_trace': 'bill_history', 'bill_date': 'date_introduced', 'bill_number': 'bill_no'})
    bills['bill_history'] = bills['bill_history'].apply(ensure_set).apply(format_bill_history)
    return bills

bills = load_bill_data()

# Additional data manipulation
bills['bill_number'] = bills['bill_no']
bills = bills.drop(['bill_no', 'bill_id', 'openstates_bill_id', 'committee_id', 'origin_chamber_id'], axis=1)
bills = bills.sort_values('bill_number', ascending=True)

# Filter DataFrames for specific topics
ai_terms = ['artificial intelligence', 'algorithm', 'automated']
ai_df = bills[bills['bill_name'].str.contains('|'.join(ai_terms), na=False, case=False)]

housing_terms = ['housing', 'eviction', 'tenants', 'renters']
housing_df = bills[bills['bill_name'].str.contains('|'.join(housing_terms), na=False, case=False)]

labor_terms = ['worker', 'labor', 'gig economy', 'contract workers']
labor_df = bills[bills['bill_name'].str.contains('|'.join(labor_terms), na=False, case=False)]

# Create a dictionary for category mapping
category_mapping = {
    "All Bills": bills,
    "AI": ai_df,
    "Housing": housing_df,
    "Labor": labor_df
}

############################### MULTISELECT FILTER ###############################
# Multiselect widget for bill categories
selected_categories = st.multiselect(
    "Select a category:",
    options=list(category_mapping.keys()),
    default=["All Bills"]
)

# Combine selected dataframes
if selected_categories:
    combined_df = pd.concat([category_mapping[category] for category in selected_categories]).drop_duplicates()

    # Create a two-column layout: left for header, right for the button
    col1, col2 = st.columns([4, 1])  # Adjust column widths as needed

    with col1:
        # Header for the selected categories
        st.header(f"Displaying: {', '.join(selected_categories)}")

    with col2:
        # Display the download button in the right column
        st.download_button(
            label="Download Data as CSV",
            data=to_csv(combined_df),
            file_name="selected_bills.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Make the aggrid dataframe
    data = aggrid_styler.draw_bill_grid(combined_df)
    
    # Define selected rows
    selected_rows = data.selected_rows
    
    # If a row is selected, display bill info
    if selected_rows is not None and len(selected_rows) != 0:
        display_bill_info(selected_rows)

else:
    st.write("Please select at least one category to display bills.")

