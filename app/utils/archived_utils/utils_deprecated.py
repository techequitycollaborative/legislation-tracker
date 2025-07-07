#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils.py
Created on Oct 15, 2024
@author: danyasherbini

Deprecated general utility functions. No longer using these as data manipulation was moved to sql scripts in db folder

Note: If these are to be reactived, need to replace bill_id with openstates_bill_id

"""
import streamlit as st
import pandas as pd
import numpy as np
import re

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

###############################################################################


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

def process_bills_data(bills, history):
    bills = clean_bill_data(bills)  # Step 1: Clean the bills data
    bills = get_bill_status(bills, history)  # Step 2: Get bill status
    bills = get_date_introduced(bills, history)  # Step 3: Get date introduced
    bills = create_bill_history(bills, history)  # Step 4: Create bill history
    bills['bill_history'] = bills['bill_history'].apply(ensure_set).apply(format_bill_history) #Step 5: Format bill history
    bills = get_bill_topics(bills, keywords) # Step 6: Get bill topics
    return bills
