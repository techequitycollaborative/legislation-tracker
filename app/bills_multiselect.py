#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bills Page: Multi-Select -- with Postgres Connection
Created on Dec 4, 2024
@author: danyasherbini

This page displays bill info, using a multi-select widget that allows users to filter bills by topic.
"""
import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
from db.config import config
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

############################ CONNECT TO POSTGRES DATABASE #############################

# Initialize connection to postgres
#conn = st.connection("postgresql",type="sql")

# Perform table queries
#bills = conn.query('SELECT * FROM bill;', ttl="10m") 
#history = conn.query('SELECT * FROM bill_history;', ttl="10m")


# Load the database configuration
db_config = config('postgres')

def query_table(schema, table):
    """
    Parameters
    ----------
    schema : str
        The schema name in the PostgreSQL database.
    table : str
        The table name in the PostgreSQL database.

    Returns
    -------
    pd.DataFrame
        The queried table in DataFrame format.
    """
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")
    
    # Define SQL query
    query = f'SELECT * FROM {schema}.{table};'
    
    # Query the table and convert to a DataFrame
    with conn.cursor() as cursor:
        cursor.execute(query)
        records = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(records, columns=columns)
    
    # Close the connection
    conn.close()
    print("Database connection closed.")
    
    return df


# Query bill and bill_history tables
bills = query_table('ca_dev', 'bill')
history = query_table('ca_dev', 'bill_history')

############################## DATA MANIPULATION ##############################

# Clean up bills table
bills['chamber'] = np.where(bills['origin_chamber_id'] == 1, 'Assembly', 'Senate')
bills = bills.drop(['openstates_bill_id', 'committee_id', 'origin_chamber_id'], axis=1)
bills = bills.sort_values('bill_number', ascending=True)

# Make status column pull from most recent update from bill_history table
#history['event_date'] = pd.to_datetime(history['event_date']) 
#latest_status = ( 
#    history.sort_values('event_date', ascending=False)
#           .drop_duplicates(subset='bill_id', keep='first')
#           .loc[:, ['bill_id', 'event_text']]
#)
#bills = bills.merge(latest_status, on='bill_id', how='left')
#bills['status'] = bills['event_text']
#bills.drop(columns=['event_text'], inplace=True)

def get_bill_status(bills, history):
    """
    Get the most recent status of a bill based on the full bill history.

    Parameters:
    -----------
        bills: DataFrame containing bill data
        history: DataFrame containing the bill history data

    Returns:
    --------
        A DataFrame with status column added.
    """
    # Ensure event_date is in datetime format
    history['event_date'] = pd.to_datetime(history['event_date']) 
    
    # Get latest status for each bill by sorting bill_history df by event_date in descending order
    latest_status = ( 
        history.sort_values('event_date', ascending=False)
               .drop_duplicates(subset='bill_id', keep='first')
               .loc[:, ['bill_id', 'event_text']]
    )
    
    # Merge latest status df with bills df
    bills = bills.merge(latest_status, on='bill_id', how='left')
    
    # Reassign event_text column as status column, then drop event_text column
    bills['status'] = bills['event_text']
    bills.drop(columns=['event_text'], inplace=True)
    
    return bills

bills = get_bill_status(bills, history)


# Make date_introduced column
def get_date_introduced(bills, history):
    """
    Get the earliest event_date (i.e. the date_introduced) for each bill and add date_introduced column to bills dataframe.

    Parameters:
    -----------
        bills: DataFrame containing bill data
        history: DataFrame containing the bill history data

    Returns:
    --------
        A DataFrame with date_introduced column added.
    """
    # Ensure event_date is in datetime format
    history['event_date'] = pd.to_datetime(history['event_date'], errors='coerce').dt.strftime('%m-%d-%Y')

    # Get the earliest event_date for each bill_id
    earliest_events = history.loc[history.groupby('bill_id')['event_date'].idxmin()]

    # Select the relevant columns: bill_id, event_date
    earliest_events = earliest_events[['bill_id', 'event_date']]
    
    # Rename column to date_introduced -- VERY IMPORTANT FOR AGRID STYLER FUNCTION TO WORK PROPERLY!!!
    earliest_events.rename(columns={'event_date': 'date_introduced'}, inplace=True)
    
    # Merge with bills df
    bills = bills.merge(earliest_events, on='bill_id', how='left')

    # Return the result
    return bills

bills = get_date_introduced(bills, history)

# Create bill_history as its own variable
def create_bill_history(history):
    """
    Create a DataFrame with bill_id and a full bill history
    
    Parameters:
        bills: DataFrame containing bill data
        history: DataFrame containing the bill history data
        
    Returns:
        DataFrame with bill_id and combined chunk of bill history text, which will be later formatted via utils function.
    """
    # Ensure event_date is in datetime format
    history['event_date'] = pd.to_datetime(history['event_date'])

    # Create the combined description in the desired format
    history['event_description'] = history['event_date'].dt.strftime('%Y-%m-%d') + " >> " + history['event_text']

    # Group by bill_id and combine all event descriptions into a list
    result = history.groupby('bill_id')['event_description'].apply(list).reset_index()

    # Convert the event_description list into a string format
    result['event_description'] = result['event_description'].apply(lambda x: ', '.join([f'"{event}"' for event in x]))

    # Rename the column to 'bill_history'
    result.rename(columns={'event_description': 'bill_history'}, inplace=True)

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

