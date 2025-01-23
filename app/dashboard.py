#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing out My Dashboard
Created on Dec 2, 2024
@author: danyasherbini

Page to add bills to user's private dashboard
"""


import streamlit as st
import pandas as pd
from utils.aggrid_styler import draw_bill_grid


# Page title
st.title('Dashboard')

# Clear dashboard button
col1, col2 = st.columns([3, 1])
with col2:
    if st.button('Clear Dashboard'):
        st.session_state.selected_bills = []  # Clear session state
        st.success('Dashboard cleared!')

# Display selected bills in the dashboard
if 'selected_bills' in st.session_state:
    st.write('Selected Bills:')
    dashboard_df = pd.DataFrame(st.session_state.selected_bills)
    draw_bill_grid(dashboard_df)
else:
    st.write('No bills selected yet.')
    



