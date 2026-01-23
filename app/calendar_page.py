#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar Page
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
from db.query import get_my_dashboard_bills, get_org_dashboard_bills
from utils.calendar_utils import load_leg_events, load_bill_events, filter_events, load_css, create_ics_file
from utils.profiling import profile, track_rerun
# Show the page title and description
# st.set_page_config(page_title='Legislation Tracker', layout='wide') # can add page_icon argument
track_rerun("Calendar")
st.title('📅 Calendar')

with st.expander("About this page", icon="ℹ️", expanded=False):
    st.markdown(
        '''
        This calendar displays overall legislative events and deadlines, as well as bill-specific events for the current session. Use the filters on the left in the sidebar to search for specific events.
        
        Important notes about the calendar:
        - **Time zone:** Events take place in Pacific Time but are displayed in your local time zone.
        - **All-day events:** Some events have no available time information and may be marked as "all-day" events.
        - **Updated events:** Events with a :pencil2: icon have had their time, location, room, or agenda order changed since the tool was last updated.
        - **Moved/postponed events:** Crossed out events have been moved or postponed to a different date. For bill-specific events, please note that the hearing itself may still be scheduled, but that particular bill may have been removed from the agenda. If available, the new event date is included as a separate event in the calendar.
        - **Letter deadlines:** Events with an :envelope: icon are deadlines for letters. These deadlines are automatically generated to be 7 days before the committee hearing date; please check committee websites to verify committee-specific rules.
        - **View:** For best experience, view calendar in full screen mode.
        '''
    )

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")

############################ INITIALIZE SESSION STATE VARS #############################
# Access user info
user_email = st.session_state['user_email']
org_id = st.session_state['org_id']
org_name = st.session_state['org_name']

# Initialize session state for dashboard bills
if 'dashboard_bills' not in st.session_state or not len(st.session_state.dashboard_bills):
    st.session_state.selected_bills = get_my_dashboard_bills(user_email)

# Initialize session state for org dashboard bills
if 'org_dashboard_bills' not in st.session_state or st.session_state.org_dashboard_bills is None:
    st.session_state.org_dashboard_bills = get_org_dashboard_bills(org_id)

# Initialize state for clicked event
if "clicked_event" not in st.session_state:
    st.session_state.clicked_event = None

# Initialize all calendar events in session state
if "calendar_events" not in st.session_state:
    st.session_state.calendar_events = []

####################################### LOAD DATA ###################################

# Load legislative calendar events for 2025-2026 leg session (this is in a CSV file for now)
leg_events = load_leg_events()

# Load events specific to individual bills
bill_events = load_bill_events()
#st.write(bill_events.head(5))  # Display the first few rows of the bill events DataFrame for debugging

# Load css
custom_css = load_css('styles/calendar.css')

######################### ADD FILTERS / SIDE BAR ###################################

# Define event classes based on type
event_classes = {
    "Legislative": "legislative",
    "Senate": "senate",
    "Assembly": "assembly",
    "Letter Deadline": "letter-deadline",
}

# Color-coding for the tags in the event type multi-select box
st.markdown("""
<style>
span[data-baseweb="tag"]:has(span[title="Legislative"]) {
  color: white;
  background-color: #0041d9;
}

span[data-baseweb="tag"]:has(span[title="Senate"]) {
  color: white;
  background-color: #712f39;
}

span[data-baseweb="tag"]:has(span[title="Assembly"]) {
  color: white;
  background-color: #00495e;
}
            
span[data-baseweb="tag"]:has(span[title="Letter Deadline"]) {
  color: white;
  background-color: #edcbab;
}
</style>
""", unsafe_allow_html=True)


# Get unique bill numbers for the bill filter -- these are the bills that have events
bill_events['bill_number'] = bill_events['bill_number'].astype(str)
unique_bills = sorted(bill_events['bill_number'].unique())

