#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sketching Leg Tracker using Streamlit
Created on Oct 2, 2024
@author: danyasherbini

This script sketches a prototype of the Legislation Tracker app using 
Streamlit, an open-source framework to build data apps in Python.
"""

import streamlit as st

# Pages
bills_tabs = st.Page('bills_tabs.py', title='Bills - Tabs', icon='📝') # not using this page right now, but leaving here as an option
bills_multi = st.Page('bills_multiselect.py', title='Bills', icon='📝')
legislators = st.Page('legislators.py', title='Legislators', icon='💼')
calendar = st.Page('calendar2.py', title='Calendar', icon='📅')
dashboard = st.Page('dashboard.py', title='My Dashboard', icon='📌')

# Build navigation bar
pg = st.navigation([bills_multi,legislators,calendar, dashboard])
st.set_page_config(page_title='Legislation Tracker', layout='wide')

# Add logo
logo = './assets/logo.png'

st.logo(
    logo,
    link="https://techequity.us"
)

# Run the pages
pg.run()