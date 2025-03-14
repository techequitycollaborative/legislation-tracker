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
st.markdown(
    '''
    This calendar displays overall legislative events and deadlines, as well as bill-specific events such as when a bill is scheduled to be discussed in a committee meeting or floor hearing.
    
    Use the filters on the left to search for a specific bill event or filter by event type.
    '''
)
st.markdown(" ")
st.markdown(" ")

############################ LOAD DATA #############################

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


######################### ADD FILTER / SIDE BAR ###################################

######################### ADD FILTER / SIDE BAR ###################################

# Define event classes based on type
event_classes = {
    "Legislative": "legislative",
    "Senate": "senate",
    "Assembly": "assembly",
}

# Get unique bill numbers for the bill filter -- these are the bills that have events
unique_bills = sorted(bill_events['bill_number'].unique())

# Add bill filter with search functionality
st.sidebar.markdown("### Filter by Bill")

# Initialize variables to handle both filtering scenarios
selected_types = []
bill_filter_active = False
selected_bills_for_calendar = []

# Option to select from dashboard bills
show_dashboard_bills = st.sidebar.checkbox("Only show events for bills from My Dashboard")

# Determine eligibility for dashboard bill checkbox
if show_dashboard_bills:
    if 'user_info' not in st.session_state:
        st.sidebar.warning("User not authenticated. Login to see dashboard bills.")
        selected_bills_for_calendar = []
        bill_filter_active = False
    elif 'dashboard_bills' not in st.session_state or st.session_state.dashboard_bills is None or len(st.session_state.dashboard_bills) == 0:
        st.sidebar.info("No bills saved to your dashboard. Go to the Bills page to add bills to your dashboard.")
        selected_bills_for_calendar = []
        bill_filter_active = False
    else:
        # Use the bills directly from session state
        dashboard_bills = st.session_state.dashboard_bills['bill_number'].unique().tolist()
        selected_bills_for_calendar = dashboard_bills
        bill_filter_active = True
        #st.sidebar.success(f"Showing {len(selected_bills_for_calendar)} bills from dashboard")
elif not show_dashboard_bills:
    # If not eligible for dashboard bill checkbox, show a multiselect search widget for all bills that have events
    unique_bills = sorted(bill_events['bill_number'].unique())
    selected_bills_for_calendar = st.sidebar.multiselect(
        "Select specific bills:",
        options=unique_bills,
        default=[],  # No default selection
        help="Type to search for specific bill numbers. Only bills that have events will appear."
    )
    if len(selected_bills_for_calendar) > 0: 
        bill_filter_active = True

# If bill filter is not active (i.e. dashboard checkbox is not selected AND bill multiselect is empty), then event type filter is active:
if not bill_filter_active:
    st.sidebar.markdown("### Filter by Event Type")
    # Multi-select filter with event types
    selected_types = st.sidebar.multiselect(
        "Select event type(s):",
        options=list(event_classes.keys()),
        default=list(event_classes.keys())  # Default: Show all
    )
elif bill_filter_active == True:
    # If bill filter IS active, then turn off filter
    # This effectively bypasses the event type filter
    #selected_types = list(event_classes.keys())
    st.sidebar.markdown("### Filter by Event Type")
    st.sidebar.info("Event type filter is disabled when specific bills are selected.")

######################### CONVERT DATA ###################################

def filter_events(selected_types, selected_bills_for_calendar, bill_filter_active):
    '''
    Filters calendar events by bill and event type, and converts data to json format for rendering in streamlit calendar.
    '''
    # Initiate empty list of calendar events
    calendar_events = []
    
    # If filtering by bills (either dashboard bills or individually selected bills)
    if bill_filter_active:
        
        # Filter the bill_events DataFrame to only include selected bills
        filtered_bill_events = bill_events[bill_events['bill_number'].isin(selected_bills_for_calendar)]
        
        # Add each filtered bill event to the calendar event list 
        for _, row in filtered_bill_events.iterrows():
            
            # Convert to JSON
            calendar_events.append({
                'title': f"{row['bill_number']} - {row['event_text']}", # Concatenate bill_number and event_text to create title
                'start': row['bill_event'], #if pd.notna(row['bill_event']) and row['bill_event'] else None,  # Use bill_event or null
                'end': row['bill_event'],  #if pd.notna(row['bill_event']) and row['bill_event'] else None,  # Use bill_event or null
                'allDay': 'true' if row['allDay'] else 'false', #  Making bill events all day for now until we can add specific event times
                'type': 'Assembly' if row['chamber'] == 'Assembly' else 'Senate',
                'className': 'assembly' if row['chamber'] == 'Assembly' else 'senate'  # Assign class -- corresponds to color coding from css file
            })           
        
    # If filtering by event type, not bill
    elif not bill_filter_active and selected_types:

        # Add legislative events if selected
        if "Legislative" in selected_types:
          for _, row in leg_events.iterrows():
              calendar_events.append({
                      'title': row.get('title', 'Legislative Event'), # Default title if missing
                      'start': row['start'],
                      'end': row['end'],
                      'allDay': 'true' if row['allDay'] else 'false', # All legislative events are all-day
                      'type': 'Legislative',
                      'className': event_classes.get('Legislative', '') # Assign class -- corresponds to color coding from css file
                  })
              
        # Add Assembly bill events if selected
        if "Assembly" in selected_types:
            assembly_events = bill_events[bill_events['chamber'] == 'Assembly']
            for _, row in assembly_events.iterrows():
                calendar_events.append({
                    'title': f"{row['bill_number']} - {row['event_text']}",
                    'start': row['bill_event'],
                    'end': row['bill_event'],
                    'allDay': 'true' if row['allDay'] else 'false', #  Making bill events all day for now until we can add specific event times
                    'type': 'Assembly',
                    'className': event_classes.get('Assembly', '') # Assign class -- corresponds to color coding from css file
                })

        # Add Senate bill events if selected
        if "Senate" in selected_types:
            senate_events = bill_events[bill_events['chamber'] == 'Senate']
            for _, row in senate_events.iterrows():
                calendar_events.append({
                    'title': f"{row['bill_number']} - {row['event_text']}",
                    'start': row['bill_event'],
                    'end': row['bill_event'],
                    'allDay': 'true' if row['allDay'] else 'false', #  Making bill events all day for now until we can add specific event times
                    'type': 'Senate',
                    'className': event_classes.get('Senate', '') # Assign class -- corresponds to color coding from css file
                })
    
    return calendar_events

    
# Get filtered events
calendar_events = filter_events(selected_types, selected_bills_for_calendar, bill_filter_active)

# Display a count of filtered events (optional, for debugging)
st.sidebar.markdown(f"**Number of events shown**: {len(calendar_events)}")

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


# Render the calendar with a key that depends on the selected filters
# This ensures the calendar re-renders when filters change
calendar_key = f"calendar_{'-'.join(sorted(selected_types))}"

# Render the calendar
calendar = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css,
    key=calendar_key, # Assign unique widget key to prevent state loss
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