with st.sidebar.container():
    # Add bill filter with search functionality
    st.sidebar.markdown("### Filter for Bills in")

    # Initialize variables to handle both filtering scenarios
    selected_types = []
    bill_filter_active = False
    selected_bills_for_calendar = []

    # Option to show only bills from ORG Dashboard
    show_org_dashboard_bills = st.sidebar.checkbox(f"{org_name}'s Dashboard")

    # Determine eligibility for dashboard bill checkbox
    if show_org_dashboard_bills:
        if 'authenticated' not in st.session_state:
            st.sidebar.warning("User not authenticated. Login to see org dashboard bill events.")
            selected_bills_for_calendar = []
            bill_filter_active = False
        elif 'org_dashboard_bills' not in st.session_state or st.session_state.org_dashboard_bills is None or len(st.session_state.org_dashboard_bills) == 0:
            st.sidebar.info("No bills saved to the org dashboard. Go to the Bills page to add bills to your organization's dashboard.")
            selected_bills_for_calendar = []
            bill_filter_active = False
        else:
            # Use the bills directly from session state
            org_dashboard_bills = st.session_state.org_dashboard_bills['bill_number'].unique().tolist()
            selected_bills_for_calendar = org_dashboard_bills
            bill_filter_active = True

    # Option to select from MY dashboard bills
    show_dashboard_bills = st.sidebar.checkbox("My Dashboard")

    # Determine eligibility for dashboard bill checkbox
    if show_dashboard_bills:
        if 'authenticated' not in st.session_state:
            st.sidebar.warning("User not authenticated. Login to see your dashboard bill events.")
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
    elif not show_dashboard_bills and not show_org_dashboard_bills:
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
        st.sidebar.markdown("### Filter by Event Type")
        st.sidebar.info("Event type filter is disabled when specific bills are selected.")
    
# Get filtered events
calendar_events, initial_date = filter_events(bill_events, leg_events, selected_types, selected_bills_for_calendar, bill_filter_active)

# Update session state with filtered events
st.session_state.calendar_events = calendar_events

# Display a count of filtered events (optional, for debugging)
#st.sidebar.markdown(f"**Total number of events**: {len(calendar_events)}")
#st.write(st.session_state.calendar_events)  # Display the filtered events for debugging

################################## DOWNLOAD ICS FILE ###################################
ics_content = create_ics_file(calendar_events)

# Create a two-column layout to position download button on upper right hand corner of page
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("")

with col2:
    # Make the button
    st.download_button(
        label="📅 Download Events (.ics)",
        data=ics_content,
        file_name="events.ics",
        mime="text/calendar",
        width='stretch'
    )

################################## BUILD CALENDAR ###################################
# This streamlit component is built from FullCalendar: https://fullcalendar.io

# Calendar options
calendar_options = {
    
    # Basic options
    "selectable": True,  # Allows for clicking an event
    "themeSystem": "bootstrap5",  # Use Bootstrap theme
    "initialView": "dayGridMonth",
    **({"initialDate": initial_date} if initial_date else {}),
    "dayMaxEventsRows": "true",  # Allows for more than one event per day
    "dayMaxEvents": 5,  # Maximum number of ALL DAY events to show per day
    "handleWindowResize": "true",  # Ensures calendar resizes on window resize
    
    # Toolbar
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay,listMonth",
    },
    
    # Customize toolbar button text
    "buttonText": {
        "today": "Today",
        "dayGridMonth": "Month",  # Customize the text for the month view button
        "listMonth": "List",  # Customize the text for the week view button
        "timeGridWeek": "Week",  # Customize the text for the week view button
        "timeGridDay": "Day",  # Customize the text for the list view button
    },
    
    # JavaScript function for event click
    "eventClick": "function(info) { alert('Event: ' + info.event.title); }",
    
    # Options for better handling overlapping timed events
    "eventOverlap": True,  # Don't allow events to overlap
    "slotEventOverlap": False,  # Don't visually overlap events (stack them horizontally instead)
    "eventMaxStack": 1,  # Maximum number of SIDE BY SIDE TIMED events to stack in a time slot
    
    # Time slot options
    #"height": "700px",
    "selectable": "true",
    "slotMinTime": "09:00:00",    # Start at 9am
    "slotMaxTime": "19:00:00",    # End at 7pm
    "slotDuration": "00:15:00",   # 15-minute slots -- making this shorter is a hack to make the event blocks taller
    "slotHeight": 50,  # Make time slots taller (default is 30px)
    #"snapDuration": "00:30:00",   # Snap to 30 min increments
    "slotLabelFormat": {
        "hour": "numeric",
        "minute": "2-digit",
        "meridiem": "short"
    }
    
}

# Render the calendar with a key that depends on the selected filters
# This ensures the calendar re-renders when filters change
calendar_key = f"calendar_{'-'.join(sorted(selected_types))}"

# Render the calendar
calendar_widget = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css,
    callbacks=["eventClick"],
    key=calendar_key, # Assign unique widget key to prevent state loss
    )
