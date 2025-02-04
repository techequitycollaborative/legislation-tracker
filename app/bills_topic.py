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
from utils.utils import display_bill_info_text, get_bill_topics, to_csv, keywords

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
bills = get_data()

# remove timestampe from date introduced
bills['date_introduced'] = pd.to_datetime(bills['date_introduced']).dt.strftime('%Y-%m-%d')

# get bill topics
bills = get_bill_topics(bills, keyword_dict= keywords)  

# Initialize session state for selected bills
if 'selected_bills' not in st.session_state:
    st.session_state.selected_bills = []
    
# Create a two-column layout
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("")

with col2:
    st.download_button(
            label='Download Data as CSV',
            data=to_csv(bills),
            file_name='selected_bills.csv',
            mime='text/csv',
            use_container_width=True
        )

# Display the aggrid table
data = aggrid_styler.draw_bill_grid(bills)
    
selected_rows = data.selected_rows

if selected_rows is not None and len(selected_rows) != 0:
        display_bill_info_text(selected_rows)


