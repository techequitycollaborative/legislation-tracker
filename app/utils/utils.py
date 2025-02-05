#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils.py
Created on Oct 15, 2024
@author: danyasherbini

Custom functions for Legislation Tracker streamlit app

"""
import streamlit as st
import pandas as pd
import numpy as np
import re

###############################################################################

def clean_bill_data(bills):
    """
    Clean up the bills DataFrame by:
    - Adding a 'chamber' column based on 'origin_chamber_id'
    - Dropping unnecessary columns
    - Sorting by 'bill_number'

    Parameters:
    -----------
        bills: DataFrame containing bill data

    Returns:
    --------
        Cleaned DataFrame
    """
    # Make 'chamber' column and assign values
    bills['chamber'] = np.where(bills['origin_chamber_id'] == 1, 'Assembly', 'Senate')

    # Drop unnecessary columns
    bills = bills.drop(['openstates_bill_id', 'committee_id', 'origin_chamber_id'], axis=1)

    # Sort by 'bill_number'
    bills = bills.sort_values('bill_number', ascending=True)

    return bills


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

###############################################################################

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

###############################################################################

def create_bill_history(bills, history):
    """
    Create a DataFrame with bill_id and a full bill history
    
    Parameters:
        bills: DataFrame containing bill data
        history: DataFrame containing the bill history data
        
    Returns:
        DataFrame with bill_id and combined chunk of bill history text, which will be later formatted via format_bill_history utils function.
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
    
    # Merge with bills table
    bills = bills.merge(result, on='bill_id', how='left')

    return bills

###############################################################################

def format_bill_history(bill_history):
    '''
    Reformats bill_history variable into a descending chronological list for the bill history section of the bill details page.
    '''
    if not bill_history:
        return ""

    # Split entries using ", " (assuming this is how they are separated)
    entries = bill_history.split(", ")

    # Process entries into tuples (date, event)
    formatted_entries = []
    for entry in entries:
        # Ensure the format is `YYYY-MM-DD >> Event`
        match = re.match(r"^(\d{4}-\d{2}-\d{2})\s*>>\s*(.+)", entry)
        if match:
            date, event = match.groups()
            formatted_entries.append((date, event))

    # Sort by date in descending order
    formatted_entries.sort(reverse=True, key=lambda x: x[0])

    # Format back into readable Markdown-style text
    return "\n\n".join([f"**{date}:** {event}" for date, event in formatted_entries])


###############################################################################

def get_bill_topics(df, keyword_dict):
    """
    Tags each bill in the DataFrame with a topic based on keywords found in the bill_name column.

    Parameters:
        - df (DataFrame): Input DataFrame containing a 'bill_name' column.
        - keywords (dict): A dictionary where keys are tuples of keywords and
                            values are the corresponding topics to apply.

    Returns:
        -df (DataFrame): A DataFrame with a new 'bill_topic' column containing the assigned topic.
    """

    # Initialize the 'bill_topic' column with default value (e.g., "Uncategorized")
    df['bill_topic'] = 'Uncategorized'

    for keywords, label in keyword_dict.items():
        # Ensure the keywords are joined into a single string for regex
        pattern = '|'.join(re.escape(word) for word in keywords)
        # Apply the label where the pattern matches in the bill_name column
        df.loc[df['bill_name'].str.contains(pattern, na=False, case=False), 'bill_topic'] = label

    return df


# Keyword/topic mapping
keywords = {
    ('artificial intelligence', 'algorithm', 'automated'): 'AI',
    ('housing', 'eviction', 'tenant', 'renter'): 'Housing',
    ('worker', 'labor', 'gig economy', 'contract workers', 'content moderator', 'data labeler', 'data labeller', 'ghost work'): 'Labor'
}


###############################################################################

def process_bills_data(bills, history):
    bills = clean_bill_data(bills)  # Step 1: Clean the bills data
    bills = get_bill_status(bills, history)  # Step 2: Get bill status
    bills = get_date_introduced(bills, history)  # Step 3: Get date introduced
    bills = create_bill_history(bills, history)  # Step 4: Create bill history
    bills['bill_history'] = bills['bill_history'].apply(ensure_set).apply(format_bill_history) #Step 5: Format bill history
    bills = get_bill_topics(bills, keywords) # Step 6: Get bill topics
    return bills

###############################################################################

def add_bill_to_dashboard(number, name, author, coauthors, status, date, chamber, link, text, history):
    """
    Adds a selected bill from the bills page to the dashboard page via the 'Add to Dashboad' button.
    """
    # Check if the bill is already in the selected_bills list
    if not any(bill['bill_number'] == number for bill in st.session_state.selected_bills):
        bill = {
            'bill_number': number,
            'bill_name': name,
            'author': author,
            'coauthors': coauthors,
            'status': status,
            'date_introduced': date,
            'chamber': chamber,
            'leginfo_link': link,
            'full_text': text,
            'bill_history': history
        }
        
        # Add the bill to the session state
        st.session_state.selected_bills.append(bill)
        st.success(f'Bill {number} added to dashboard!')
    else:
        st.warning(f'Bill {number} is already in the dashboard.')


###############################################################################

from io import BytesIO

def to_csv(df) -> bytes:
    '''
    Downloads data from the app to csv file. To be used with st.download_button()
    '''
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output.getvalue()


