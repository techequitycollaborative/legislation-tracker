#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bills Page: Tabs
Created on Oct 2, 2024
@author: danyasherbini

This page displays bill info, segementing bills by topic using a tab display.
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
from utils import aggrid_styler
from utils.utils import display_bill_info, to_csv, format_bill_history, ensure_set
from utils.session_manager import initialize_session_state

PATH = '/Users/danyasherbini/Documents/GitHub/lt-streamlit'
os.chdir(PATH)
os.getcwd()


# Show the page title and description
#st.set_page_config(page_title='Legislation Tracker', layout='wide') #can add page_icon argument
st.title('Bills')
st.write(
    '''
    This page shows California bills for the 2023-2024 legislative session. 
    Please note that the page may take a few moments to load.
    '''
)

############################ LOAD AND SET UP DATA #############################

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_bill_data():
    # load bill data
    bills = pd.read_csv('/Users/danyasherbini/Documents/GitHub/lt-streamlit/data/bills.csv')
    # Change chamber id to senate and assembly
    bills['chamber'] = np.where(bills['origin_chamber_id']==1,'Assembly','Senate')
    # load bill history data
    bill_history = pd.read_csv('/Users/danyasherbini/Documents/GitHub/lt-streamlit/data/bill_history.csv')
    # merge data sets
    bills = pd.merge(bills, bill_history, how='left', on= 'bill_id')
    # rename columns
    bills = bills.rename(columns={'history_trace':'bill_history','bill_date':'date_introduced','bill_number':'bill_no'})
    # reformat bill history column
    bills['bill_history'] = bills['bill_history'].apply(ensure_set)
    bills['bill_history'] = bills['bill_history'].apply(format_bill_history)
    return bills

bills = load_bill_data()


# Additional data manipulation to bills df
# Move bill_number column to first column
numbers = bills['bill_no']
bills.insert(0,'bill_number',numbers)
# Drop some columns we don't need
drop_cols = ['bill_no','bill_id','openstates_bill_id', 'committee_id', 'origin_chamber_id']
bills = bills.drop(drop_cols, axis=1)
# Sort by bill number by default
bills = bills.sort_values('bill_number', ascending=True)


# Get dataframes for AI bills, housing bills, and labor bills

# AI bills
ai_terms = ['artificial intelligence','algorithm','automated']
ai_df = bills[bills['bill_name'].str.contains('|'.join(ai_terms),na=False,case=False)]
ai_df = ai_df.sort_values('bill_number', ascending=True) # sort by bill number by default

# Housing bills
housing_terms = ['housing','eviction','tenants','renters']
housing_df = bills[bills['bill_name'].str.contains('|'.join(housing_terms), na=False, case=False)]
housing_df = housing_df.sort_values('bill_number', ascending=True) # sort by bill number by default

# Labor bills
labor_terms = ['worker','labor','gig economy','contract workers']
labor_df = bills[bills['bill_name'].str.contains('|'.join(labor_terms), na=False, case=False)]
labor_df = labor_df.sort_values('bill_number', ascending=True) # sort by bill number by default


# Create page tabs
tab1, tab2, tab3 , tab4 = st.tabs(['All Bills', 'AI', 'Housing', 'Labor'])


# Initialize session state for selected bills
initialize_session_state()

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


