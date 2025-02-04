#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bills Page: Multi-Select -- with Postgres Connection
Created on Dec 4, 2024
@author: danyasherbini

Bill into page with:
    - Bill table with multi-select
    - Bill details with text
"""

import streamlit as st
import pandas as pd
from db.query import get_data
from utils import aggrid_styler
from utils.utils import display_bill_info_text, display_bill_info_expander, display_bill_info_dialog, to_csv, process_bills_data

# Page title and description
st.title('Bills')
st.write(
    '''
    This page shows California assembly and senate bill information. 
    Please note that the page may take a few moments to load.
    '''
)

############################ LOAD AND PROCESS BILLS DATA #############################

# get data
bills = get_data()

############################### FILTER DATA FRAMES BY TOPIC ###############################

# Filter DataFrames for specific topics
@st.cache_data
def get_filtered_df(df, filter_terms):
    
    # filter df by if the bill name contains specific terms
    filtered_df = df[df['bill_name'].str.contains('|'.join(filter_terms), na=False, case=False)]

    return filtered_df

# Filtered dataframes for each category
ai_df = get_filtered_df(bills, ['artificial intelligence', 'algorithm', 'automated'])
housing_df = get_filtered_df(bills, ['housing', 'eviction', 'tenants', 'renters'])
labor_df = get_filtered_df(bills, ['worker', 'labor', 'gig economy', 'contract workers'])

# Category mapping
category_mapping = {
    'All Bills': bills,
    'AI': ai_df,
    'Housing': housing_df,
    'Labor': labor_df
}

# Initialize session state for selected bills
if 'selected_bills' not in st.session_state:
    st.session_state.selected_bills = []

############################### MULTISELECT FILTER ###############################

# Multiselect widget for bill categories
selected_categories = st.multiselect(
    'Select a category:',
    options=list(category_mapping.keys()),
    default=['All Bills']
)

# Make a combined dataframe based on the selections made in the multi-select widget
# Caching this function so it doesn't take as long to load/filter the dataframe based on user selections
@st.cache_data
def get_combined_df(selected_categories):
    # Concatenate and deduplicate only when categories change
    combined_df = pd.concat([category_mapping[category] for category in selected_categories]).drop_duplicates()

    # remove timestampe from date introduced
    combined_df['date_introduced'] = pd.to_datetime(combined_df['date_introduced']).dt.strftime('%Y-%m-%d')

    return combined_df

# only combine the dataframe when the user selection changes
if selected_categories:
    combined_df = get_combined_df(selected_categories)

    # Create a two-column layout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"### Displaying: {', '.join(selected_categories)}")
    with col2:
        st.download_button(
            label='Download Data as CSV',
            data=to_csv(combined_df),
            file_name='selected_bills.csv',
            mime='text/csv',
            use_container_width=True
        )

    # Display the aggrid table
    data = aggrid_styler.draw_bill_grid(combined_df)
    
    selected_rows = data.selected_rows
    if selected_rows is not None and len(selected_rows) != 0:
        display_bill_info_text(selected_rows)
else:
    st.write('Please select at least one category to display bills.')

