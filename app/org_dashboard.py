#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Org Dashboard
Created on March 28, 2025
@author: danyasherbini

Page to add bills to an org's private dashboard
"""

import streamlit as st
import pandas as pd
from utils.aggrid_styler import draw_bill_grid
from utils.utils import format_bill_history, get_bill_topics, keywords, to_csv
from db.query import get_my_dashboard_bills
from utils.display_utils import display_dashboard_details, format_bill_history_dashboard


# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'authenticated' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Access user info
org_id = st.session_state.get('org_id')
org_name = st.session_state['org_name']
user_email = st.session_state['user_email']

# Page title
st.title(f"{org_name}'s Dashboard")

st.write("This page will be available only to users of a specific organization.")


