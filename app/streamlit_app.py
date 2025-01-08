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
import requests
from io import BytesIO

# Pages
bills_tabs = st.Page('bills_tabs.py', title='Bills - Tabs', icon='📝')
bills_multi = st.Page('bills_multiselect.py', title='Bills - Multi-Select', icon='📝')
legislators = st.Page('legislators.py', title='Legislators', icon='💼')
calendar = st.Page('calendar2.py', title='Calendar', icon='📅')
dashboard = st.Page('dashboard.py', title='My Dashboard', icon='📌')

# Build navigation bar
pg = st.navigation([bills_tabs, bills_multi,legislators,calendar, dashboard])
st.set_page_config(page_title='Legislation Tracker', layout='wide')

# Add logo
logo_url = 'https://github.com/techequitycollaborative/legislation-tracker/blob/main/app/assets/logo.png'
response = requests.get(url_icon)
logo = Image.open(BytesIO(response.content))

st.logo(
    logo,
    link="https://techequity.us"
)

# Run the pages
pg.run()