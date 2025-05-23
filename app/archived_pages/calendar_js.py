#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar Page
Created on May 6, 2025
@author: danyasherbini

This page of the app features a calendar of legislative deadlines and/or events, built with
injected FullCalendar javascript.

"""

import pandas as pd
import streamlit as st
from db.query import query_table
from db.query import get_my_dashboard_bills
from streamlit.components.v1 import html
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import pytz

# Show the page title and description
# st.set_page_config(page_title='Legislation Tracker', layout='wide') # can add page_icon argument
st.title('Calendar')
st.markdown(
    '''
    This calendar displays overall legislative events and deadlines, as well as bill-specific events for the current session. Use the filters on the left to search for specific events.

    **Important notes:**
    - Events take place in Pacific Time but are displayed in your local time zone.
    - Some events have no available time information and may be marked as "all-day" events.
    - Events with a :pencil2: icon have had their location or time changed since the tool was last updated.
    - Events with a :warning: icon have had their date updated since the tool was last updated.
    '''
)
st.markdown(" ")
st.markdown(" ")

############################ INITIALIZE SESSION STATE VARS #############################

# Access user info
user_email = st.session_state['user_email']

# Initialize session state for dashboard bills
if 'dashboard_bills' not in st.session_state or st.session_state.dashboard_bills is None:
    st.session_state.selected_bills = pd.DataFrame()  # Initialize as empty DataFrame

# Fetch the user's saved bills from the database
db_bills = get_my_dashboard_bills(user_email)

# Update session state with user's dashboard bills
st.session_state.dashboard_bills = db_bills

####################################### LOAD DATA ###################################

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
    bills = query_table('public', 'processed_bills_from_snapshot_2025_2026') # Get bill info from processed_bills table
    events = query_table('ca_dev', 'bill_schedule') # Get bill events from bill_schedule table

    # Subset columns we want from each table
    bills = bills[['openstates_bill_id', 'bill_number', 'bill_name', 'status', 'date_introduced']]
    events = events[['openstates_bill_id', 'chamber_id', 'event_date', 'event_text', 'agenda_order', 'event_time',
                           'event_location', 'event_room', 'revised', 'event_status']]
    

    bill_events = pd.merge(bills, events, how='outer', on='openstates_bill_id') # Merge the two tables on openstates_bill_id
    #bill_events = bill_events[['bill_number','bill_name','status','date_introduced','chamber','event_date','event_text','agenda_order','event_time','event_location','revised','event_status']] # Subset only these columns (for now)
    
    # Drop certain rows
    bill_events = bill_events.dropna(subset=['event_date']) # Drop rows with empty event_date, if any
    #bill_events = bill_events.dropna(subset=['event_time']) # Drop rows with empty event_time, for now
    #bill_events = bill_events[~bill_events['event_time'].str.startswith('Upon')]
    
    # Format event_date as date string without time for display purposes
    bill_events['event_date'] = pd.to_datetime(bill_events['event_date']).dt.strftime('%Y-%m-%d') # event date as just a date (no timestamp)

    # Add column for allDay    
    # Using regex to check if any digit exists in the event_time string. If they do, then allDay is false, else true.
    import re
    bill_events['allDay'] = [False if re.search(r'\d', str(x)) else True for x in bill_events['event_time']]
    
    # Add empty column for resourceId
    bill_events['resourceId'] = ''

    return bill_events

bill_events = load_bill_events()

######################### ADD FILTERS / SIDE BAR ###################################

# Define event classes based on type
event_classes = {
    "Legislative": "legislative",
    "Senate": "senate",
    "Assembly": "assembly",
}

# Also define event flags based on event status and revised status
def get_event_flags(status, revised):
    if status == 'moved' and revised:
        return 'event-moved-rev'
    elif status == 'moved':
        return 'event-moved'
    elif status == 'active' and revised:
        return 'event-active-rev'
    else:
        return 'event-active'

# Color-coding for the tags in the event type multi-select box
st.markdown("""
<style>
span[data-baseweb="tag"]:has(span[title="Legislative"]) {
  color: white;
  background-color: #1f77b4;
}

