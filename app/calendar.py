#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar Page - Option 1
Created on Nov 26, 2024
@author: danyasherbini

This page of the app features a calendar of legislative deadlines and/or events, built with
a custom streamlit component.
"""

import os
import pandas as pd
import streamlit as st
from streamlit_calendar import calendar


PATH = '/Users/danyasherbini/Documents/GitHub/lt-streamlit'
os.chdir(PATH)
os.getcwd()


# Show the page title and description
#st.set_page_config(page_title='Legislation Tracker', layout='wide') #can add page_icon argument
st.title('Calendar - Option 1')
st.write(
    """
    This page shows important deadlines and/or events in the legislative cycle. 
    """
)

############################ LOAD AND SET UP DATA #############################

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_calendar_data():
    assembly_data = pd.read_csv('/Users/danyasherbini/Documents/GitHub/lt-streamlit/data/assembly_dates.csv')
    return assembly_data

assembly_data = load_calendar_data()

# convert from csv to json format
calendar_events = [
    {
        "title": row["title"],
        "start": row["start"],
        "end": row["end"],
        "allDay": "true" if row["allDay"] else "false",
    }
    for _, row in assembly_data.iterrows()
]


################################## CALENDAR ###################################
   
calendar_options = {
    #"editable": "true",
    "selectable": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,dayGridWeek,listMonth",
    },
    #"slotMinTime": "06:00:00",
    #"slotMaxTime": "18:00:00",
    "initialView": "dayGridMonth",
    # can add additional features to the calendar, such as locations like rooms or buildings:
    #"resourceGroupField": "building",
    #"resources": [
    #    {"id": "a", "building": "Building A", "title": "Building A"},
    #    {"id": "b", "building": "Building A", "title": "Building B"},
    #    {"id": "c", "building": "Building B", "title": "Building C"},
    #],
}


# custom css formatting
custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""

# display calendar
calendar = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)
