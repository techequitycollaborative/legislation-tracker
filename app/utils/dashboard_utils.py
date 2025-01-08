#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 17:16:13 2025

@author: danyasherbini
"""

import streamlit as st
from utils.session_manager import update_session_state

def add_bill_to_dashboard(number, name, author, coauthors, status, date, chamber, link, text, history):
    """
    Adds the selected bill to the dashboard and updates the session state and cache.
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
        update_session_state(st.session_state.selected_bills)  # Update session and cache
        st.success(f'Bill {number} added to dashboard!')
    else:
        st.warning(f'Bill {number} is already in the dashboard.')

