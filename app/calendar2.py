#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar Page - Option 2
Created on Nov 27, 2024
@author: danyasherbini

This page of the app features a calendar of legislative deadlines and/or events, built with
html code (via streamlit html component)
"""

import os
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html


PATH = '/Users/danyasherbini/Documents/GitHub/lt-streamlit'
os.chdir(PATH)
os.getcwd()


# Show the page title and description
#st.set_page_config(page_title='Legislation Tracker', layout='wide') #can add page_icon argument
st.title('Calendar')
st.write(
    '''
    This page shows important events and deadlines in the 2025-2026 legislative cycle.
    '''
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
        'title': row['title'],
        'start': row['start'],
        'end': row['end'],
        'allDay': 'true' if row['allDay'] else 'false',
    }
    for _, row in assembly_data.iterrows()
]

################################## CALENDAR ###################################

custom_css = """
    /* Background and toolbar styling */
    #calendar {
      font-family: 'Georgia', serif;
      font-size: 14px;
    }
    .fc-toolbar {
      color: black;
      font-family: 'Georgia', serif;
      font-size: 18px;
    }
    .fc-toolbar-title {
      color: black;
    }

    /* Event styling */
    .fc-event {
      color: black;
      padding: 5px;  /* Add padding to give space for wrapping */
      white-space: normal !important;  /* Allow text wrapping */
      word-wrap: break-word;  /* Allow long words to break and wrap */
      word-break: break-word;  /* Ensure long words break onto the next line */
    }
    .fc-event-title {
      font-family: 'Georgia',
      font-size: 12x;
      word-wrap: break-word;  /* Allow event title to wrap */
      white-space: normal;  /* Ensure text wraps properly */
    }

    /* Highlight today's date */
    .fc-day-today {
      background-color: #ffffcc !important;
    }

"""

# FullCalendar html with eventClick handling
# https://fullcalendar.io
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
        initialView: 'dayGridMonth',
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


# render the calendar in Streamlit
html(calendar_html, height=600)
