#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bills Page: Topic as Tag
Created on Jan 27, 2025
@author: danyasherbini

Bills page with:
    - Bill table with column for 'topic' that is filterable based on keyword
    - Bill details with text
"""

import streamlit as st
import pandas as pd
from db.query import get_data
from utils import aggrid_styler
from utils.general import to_csv, keyword_to_topics, global_keyword_regex, get_bill_topics_multiple
from utils.bills import display_bill_info_text
from utils.bill_history import format_bill_history
from itertools import chain # For flattening bill topic list in bill topic expander

# Page title and description
st.title('📝 Bills')

current_session = '2025-2026'

st.expander("About this page", icon="ℹ️", expanded=False).markdown(f""" 
- This page shows California assembly and senate bill information for the {current_session} legislative session.
- Use the column filters to search for specific bills by bill number, author, topic, and more.    
- Click on a bill to view additional details and add the bill to your dashboards.                                                               
- Please note that this page may take a few moments to load due to the volume of data.                                              
""")

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")

############################ LOAD AND PROCESS BILLS DATA #############################

@st.cache_data(show_spinner="Loading bills data...",ttl=60 * 60 * 11.5)
def load_bills_table():
    # Get data
    bills = get_data()

    # Minor data processing
    # Convert to datetime (without formatting yet)
    bills['date_introduced'] = pd.to_datetime(bills['date_introduced'], errors='coerce')
    bills['bill_event'] = pd.to_datetime(bills['bill_event'], errors='coerce')

    # Sort bills table by most recent date_introduced
    bills = bills.sort_values(by='last_updated_on', ascending=False)

    # Now remove timestamp from date_introduced and bill_event (for formatting purposes in other display areas)
    # KEEP AS Y-M-D FORMAT FOR AG GRID DATE FILTERING TO WORK
    bills['date_introduced'] = pd.to_datetime(bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestamp from date introduced
    bills['bill_event'] = pd.to_datetime(bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
    bills['last_updated_on'] = pd.to_datetime(bills['last_updated_on']).dt.strftime('%Y-%m-%d') # Remove timestamp from last_updated_on

    # Get bill topic and format bill history
    bills = get_bill_topics_multiple(
         bills, 
         keyword_dict = keyword_to_topics,
         keyword_regex = global_keyword_regex
    )  # Get bill topics
    bills['bill_history'] = bills['bill_history'].apply(format_bill_history) #Format bill history
    return bills

# Initialize session state for bills and load bills if not set
if 'bills' not in st.session_state:
     st.session_state.bills = load_bills_table()

# Assign bills variable to session state bills for future access / to enable caching
bills = st.session_state.bills

# Initialize session state for selected bills
if 'selected_bills' not in st.session_state:
    st.session_state.selected_bills = []

# Mapping between user-friendly labels and internal theme values
theme_options = {
    'narrow': 'streamlit',
    'wide': 'alpine'
}

# Initialize session state for theme if not set
if 'theme' not in st.session_state:
    st.session_state.theme = 'streamlit'  # Default theme

# Reverse mapping to get the label from the internal value
label_from_theme = {v: k for k, v in theme_options.items()}

# Create a two-column layout
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    selected_label = st.selectbox(
        'Change grid theme:',
        options=list(theme_options.keys()),
        index=list(theme_options.keys()).index(label_from_theme[st.session_state.theme])
    )

with col2:    
    st.markdown("")

with col3:
    st.download_button(
        label='Download Bills',
        data=to_csv(bills),
        file_name='bills.csv',
        mime='text/csv',
        use_container_width=True
    )

# Update session state if the user picks a new theme
selected_theme = theme_options[selected_label]
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme

# Use the persisted theme
theme = st.session_state.theme

# Display list of bill topics above the table
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    # Display count of total bills above the table
    total_bills = len(bills)
    st.markdown(f"#### Total bills: {total_bills:,}")

with col2:
    st.markdown("")

with col3:
    # Flatten the list of lists in 'bill_topic' and clean whitespace
    unique_topics = sorted(set(
        topic.strip()
        for topic in chain.from_iterable(bills['bill_topic'])
        if isinstance(topic, str) and topic.strip()
    ))

    # Display bill topics via dialog pop-up
    @st.dialog("View List of Bill Topics")
    def show_topic_dialog():
        st.markdown(
            " | ".join([f"`{topic}`" for topic in unique_topics])
        )
    # Trigger the dialog with a button
    st.button("*View List of Bill Topics*", on_click=show_topic_dialog, use_container_width=True)

# Display the aggrid table
data = aggrid_styler.draw_bill_grid(bills, theme=theme)
    
selected_rows = data.selected_rows

if selected_rows is not None and len(selected_rows) != 0:
        display_bill_info_text(selected_rows)



