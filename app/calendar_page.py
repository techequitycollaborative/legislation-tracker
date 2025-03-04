#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar Page - Option 2
Created on Nov 27, 2024
@author: danyasherbini

This page of the app features a calendar of legislative deadlines and/or events, built with
a custom streamlit calendar component.
"""

import pandas as pd
import streamlit as st
from streamlit_calendar import calendar


# Show the page title and description
# st.set_page_config(page_title='Legislation Tracker', layout='wide') # can add page_icon argument
st.title('Calendar')
st.write(
    '''
    This page shows important dates and deadlines for the current legislative cycle.
    '''
)

############################ LOAD AND SET UP DATA #############################

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_calendar_data():
    assembly_data = pd.read_csv('./data/assembly_dates.csv')
    return assembly_data

assembly_data = load_calendar_data()

# Convert from csv to json format
calendar_events = [
    {
        'title': row['title'],
        'start': row['start'],
        'end': row['end'],
        'allDay': 'true' if row['allDay'] else 'false',
    }
    for _, row in assembly_data.iterrows()
]

################################## CSS ###################################

# Load external CSS file
def load_css(file_path):
    with open(file_path, "r") as f:
        return f"<style>{f.read()}</style>"

# Read the CSS file
custom_css = load_css("./styles/calendar.css")


################################## BUILD CALENDAR ###################################
# This streamlit component is built from FullCalendar: https://fullcalendar.io

# Calendar options
calendar_options = {
  "selectable":True,
  "themeSystem": 'standard',
  "initialView": 'dayGridMonth',
  "dayMaxEventsRows": True,
  "handleWindowResize": True, #Ensures calendar resizes on window resize
  "headerToolbar": {
    "left": 'today prev,next',
    "center": 'title',
    "right": 'dayGridMonth,dayGridWeek,listMonth',
    }}

# Render the calendar
calendar = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css,
    key='calendar', # Assign a widget key to prevent state loss
    )

################################################################################################

# Alternate option to build calendar with html

from streamlit.components.v1 import html

calendar_html = f"""
<!DOCTYPE html>
<html>
<head>
  <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css' rel='stylesheet' />
  <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js'></script>
  <style>
    {custom_css} <!-- custom CSS here -->
  </style>
</head>
<body>
  <div id='calendar'></div>
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      var calendarEl = document.getElementById('calendar');
      var calendar = new FullCalendar.Calendar(calendarEl, {{
        themeSystem: 'standard',
        initialView: 'dayGridMonth',
        dayMaxEventsRows: true,
        handleWindowResize: true,  // Ensures calendar resizes on window resize
        headerToolbar: {{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,dayGridWeek,listMonth'
        }},
        events: {calendar_events},  <!-- events are here -->
        eventClick: function(info) {{
          alert('Event: ' + info.event.title);
        }}
      }});
      calendar.render();
    }});
  </script>
</body>
</html>
"""

# render the calendar with html
#html(calendar_html, height=800, width=800)