span[data-baseweb="tag"]:has(span[title="Senate"]) {
  color: white;
  background-color: #ff7f0e;
}

span[data-baseweb="tag"]:has(span[title="Assembly"]) {
  color: white;
  background-color: #2ca02c;
}
</style>
""", unsafe_allow_html=True)


# Get unique bill numbers for the bill filter -- these are the bills that have events
unique_bills = sorted(bill_events['bill_number'].unique())

with st.sidebar.container():
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
        if 'authenticated' not in st.session_state:
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
        st.sidebar.markdown("### Filter by Event Type")
        st.sidebar.info("Event type filter is disabled when specific bills are selected.")


################# PROCESS CALENDAR RESOURCES (i.e. location, room, agenda order, etc.) ###############

def convert_datetime(event_date: str, event_time: str, add_hours: int = 0) -> str | None:
    """
    Combines a date and time string in US Pacific Time and returns ISO 8601 UTC datetime string.
    Optionally adds hours to the converted time.
    
    Args:
        event_date (str): 'YYYY-MM-DD'
        event_time (str): 'h a.m./p.m.' or 'h:mm a.m./p.m.'
        add_hours (int): number of hours to add to the final UTC time (default is 0)

    Returns:
        str or None: ISO 8601 formatted UTC time string, or None if input is invalid
    """
    if not event_date or not event_time:
        return None

    time_str = event_time.replace('.', '').strip().lower()
    if not time_str:
        return None

    dt_str = f"{event_date} {time_str}"

    try:
        dt_format = "%Y-%m-%d %I:%M %p" if ':' in time_str else "%Y-%m-%d %I %p"
        dt = datetime.strptime(dt_str, dt_format)
    except ValueError:
        return None

    pacific = pytz.timezone("US/Pacific")
    localized_dt = pacific.localize(dt)
    utc_dt = localized_dt.astimezone(pytz.utc)

    # Add hours if requested
    if add_hours != 0:
        utc_dt += timedelta(hours=add_hours)

    return utc_dt.isoformat()


# Process location and room data from bill_events
def create_calendar_resources(bill_events_df):
    # Extract unique locations, rooms, and agenda order
    resources = []
    resource_id = 0  # Counter for generating unique IDs
    
    # Create a dictionary to track unique building/room combinations
    unique_locations = {}
    
    for _, row in bill_events_df.iterrows():
        location = row.get('event_location')
        room = row.get('event_room')
        agenda_order = row.get('agenda_order')
        
        # Skip if location or room is missing
        if pd.isna(location) or not location or pd.isna(room) or not room:
            continue
            
        # Create a unique key for this building/room combination
        key = f"{location}|{room}"
        
        # Add to our tracking dictionary if it's a new combination
        if key not in unique_locations:
            resource_id += 1
            # Generate a unique ID (using letters as in your example)
            id_value = chr(96 + resource_id) if resource_id <= 26 else f"resource_{resource_id}"
            
            unique_locations[key] = {
                "id": id_value,
                "building": location,
                "title": room,
                "order": agenda_order if not pd.isna(agenda_order) else 0
            }
        # If this combination already exists but the current row has an agenda_order and the stored one doesn't
        #elif pd.isna(unique_locations[key].get("order", None)) and not pd.isna(agenda_order):
        #    unique_locations[key]["order"] = agenda_order
    
    # Convert the dictionary to a list
    resources = list(unique_locations.values())
    
    # Sort resources by order
    #resources.sort(key=lambda x: x.get("order", 0))
    
    return resources, unique_locations  # Return both the list and the dictionary for easy lookup

# Generate calendar_resources from bill_events
calendar_resources, resource_lookup = create_calendar_resources(bill_events)

######################### CONVERT DATA ###################################

def build_title(row):
    '''
    Helper function to build the title text for the calendar event blocks.
    Combines emojis, bill number, event text, location, room, and agenda order.
    '''
    # Build emoji prefix (no separator after)
    emojis = []
    if row.get('revised') == True:
        emojis.append("✏️")
    if row.get('event_status') == 'moved':
        emojis.append("⚠️")
    emoji_prefix = ' '.join(emojis)

    # Build the rest of the title
    parts = []

    if row.get('bill_number') and row.get('event_text'):
        parts.append(f"{row['bill_number']} - {row['event_text']}")
    elif row.get('bill_number'):
        parts.append(row['bill_number'])
    elif row.get('event_text'):
        parts.append(row['event_text'])

    if row.get('event_location'):
        parts.append(row['event_location'])

    if row.get('event_room'):
        parts.append(row['event_room'])

    agenda_order = row.get('agenda_order')
    if agenda_order not in (None, '', float('nan')):
        try:
            parts.append(f"Agenda order: {int(agenda_order)}")
        except (ValueError, TypeError):
            pass

    # Combine emoji prefix (if any) with rest of title
    title_body = ' | '.join(parts)
    if emoji_prefix:
        return f"{emoji_prefix} {title_body}"
    else:
        return title_body


def filter_events(selected_types, selected_bills_for_calendar, bill_filter_active):
    '''
    Filters calendar events by bill and event type, and converts data to json format for rendering in streamlit calendar.
    '''
    # Initiate empty list of calendar events
    calendar_events = []
    initial_date = str(datetime.now())  # Default to current date if no events are selected
    
    # If filtering by bills (either dashboard bills or individually selected bills)
    if bill_filter_active:
        
        # Filter the bill_events DataFrame to only include selected bills
        filtered_bill_events = bill_events[bill_events['bill_number'].isin(selected_bills_for_calendar)]

        # If user only selects one bill, then set initial date to that bill's event date in order to jump to the event date on the calendar
        if len(selected_bills_for_calendar) == 1 and len(filtered_bill_events) == 1:
            initial_date = str(pd.to_datetime(filtered_bill_events.iloc[0]['event_date'])) # make sure its a string so its JSON compatible

        # If user selects one bill but there are multiple events for that bill:
        elif len(selected_bills_for_calendar) == 1 and len(filtered_bill_events) > 1:
            active_events = filtered_bill_events[filtered_bill_events['event_status'] == 'active']
            
            # Grab the date for the soonest active event
            if not active_events.empty:
                upcoming_event = active_events.loc[pd.to_datetime(active_events['event_date']).idxmin()]
                initial_date = str(pd.to_datetime(upcoming_event['event_date']))
            
            # Else grab the date of the most upcoming event
            else:
                # Pick the soonest event overall, even if inactive or in the past
                soonest_event = filtered_bill_events.loc[pd.to_datetime(filtered_bill_events['event_date']).idxmin()]
                initial_date = str(pd.to_datetime(soonest_event['event_date']))
        
        # Add each filtered bill event to the calendar event list 
        for _, row in filtered_bill_events.iterrows():

            # For events with a specific time, parse the event_time string to time object (combined date and time)
            start_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time'])))
            end_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time']), add_hours=1))

            event_status = get_event_flags(row['event_status'], row['revised'])
            event_class = 'assembly' if row['chamber_id'] == 1 else 'senate'
            
            # Convert to JSON
            calendar_events.append({
                # Add key info to title -- this will be text displayed on the calendar event blocks
                'title': build_title(row),
                'start': start_time if not row['allDay'] else row['event_date'], 
                'end': end_time if not row['allDay'] else row['event_date'],  
                #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
                'type': 'Assembly' if row['chamber_id'] == 1 else 'Senate',
                'className': f"{event_class} {event_status}",  # Assign class -- corresponds to color coding from css file
                'billNumber': row['bill_number'],
                'billName': row['bill_name'],
                'eventText': row['event_text'],
                'eventTime': row['event_time']

            })          
        
    # If filtering by event type, not bill
    elif not bill_filter_active and selected_types:

        # Add legislative events if selected
        if "Legislative" in selected_types:
          for _, row in leg_events.iterrows():

            calendar_events.append({
                'title': row.get('title', 'Legislative Event'), # Default title if missing
                'start': row['start'], # this is the name of the column in the leg events csv file
                'end': row['end'],  # this is the namer of the column in the leg events csv file
                #'allDay': bool(row['allDay']), # All legislative events are all-day, which is already hardcoded in the csv file
                'type': 'Legislative',
                'className': f"{event_classes.get('Legislative', '')} event-active", # Assign class -- corresponds to color coding from css file
                'billNumber': 'N/A',
                'billName': 'N/A',
                'eventText': 'N/A',
                'eventTime': 'N/A'

            })
              
        # Add Assembly bill events if selected
        if "Assembly" in selected_types:
            assembly_events = bill_events[bill_events['chamber_id'] == 1]
            for _, row in assembly_events.iterrows():

                # For events with a specific time, parse the event_time string to time object (combined date and time)
                start_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time'])))
                end_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time']), add_hours=1))

                event_status = get_event_flags(row['event_status'], row['revised'])
                event_class = 'assembly' if row['chamber_id'] == 1 else 'senate'
            
                calendar_events.append({
                    'title': build_title(row),                 
                    'start': start_time if not row['allDay'] else row['event_date'], 
                    'end': end_time if not row['allDay'] else row['event_date'],  
                    #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
                    'type': 'Assembly',
                    'className': f"{event_class} {event_status}",  # Assign class -- corresponds to color coding from css file
                    'billNumber': row['bill_number'],
                    'billName': row['bill_name'],
                    'eventText': row['event_text'],
                    'eventTime': row['event_time']

                })

        # Add Senate bill events if selected
        if "Senate" in selected_types:
            senate_events = bill_events[bill_events['chamber_id'] == 2]
            for _, row in senate_events.iterrows():

                # For events with a specific time, parse the event_time string to time object (combined date and time)
                start_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time'])))
                end_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time']), add_hours=1))

                event_status = get_event_flags(row['event_status'], row['revised'])
                event_class = 'assembly' if row['chamber_id'] == 1 else 'senate'
                
                calendar_events.append({
                    'title': build_title(row),                           
                    'start': start_time if not row['allDay'] else row['event_date'], 
                    'end': end_time if not row['allDay'] else row['event_date'],  
                    #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
                    'type': 'Senate',
                    'className': f"{event_class} {event_status}",  # Assign class -- corresponds to color coding from css file
                    'billNumber': row['bill_number'],
                    'billName': row['bill_name'],
                    'eventText': row['event_text'],
                    'eventTime': row['event_time']
                })
    
    return calendar_events, initial_date
    
# Get filtered events
calendar_events, initial_date = filter_events(selected_types, selected_bills_for_calendar, bill_filter_active)

# Display a count of filtered events (optional, for debugging)
st.sidebar.markdown(f"**Total number of events**: {len(calendar_events)}")

################################## CSS ###################################

# Load external CSS file
def load_css(file_path):
    with open(file_path, "r") as f:
        return f"<style>{f.read()}</style>"

# Read the CSS file
custom_css = load_css("./styles/calendar.css")

# For debugging
#st.write(calendar_events[80]) 


################## DOWNLOAD .ICS FILE ##########################

from ics import Calendar, Event
from datetime import datetime

def create_ics_file(events):
    cal = Calendar()

    for event_data in events:
        event = Event()  # Create a new event
        event.name = f"{event_data['billNumber']} - {event_data['eventText']}"  # Set the event title
        
        # Build the description with your specified format
        description = f"Bill Name: {event_data.get('billName', 'No name provided')}\n"
        description += f"Type: {event_data.get('type', 'Unknown')}\n"
        description += f"Event Details: {event_data.get('title', 'No details provided')}\n"
        
        # Format the date range for the description (check if there's an 'end' date)
        start_date = event_data.get('start', 'Unknown Start Date')
        end_date = event_data.get('end', None)

        # Set the description
        event.description = description

        # Logic for all day events
        if event_data['eventTime'] == 'N/A' or event_data['eventTime'] == '' or "adjourn" in event_data['eventTime']:
            event.begin = pd.to_datetime(start_date).to_pydatetime()
            event.end = pd.to_datetime(start_date).to_pydatetime()
            event.make_all_day()

        # Logic for non-all-day events
        else:
            try:
                # First convert to string if it's not already
                start_str = str(event_data["start"]) if not isinstance(event_data["start"], str) else event_data["start"]
                
                # Check if the date has a time component (contains 'T')
                if 'T' in start_str:
                    # Parse ISO format datetime string (e.g., "2025-01-01T09:30:00")
                    event.begin = pd.to_datetime(start_str).to_pydatetime()
                else:
                    # No time component, just a date
                    event.begin = pd.to_datetime(start_str).to_pydatetime()
                
                # Handle end date/time similarly
                if end_date:
                    end_str = str(end_date) if not isinstance(end_date, str) else end_date
                    event.end = pd.to_datetime(end_str).to_pydatetime()
                else:
                    # If no specific end time, set end to start + 2 hours
                    event.end = event.begin + pd.Timedelta(hours=2)
            except Exception as e:
                # Log error and skip this event if there's a problem
                print(f"Error processing event: {e}")
                continue

        cal.events.add(event)  # Add the event to the calendar
    
    return str(cal)  # Return the .ics content as a string

ics_content = create_ics_file(calendar_events)

# Create a two-column layout to position download button on upper right hand corner of page
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("")

with col2:
    # Make the button
    st.download_button(
        label="📅 Download Events",
        data=ics_content,
        file_name="events.ics",
        mime="text/calendar",
        use_container_width=True
    )

################################## BUILD CALENDAR ###################################
# This streamlit component is built from FullCalendar: https://fullcalendar.io
import json

# Convert calendar_options to JSON, taking care of JavaScript functions
calendar_options = {
    "editable": False,
    "clickable": True,
    "themeSystem": "bootstrap5", # using bootstrap 5 theme
    #"timezone": "Pacific", # can use this if needed but keeping in local time zone for now
    "initialView": "dayGridMonth",
    **({"initialDate": initial_date} if initial_date else {}),
    "dayMaxEventsRows": True,
    "handleWindowResize": True,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay,listMonth",
    },
    "buttonText": {
        "today": "Today",
        "dayGridMonth": "Month",
        "listMonth": "List",
        "timeGridWeek": "Week",
        "timeGridDay": "Day",
    },
    "resources": calendar_resources,
    "resourceAreaWidth": "15%",
    "resourceLabelText": "Locations",
    "resourceOrder": "title",
    "eventOverlap": False,
    "slotEventOverlap": False,
    "eventMaxStack": 3,
    "selectable": True,
    "slotMinTime": "09:00:00",
    "slotMaxTime": "19:00:00",
    "slotDuration": "00:15:00",
    #"snapDuration": "00:30:00",   # Snap to 30 min increments
    "slotHeight": 50,
    "slotLabelFormat": {
        "hour": "numeric",
        "minute": "2-digit",
        "meridiem": "short"
    },
    "events": calendar_events
}

# Extract and temporarily remove the JS function so it can be embedded raw
event_click_js = "function(info) { alert(info.event.title); }"
calendar_options["eventClick"] = None  # Remove temporarily to dump JSON
#calendar_options["height"] = "auto"

# Dump options as JSON (minus function)
options_json = json.dumps(calendar_options, indent=2)
# Insert the function manually
options_json = options_json.replace('"eventClick": null', f'"eventClick": {event_click_js}')

calendar_html = f"""
<!DOCTYPE html>
<html>
<head>
  <!-- Google Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@200;300;400;600&family=Roboto+Slab:wght@200;300;400;600&display=swap" rel="stylesheet">
  
  <!-- FullCalendar CSS -->
  <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css' rel='stylesheet' />

  <!-- Bootstrap 5 CSS and Icons -->
  <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css' rel='stylesheet'>
  <link href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css' rel='stylesheet'>

  <!-- Your Custom CSS -->
  <style>
    {custom_css}
  </style>

  <!-- FullCalendar JS -->
  <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js'></script>
</head>
<body>
  <div id='calendar'></div>
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      var calendarEl = document.getElementById('calendar');
      var calendar = new FullCalendar.Calendar(calendarEl, {options_json});
      calendar.render();
    }});
  </script>
</body>
</html>
"""

# Render calendar
if "calendar_initialized" not in st.session_state:
    st.session_state["calendar_initialized"] = True
    components.html(calendar_html, height=800, width=1000, scrolling=True)
    
#html(calendar_html, height=800, width=1000, scrolling=True)
