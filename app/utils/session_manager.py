#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Manager
Created on Jan 6, 2025
@author: danyasherbini

Initializes session state for the app (only need to run once for the app)
"""

import streamlit as st
from utils.cache_manager import get_cached_bills, update_cached_bills

# Function to initialize session state
def initialize_session_state():
    """
    Initialize session state for 'selected_bills' if it doesn't exist.
    This will run once at the start.
    """
    if 'selected_bills' not in st.session_state:
        st.session_state.selected_bills = get_cached_bills()  # Load from cache if available

# Function to update session state with new selected bills
def update_session_state(new_bills):
    """
    Update the session state with new list of selected bills.
    """
    st.session_state.selected_bills = new_bills
    update_cached_bills(new_bills)  # Update the cache
    
    
    
