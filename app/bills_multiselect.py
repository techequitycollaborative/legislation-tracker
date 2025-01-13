#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bills Page: Multi-Select -- with Postgres Connection
Created on Dec 4, 2024
@author: danyasherbini

This page displays bill info, using a multi-select widget that allows users to filter bills by topic.
"""

import pandas as pd
import numpy as np
import streamlit as st
from utils import aggrid_styler
from utils.utils import display_bill_info, to_csv, format_bill_history, ensure_set
from utils.session_manager import initialize_session_state

# Page title and description
st.title('Bills')
st.write(
    '''
    This page shows California bills for the 2023-2024 legislative session. 
    Please note that the page may take a few moments to load.
    '''
)

############################ LOAD AND CLEAN DATA #############################

# Initialize connection to postgres
conn = st.connection("postgresql", type="sql")

# Perform table queries
bills = conn.query('SELECT * FROM bill;', ttl="10m")
history = conn.query('SELECT * FROM bill_history;', ttl="10m")

# Clean up bills
bills['chamber'] = np.where(bills['origin_chamber_id'] == 1, 'Assembly', 'Senate')
bills = bills.drop(['openstates_bill_id', 'committee_id', 'origin_chamber_id'], axis=1)
bills = bills.sort_values('bill_number', ascending=True)

# Make status column pull from most recent update from bill_history table
history['event_date'] = pd.to_datetime(history['event_date']) 
latest_status = ( 
    history.sort_values('event_date', ascending=False)
           .drop_duplicates(subset='bill_id', keep='first')
           .loc[:, ['bill_id', 'event_text']]
)
bills = bills.merge(latest_status, on='bill_id', how='left')
bills['status'] = bills['event_text']
bills.drop(columns=['event_text'], inplace=True)

# Make data_introduced column
introduced_events = history[history['event_text'] == 'Introduced.']
introduced_events = introduced_events.loc[:, ['bill_id', 'event_date']]
introduced_events.rename(columns={'event_date': 'date_introduced'}, inplace=True)
bills = bills.merge(introduced_events, on='bill_id', how='left')

# Create bill_history as its own variable
def create_bill_history(history):
    """
    Create a DataFrame with bill_id and a full bill history
    
    Parameters:
        history: DataFrame containing the bill history data
        
    Returns:
        DataFrame with bill_id and combined event descriptions
    """
    # Ensure event_date is in datetime format
    history['event_date'] = pd.to_datetime(history['event_date'])

    # Create the combined description in the desired format
    history['event_description'] = history['event_date'].dt.strftime('%Y-%m-%d') + " >> " + history['event_text']

    # Group by bill_id and combine all event descriptions into a list
    result = history.groupby('bill_id')['event_description'].apply(list).reset_index()

    # Convert the event_description list into a string format
    result['event_description'] = result['event_description'].apply(lambda x: ', '.join([f'"{event}"' for event in x]))

    # Rename column
    result['bill_history'] = result['event_description']

    return result

bill_history = create_bill_history(history)
bills = bills.merge(bill_history, on='bill_id', how='left')
bills['bill_history'] = bills['bill_history'].apply(ensure_set).apply(format_bill_history)


############################### FILTER DATA FRAMES ###############################

# Filter DataFrames for specific topics
ai_terms = ['artificial intelligence', 'algorithm', 'automated']
ai_df = bills[bills['bill_name'].str.contains('|'.join(ai_terms), na=False, case=False)]

housing_terms = ['housing', 'eviction', 'tenants', 'renters']
housing_df = bills[bills['bill_name'].str.contains('|'.join(housing_terms), na=False, case=False)]

labor_terms = ['worker', 'labor', 'gig economy', 'contract workers']
labor_df = bills[bills['bill_name'].str.contains('|'.join(labor_terms), na=False, case=False)]

# Create a dictionary for category mapping
category_mapping = {
    'All Bills': bills,
    'AI': ai_df,
    'Housing': housing_df,
    'Labor': labor_df
}

# Initialize session state for selected bills
initialize_session_state()

############################### MULTISELECT FILTER ###############################
# Multiselect widget for bill categories
selected_categories = st.multiselect(
    'Select a category:',
    options=list(category_mapping.keys()),
    default=['All Bills']
)

# Combine selected dataframes
if selected_categories:
    combined_df = pd.concat([category_mapping[category] for category in selected_categories]).drop_duplicates()

    # Create a two-column layout: left for header, right for the button
    col1, col2 = st.columns([4, 1])  # Adjust column widths as needed

    with col1:
        # Header for the selected categories
        st.markdown(f"### Displaying: {', '.join(selected_categories)}")

    with col2:
        # Display the download button in the right column
        st.download_button(
            label='Download Data as CSV',
            data=to_csv(combined_df),
            file_name='selected_bills.csv',
            mime='text/csv',
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
    st.write('Please select at least one category to display bills.')

