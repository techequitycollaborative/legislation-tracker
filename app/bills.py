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
from utils.utils import get_bill_topics, to_csv, keywords, format_bill_history
from utils.display_utils import display_bill_info_text

# Page title and description
st.title('Bills')

current_session = '2025-2026'

st.write(
    f"""
    This page shows California assembly and senate bill information for the {current_session} legislative session. 
    Please note that the page may take a few moments to load.
    """
)

############################ LOAD AND PROCESS BILLS DATA #############################

# Get data
bills = get_data()

# Minor data processing 
bills['date_introduced'] = pd.to_datetime(bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestamp from date introduced
bills['bill_event'] = pd.to_datetime(bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
bills = get_bill_topics(bills, keyword_dict= keywords)  # Get bill topics
bills['bill_history'] = bills['bill_history'].apply(format_bill_history) #Format bill history

# Initialize session state for selected bills
if 'selected_bills' not in st.session_state:
    st.session_state.selected_bills = []

# Initialize session state for theme if not set
if 'theme' not in st.session_state:
    st.session_state.theme = 'streamlit'  # Default theme
    
# Create a two-column layout
col1, col2, col3 = st.columns([1, 7, 2])
with col1:
    selected_theme = st.selectbox(
        'Change grid theme:',
        options=['streamlit', 'alpine', 'balham', 'material'],
        index=['streamlit', 'alpine', 'balham', 'material'].index(st.session_state.theme)
    )
    
with col2:    
    st.markdown("")

with col3:
    st.download_button(
            label='Download Data as CSV',
            data=to_csv(bills),
            file_name='selected_bills.csv',
            mime='text/csv',
            use_container_width=True
        )


# Update session state if the user picks a new theme
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme

# Use the persisted theme
theme = st.session_state.theme 

# Display count of total bills above the table
total_bills = len(bills)
st.markdown(f"#### Total bills: {total_bills:,}")

# Display the aggrid table
data = aggrid_styler.draw_bill_grid(bills, theme=theme)
    
selected_rows = data.selected_rows

if selected_rows is not None and len(selected_rows) != 0:
        display_bill_info_text(selected_rows)



