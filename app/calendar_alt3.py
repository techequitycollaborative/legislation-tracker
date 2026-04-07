#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar Page
Created on April 7, 2026
@author: danyasherbini

This page of the app features a calendar of legislative deadlines and/or events, built by 
embedding a Google Calendar URL.

Users cannot filter the calendar, but they have the option to get their own calendar URLs
for their org dashboard, my dashboard, and the AI working group dashboard.

"""

import streamlit as st
import streamlit.components.v1 as components

st.title('📅 Calendar')

with st.expander("About this page", icon="ℹ️", expanded=False):
    st.markdown(
        """
        - This calendar displays committee hearings, letter deadlines, and overall legislative events/deadlines.
        - Committee hearings are sourced from Assembly and Senate calendar websites directly, so only available events are shown.
        - Letter Deadlines are auto-generated for 7 days before a committee hearing.
        - Event times are displayed in your local time zone. See event descriptions for Pacific Time.
        """
    )

components.html(
    """
    <iframe src="https://calendar.google.com/calendar/embed?src=cc5vvi9rmid4tg94dbfrvrso1esu0v1r%40import.calendar.google.com&color=%23D50000&src=2pn9vcgp0dh8nuhm4880bv8ekr0tc34m%40import.calendar.google.com&color=%230B8043&ctz=America%2FChicago"
        style="border: 0"
        width="100%"
        height="600"
        frameborder="0"
        scrolling="no">
    </iframe>
    """,
    height=620,  # slightly taller than iframe to avoid scrollbars
)