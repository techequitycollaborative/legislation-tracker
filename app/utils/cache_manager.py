#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: Cache Manager
Created on Jan 6, 2025
@author: danyasherbini

Ensures bills added to the dashboard are cached and don't disappear upon page refresh.
"""

import streamlit as st

# Cache function to store and retrieve the list of selected bills
@st.cache_data
def get_cached_bills():
    """
    Retrieve the cached list of bills. If none exist, return an empty list.
    """
    return []

@st.cache_data
def update_cached_bills(new_bills):
    """
    Update the cached list of bills.
    """
    return new_bills
