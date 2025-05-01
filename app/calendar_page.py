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
from db.query import get_my_dashboard_bills

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

from datetime import datetime, timedelta
import pytz

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


st.write(convert_datetime("2025-01-01", "9 a.m."))  # Example usage


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

            # For events with a specific time, parse the event_time string to time object (combined date and time)
            start_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time'])))
            end_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time']), add_hours=1))
            
            # Convert to JSON
            calendar_events.append({
                # Add key info to title -- this will be text displayed on the calendar event blocks
                'title': f"""
                            {row['bill_number']} - {row['event_text']} | 
                            {row['event_location']} | 
                            {row['event_room']} |
                            Agenda order: {row['agenda_order']:.0f}
                        """,     
                'start': start_time if not row['allDay'] else row['event_date'], 
                'end': end_time if not row['allDay'] else row['event_date'],  
                #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
                'type': 'Assembly' if row['chamber_id'] == 1 else 'Senate',
                'className': 'assembly' if row['chamber_id'] == 1 else 'senate',  # Assign class -- corresponds to color coding from css file
            
                # Add extended properties that will be appear in event pop up upon click
                'billName': f"Bill Name: {row['bill_name']}",
                'status': f"Bill latest status: {row['status']}",
                'dateIntroduced': f"Date Introduced: {row['date_introduced']}",
                'eventLocation': f"Event Location: {row['event_location']}",
                'eventRoom': f"Room:{row['event_room']}"
                #'eventStatus': row['event_status'],
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
                'className': event_classes.get('Legislative', ''), # Assign class -- corresponds to color coding from css file
                  })
              
        # Add Assembly bill events if selected
        if "Assembly" in selected_types:
            assembly_events = bill_events[bill_events['chamber_id'] == 1]
            for _, row in assembly_events.iterrows():

                # For events with a specific time, parse the event_time string to time object (combined date and time)
                start_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time'])))
                end_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time']), add_hours=1))
            
                calendar_events.append({
                    'title': f"""
                                {row['bill_number']} - {row['event_text']} | 
                                {row['event_location']} | 
                                {row['event_room']} |
                                Agenda order: {row['agenda_order']:.0f}
                            """,                    
                    'start': start_time if not row['allDay'] else row['event_date'], 
                    'end': end_time if not row['allDay'] else row['event_date'],  
                    #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
                    'type': 'Assembly',
                    'className': event_classes.get('Assembly', ''), # Assign class -- corresponds to color coding from css file
                    # Add extended properties that will be appear in event pop up upon click
                    'billName': f"Bill Name: {row['bill_name']}",
                    'status': f"Bill latest status: {row['status']}",
                    'dateIntroduced': f"Date Introduced: {row['date_introduced']}",
                    'eventLocation': f"Event Location: {row['event_location']}",
                    'eventRoom': f"Room:{row['event_room']}"
                    #'eventStatus': row['event_status'],             
                })

        # Add Senate bill events if selected
        if "Senate" in selected_types:
            senate_events = bill_events[bill_events['chamber_id'] == 2]
            for _, row in senate_events.iterrows():

                # For events with a specific time, parse the event_time string to time object (combined date and time)
                start_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time'])))
                end_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time']), add_hours=1))

                calendar_events.append({
                    'title': f"""
                                {row['bill_number']} - {row['event_text']} | 
                                {row['event_location']} | 
                                {row['event_room']} |
                                Agenda order: {row['agenda_order']:.0f}
                            """,                           
                    'start': start_time if not row['allDay'] else row['event_date'], 
                    'end': end_time if not row['allDay'] else row['event_date'],  
                    #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
                    'type': 'Senate',
                    'className': event_classes.get('Senate', ''), # Assign class -- corresponds to color coding from css file
                    # Add extended properties that will be appear in event pop up upon click
                    'billName': f"Bill Name: {row['bill_name']}",
                    'status': f"Bill latest status: {row['status']}",
                    'dateIntroduced': f"Date Introduced: {row['date_introduced']}",
                    'eventLocation': f"Event Location: {row['event_location']}",
                    'eventRoom': f"Room:{row['event_room']}"
                    #'eventStatus': row['event_status'],
                })
    
    return calendar_events
    
# Get filtered events
calendar_events = filter_events(selected_types, selected_bills_for_calendar, bill_filter_active)

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
        event.name = event_data["title"]  # Set the event title
        
        # Build the description with your specified format
        description = f"Type: {event_data.get('type', 'Unknown')}\n"
        description += f"Event Details: {event_data.get('title', 'No title provided')}\n"
        
        # Format the date range for the description (check if there's an 'end' date)
        start_date = event_data.get('start', 'Unknown Start Date')
        end_date = event_data.get('end', None)

        description += f"Date: {start_date}"
        if end_date and end_date != start_date:  # If the end date exists, add it to the description
            description += f" - {end_date}"

        # Set the description
        event.description = description

        # Check if the event is an all-day event
        if event_data.get("allDay", "false") == "true":
            # Handle all-day events
            try:
                # Convert to datetime and set as all-day
                event.begin = pd.to_datetime(event_data["start"]).to_pydatetime()
                event.make_all_day()
            except Exception as e:
                # Fallback if there's an error
                print(f"Error processing all-day event: {e}")
                continue
        else:
            # Handle non-all-day events
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

# Calendar options
calendar_options = {
    
    # Basic options
    "editable": False,  # Disable editing of events
    "clickable": True,  # Allows for clicking an event
    "themeSystem": "standard",
    "initialView": "timeGridWeek",
    "dayMaxEventsRows": "true",  # Allows for more than one event per day
    "handleWindowResize": "true",  # Ensures calendar resizes on window resize
    
    # Toolbar
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
    },
    
    # Customize toolbar button text
    "buttonText": {
        "today": "Today",
        "dayGridMonth": "Month",  # Customize the text for the month view button
        "listWeek": "List",  # Customize the text for the week view button
        "timeGridWeek": "Week",  # Customize the text for the week view button
        "timeGridDay": "Day",  # Customize the text for the list view button
    },
    
    # JavaScript function for event click
    "eventClick": "function(info) { alert('Event: ' + info.event.title); }",
    
    # Resources
    "resources": calendar_resources,  # Your resource list
    "resourceAreaWidth": "15%",
    "resourceLabelText": "Locations",
    "resourceOrder": "title",  # Sort resources by room title
    
    # Options for better handling overlapping events
    "eventOverlap": True,  # Allow events to overlap
    "slotEventOverlap": False,  # Don't visually overlap events (stacks them instead)
    "eventMaxStack": 3,  # Maximum number of events to stack in a time slot
    
    # Time slot options
    "selectable": "true",
    "slotMinTime": "09:00:00",    # Start at 9am
    "slotMaxTime": "18:00:00",    # End at 6pm
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
calendar = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css,
    key=calendar_key, # Assign unique widget key to prevent state loss
    )


################################################################################################

