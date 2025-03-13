#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar Page - Option 2
Created on Nov 27, 2024
@author: danyasherbini

This page of the app features a calendar of legislative deadlines and/or events, built with
a custom streamlit calendar component.

IMPORTANT: THIS PAGE'S FILE CANNOT BE NAMED 'CALENDAR' BECAUSE IT WILL OVERRIDE THE STREAMLIT 'CALENDAR.PY' MODULE. You will get a warning if you try to do this.
That's why it's named calendar_page.py.
"""

import pandas as pd
import streamlit as st
from streamlit_calendar import calendar
from db.query import query_table


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

# Load legislative calendar events for 2025-2026 leg session (this is in a CSV file for now)
@st.cache_data
def load_leg_events():
    leg_events = pd.read_csv('./data/20252026_leg_dates.csv')
    return leg_events

leg_events = load_leg_events()

# Load events specific to individual bills
@st.cache_data
def load_bill_events():
    # Query processed_bills table which contains both bill and bill events info
    bills = query_table('public', 'processed_bills_20252026')

    # Subset only these columns (for now)
    bill_events = bills[['bill_number','bill_event','event_text','chamber']] 

    # Get only bills that have a bill event
    bill_events = bill_events.dropna(subset=['bill_event'])

    # Remove timestamp from bill_event
    bill_events['bill_event'] = pd.to_datetime(bill_events['bill_event']).dt.strftime('%Y-%m-%d') 

    # Add column for allDay
    bill_events['allDay'] = True 

    return bill_events

bill_events = load_bill_events()

# Convert data to JSON format (necessary for streamlit_calendar)
calendar_events = []

# Define event classes based on type
event_classes = {
    "Legislative": "legislative",
    "Senate": "senate",
    "Assembly": "assembly",
}

# Convert legislative events
for _, row in leg_events.iterrows():
    calendar_events.append({
        'title': row.get('title', 'Legislative Event'),  # Default title if missing
        'start': row['start'],
        'end': row['end'],
        'allDay': 'true' if row['allDay'] else 'false',  # All legislative events are all-day
        'type': 'Legislative',
        'className': event_classes.get('Legislative', '')  # Assign class -- corresponds to color coding from css file
    })

# Convert bill events
for _, row in bill_events.iterrows():
    event_type = row['chamber']
    calendar_events.append({
        'title': f"{row['bill_number']} - {row['event_text']}",  # Concatenate bill_number and event_text to create title
        'start': row['bill_event'], #if pd.notna(row['bill_event']) and row['bill_event'] else None,  # Use bill_event or null
        'end': row['bill_event'], #if pd.notna(row['bill_event']) and row['bill_event'] else None,  # Use bill_event or null
        'allDay': 'true' if row['allDay'] else 'false',  # Making bill events all day for now until we can add specific event times
        'type': event_type,
        'className': event_classes.get(event_type, '')  # Assign class -- corresponds to color coding from css file
    })

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
    "selectable": True,
    # JavaScript function for event click -- this isn't working and needs to be reconfigured
    "eventClick": """
        function(info) {
            alert('Event: ' + info.event.title);  // Show event title on click
        }
    """,  
    "themeSystem": "standard",
    "initialView": "dayGridMonth",
    "dayMaxEventsRows": True,  
    "handleWindowResize": True,  
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "listMonth,dayGridWeek,dayGridMonth"
    },

    # Customize toolbar button text
    "buttonText": {
        "today": "Today",
        "dayGridMonth": "Month",  # Customize the text for the month view button
        "dayGridWeek": "Week",  # Customize the text for the week view button
        "listMonth": "Day",  # Customize the text for the list view button
    }
}


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