#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils.py
Created on Oct 15, 2024
@author: danyasherbini

General utility functions for Legislation Tracker:
- get_bill_topics: Tags bills with topics based on keywords.
- get_bill_topics_multiple: Tags bills with multiple topics based on keywords.
- add_bill_to_dashboard: Adds a selected bill to the dashboard.
- to_csv: Converts a DataFrame to CSV for download.

"""
import streamlit as st
import pandas as pd
import numpy as np
import re


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
        #pattern = '|'.join(re.escape(word) for word in keywords)
        # Create a regex pattern to match whole words/phrases only
        pattern = '|'.join(rf'\b{re.escape(word)}\b' for word in keywords)
        # Apply the label where the pattern matches in the bill_name column -- ignoring NA values and ignore case
        df.loc[df['bill_name'].str.contains(pattern, na=False, case=False), 'bill_topic'] = label

    return df


# Keyword/topic mapping
keywords = {
    ('artificial intelligence', 'algorithm', 'automated', 'automated decision-making', 'AI', 'algorithmic', 'autonomous', 'data centers', 'data center', 'training data','data privacy','CCPA','robotics','surveillance pricing', 'deepfake', 'computer science'): 'AI',
    ('housing', 'eviction', 'tenant', 'renter', 'tenancy', 'house', 'rental', 'rent', 'rental pricing', 'mortgage'): 'Housing',
    #('health', 'healthcare', 'health care', 'medical', 'medication', 'medicine', 'pharmaceutical', 'pharmacy', 'health insurance', 'insurance', 'health plan'): 'Health',
    ('work', 'worker', 'workplace', 'workplace surveillance', 'labor', 'employment', 'gig economy', 'gig work', 'contract work', 'contract workers', 'content moderator', 'data labeler', 'data labeller', 'ghost work','robo bosses','wages','salary','salaries'): 'Labor'
}

###############################################################################

def get_bill_topics_multiple(df, keyword_dict):
    """
    Tags each bill in the DataFrame with ONE OR MORE TOPICS based on keywords found in the 'bill_name' column.

    Parameters:
        - df (DataFrame): Input DataFrame containing a 'bill_name' column.
        - keyword_dict (dict): A dictionary where keys are tuples of keywords and
                               values are the corresponding topics to apply.

    Returns:
        - df (DataFrame): A DataFrame with a new 'bill_topic' column containing a list of assigned topics.
    """

    # Initialize the 'bill_topic' column with empty lists
    df['bill_topic'] = [[] for _ in range(len(df))]

    for keywords, label in keyword_dict.items():
        # Use word boundaries to prevent partial matches
        pattern = '|'.join(rf'\b{re.escape(word)}\b' for word in keywords)
        
        # Find which rows match this pattern (case-insensitive)
        matches = df['bill_name'].str.contains(pattern, na=False, case=False, regex=True)
        
        # Append the label to the matching rows
        df.loc[matches, 'bill_topic'] = df.loc[matches, 'bill_topic'].apply(lambda x: x + [label])

    return df



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
            'bill_text': text,
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

###############################################################################

def transform_name(name):
    # Re-formats legislator names
    parts = re.split(r"\s+", name.replace(",", ""))
    no_title = len(name.split(",")) == 1
    if no_title:
        return f"{parts[-1]}, {' '.join(parts[0:-1])}"
    else:
        return f"{parts[-2]}, {' '.join(parts[0:-2])}, {parts[-1].replace(',', '')}"