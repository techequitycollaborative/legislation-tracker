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
from yaml import safe_load
from collections import defaultdict

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

###############################################################################

# TODO: find a better place for this to live - maybe in the session state or populated in the database itself...
# Load topic_keywords.yaml as a dictionary
with open("utils/topic_keywords.yaml") as f:
    topic_config = safe_load(f)

# Initialize dictionary mapping
keyword_to_topics = defaultdict(list) # keyword, List[topic1, topic2]
all_keywords = set() # A global set of keywords for optimized DF updates

# Fill mapping and update global set
for topic, data in topic_config.items():
    # Select keywords if available
    keywords = data["keywords"]

    # if a topic does not have keywords, treat it like its own keyword
    if not keywords:
        keywords = [topic] 
    
    # Now update the keyword -> topic mapping
    for keyword in keywords:
        # normalize to lowercase
        keyword_to_topics[keyword.lower()].append(topic)
    
    # Finally update the global set
    all_keywords.update(keywords) 

# Create global regex pattern
pattern = '|'.join(rf'\b{re.escape(word)}\b' for word in all_keywords)
global_keyword_regex = re.compile(rf"\b{pattern}\b", flags=re.IGNORECASE)

def get_topics_for_row(current_keywords, keyword_dict):
    """
    Tags each bill in a row's matching keywords with ONE OR MORE TOPICS 

    Parameters:
        - current_keywords (list): A list of matching keywords
        - keyword_dict (dict): A dictionary where keys are tuples of keywords and
                               values are the corresponding topics to apply.

    Returns:
        - topics (list): A list of unique topics that correspond to the set of keywords
    """
    topics = set() # store unique set of matched topics
    if current_keywords:    
        for kw in current_keywords:
            # Update the set with a list of topics based on normalized keyword
            found = keyword_dict.get(kw, [])
            topics.update(found)

    # Check if topics were detected
    if topics:
        return list(topics)
    else:
        return ["Other"]


def get_bill_topics_multiple(df, keyword_dict, keyword_regex):
    """
    Tags each bill in the DataFrame with ONE OR MORE TOPICS based on keywords found in the 'bill_name' column.

    Parameters:
        - df (DataFrame): Input DataFrame containing a 'bill_name' column.
        - keyword_dict (dict): A dictionary where keys are tuples of keywords and
                               values are the corresponding topics to apply.
        - keyword_regex (regex object): compiled regular expression pattern consisting of all keywords

    Returns:
        - df (DataFrame): A DataFrame with a new 'bill_topic' column containing a list of assigned topics.
    """
    # Extract all keyword matches in a bill name
    df["keyword_matches"] = df["bill_name"].str.lower().str.findall(keyword_regex)

    # Map keyword matches to a topic list
    df["bill_topic"] = df["keyword_matches"].apply(
        lambda keywords: get_topics_for_row(keywords, keyword_dict)
    )
    # Drop helper column
    df = df.drop("keyword_matches", axis=1)
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

###############################################################################

def clean_markdown(text):
    # Un-escape newlines
    result = text.replace("\\n", "\n")

    # Escape Markdown special characters
    result = result.replace("$", "\$")
    result = result.replace("%", "\%")
    result = result.replace("+", "\+")
    result = result.replace("-", "\-")
    result = result.replace("!", "\!")  

    return result
###############################################################################

def get_topic_color(topic):
    # Handle empty/null case first (returns light gray)
    if not topic or topic == "0":
        return "#f0f0f0"  # Light gray for empty/default
    
    # Define color mapping for each category 
    color_map = {
        "AI": "#E1D5E7",  # Soft lavender
        "Discrimination": "#F5C2C7",  # Dusty rose
        "Education": "#B8D8EB",  # Pale sky blue
        "Environment": "#C3E6C3",  # Mint green
        "Health": "#F8D6B3",  # Peach
        "Housing": "#C9C9EE",  # Periwinkle
        "Labor": "#FFE0B3",  # Pale amber
        "Data, Surveillence, Privacy": "#B3E0E6",  # Powder blue
        "Disinformation": "#D4C5C0",  # Warm gray
        "Judicial System": "#B3B3D6",  # Soft denim
        "Safety": "#E6B3B3",  # Blush pink
        "Other": "#E0E0E0"   # Light gray
    }
    
    # Return the corresponding color or default if not found
    return color_map.get(topic, "#FFFFFF")  # ultimate fallback on white if needed

def bill_topic_grid(bill_topic_lst):
    # TODO: decide if we want to display something for bills without set topics
    if not bill_topic_lst:
        bill_topic_lst = ["Other"]  # Default for empty list
    
    # Always use 3 columns layout
    cols = st.columns(3)
    
    for idx, topic in enumerate(bill_topic_lst):
        # Use modulo to select 1st, 2nd or 3rd column
        col = cols[idx % 3]

        # Transform topic text for display assuming the null case is in scope
        display_text = topic if topic != "0" else "None set"
        
        with col:
            container = st.container() # Create a container to fill with HTML
            container.markdown(
                f"""
                <div style="
                    background-color: {get_topic_color(topic)};
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                    height: 70px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    {display_text}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Visual indication of empty slots
    remaining_slots = (3 - (len(bill_topic_lst) % 3)) % 3
    if remaining_slots > 0 and len(bill_topic_lst) > 0:
        for i in range(remaining_slots):
            cols[(len(bill_topic_lst) + i) % 3].container()
    return