#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bills Page: Tabs
Created on Oct 2, 2024
@author: danyasherbini

This page displays bill info, segementing bills by topic using a tab display.
"""

import streamlit as st
#import pandas as pd
from db.query import get_data
from utils import aggrid_styler
from utils.utils import display_bill_info, to_csv, process_bills_data

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
bills, history = get_data()

# process data
bills = process_bills_data(bills, history)


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


################################# CREATE TABS #################################

# Create page tabs
tab1, tab2, tab3 , tab4 = st.tabs(['All Bills', 'AI', 'Housing', 'Labor'])


# Initialize session state for selected bills
if 'selected_bills' not in st.session_state:
    st.session_state.selected_bills = []

############################### TAB 1: All Bills ###############################
with tab1:
    # Create two columns: left for header, right for the button
    col1, col2 = st.columns([4, 1])  # Adjust column widths as needed

    with col1:
        st.header('All Bills')  # Header remains on the left

    with col2:
        # Place the download button in the right column so it appears in the upper right hand corner of the page
        st.download_button(
            key='all_bills_download',
            label='Download Data as CSV',
            data=to_csv(bills),
            file_name='output.csv',
            mime='text/csv',
            use_container_width=True
        )

    # Make the aggrid dataframe
    data = aggrid_styler.draw_bill_grid(bills)

    # Define selected rows
    selected_rows = data.selected_rows

    # If a row is selected, display bill info:
    if selected_rows is not None and len(selected_rows) != 0:
        display_bill_info(selected_rows)



############################### TAB 2: AI Bills ###############################
with tab2:
    st.header('AI Bills')

    # Make the aggrid dataframe
    data = aggrid_styler.draw_bill_grid(
        ai_df)

    # Define selected rows
    selected_rows = data.selected_rows
    
    # If a row is selected, display bill info:
    if selected_rows is not None:
        if len(selected_rows) != 0:
            display_bill_info(selected_rows)

    # Button to download data as csv file       
    st.download_button(key='ai_download',
                       label='Download Full Data as CSV',
                       data=to_csv(data['data']),
                       file_name='output.csv',
                       mime='text/csv'
                       )
        
        
############################# TAB 3: Housing Bills #############################

with tab3:
    # Title the page
    st.header('Housing Bills')
    
    # Make the aggrid dataframe
    data = aggrid_styler.draw_bill_grid(
        housing_df)

    # Define selected rows
    selected_rows = data.selected_rows
    
    # If a row is selected, display bill info:
    if selected_rows is not None:
        if len(selected_rows) != 0:
            display_bill_info(selected_rows)

    # Button to download data as csv file       
    st.download_button(key='housing_download',
                       label='Download Full Data as CSV',
                       data=to_csv(data['data']),
                       file_name='output.csv',
                       mime='text/csv'
                       )
        
    
############################# TAB 4: Labor Bills ##############################

with tab4: 
    # Title the page
    st.header('Labor Bills')
    
    # Make the aggrid dataframe
    data = aggrid_styler.draw_bill_grid(
        labor_df)

    # Define selected rows
    selected_rows = data.selected_rows
        
    # If a row is selected, display bill info:
    if selected_rows is not None:
        if len(selected_rows) != 0:
            display_bill_info(selected_rows)
   
    # Button to download data as csv file          
    st.download_button(key='labor_download',
                       label='Download Full Data as CSV',
                       data=to_csv(data['data']),
                       file_name='output.csv',
                       mime='text/csv'
                       )


