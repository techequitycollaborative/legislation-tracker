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
from db.query import query_table
from db.query import get_my_dashboard_bills, get_org_dashboard_bills
from datetime import datetime, timedelta, date
import pytz
import numpy as np

# Show the page title and description
# st.set_page_config(page_title='Legislation Tracker', layout='wide') # can add page_icon argument
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
        - **Letter of support deadlines:** Events with an :envelope: icon are deadlines for letters of support. These deadlines are automatically generated to be 7 days before the committee hearing date; please check committee websites to verify committee-specific rules.
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
if 'dashboard_bills' not in st.session_state or st.session_state.dashboard_bills is None:
    st.session_state.selected_bills = pd.DataFrame()  # Initialize as empty DataFrame

# Fetch the user's saved bills from the database
db_bills = get_my_dashboard_bills(user_email)

# Update session state with user's dashboard bills
st.session_state.dashboard_bills = db_bills

# Initialize session state for org dashboard bills
if 'org_dashboard_bills' not in st.session_state or st.session_state.org_dashboard_bills is None:
    st.session_state.org_dashboard_bills = pd.DataFrame()  # Initialize as empty DataFrame

# Fetch the user's org's saved bills from the database
org_db_bills = get_org_dashboard_bills(org_id)

# Update session state with user's org's dashboard bills
st.session_state.org_dashboard_bills = org_db_bills

# Initialize state for clicked event
if "clicked_event" not in st.session_state:
    st.session_state.clicked_event = None

# Initialize all calendar events in session state
if "calendar_events" not in st.session_state:
    st.session_state.calendar_events = []

####################################### LOAD DATA ###################################

# Load legislative calendar events for 2025-2026 leg session (this is in a CSV file for now)
@st.cache_data
def load_leg_events():
    leg_events = pd.read_csv('./data/20252026_leg_dates.csv')
    return leg_events

leg_events = load_leg_events()

# Load events specific to individual bills
@st.cache_data(ttl=10 * 60 * 60) # Cache for 10 hours
def load_bill_events():
    bills = query_table('public', 'processed_bills_from_snapshot_2025_2026') # Get bill info from processed_bills table
    events = query_table('ca_dev', 'bill_schedule') # Get bill events from bill_schedule table

    # Subset columns we want from each table
    bills = bills[['openstates_bill_id', 'bill_number', 'bill_name', 'status', 'date_introduced']]
    events = events[['openstates_bill_id', 'chamber_id', 'event_date', 'event_text', 'agenda_order', 'event_time',
                           'event_location', 'event_room', 'revised', 'event_status']]
    

    bill_events = pd.merge(bills, events, how='outer', on='openstates_bill_id') # Merge the two tables on openstates_bill_id
    
    # Drop rows with empty event_date, if any
    bill_events = bill_events.dropna(subset=['event_date']) 
    
    # Format event_date as date string without time for display purposes
    bill_events['event_date'] = pd.to_datetime(bill_events['event_date']).dt.strftime('%Y-%m-%d') # event date as just a date (no timestamp)

    # Add column for allDay events and categorize based on values in event_time column
    def all_day(x):

        # Control for events that don't have an actual time (e.g. "Upon adjournment")
        def contains_keywords(text):
            text = str(text).lower()
            keywords = ['upon', 'adjournment', 'after', 'before', 'session']
            return any(keyword in text for keyword in keywords)
        
        # Define all day event as any event that has no time or has a time that contains certain keywords
        def is_empty(x):
            if pd.isna(x) or x == '' or x == 'N/A':
                return True
            else:
                return False
        
        # Check if the event_time is empty or contains keywords
        if is_empty(x) or contains_keywords(x):
            return True
        else:
            return False

    bill_events['allDay'] = [all_day(x) for x in bill_events['event_time']]

    # Add empty column for resourceId
    bill_events['resourceId'] = ''

    # Add letter of support deadline column -- make all letter of support deadlines 7 days before the event date for now
    bill_events['letter_deadline'] = [(pd.to_datetime(x) - timedelta(days=7)) if pd.notna(x) else None for x in bill_events['event_date']]
    bill_events['letter_deadline'] = bill_events['letter_deadline'].dt.strftime('%Y-%m-%d') # Format as date string without time

    # Set letter_deadline to None if event_text contains certain keywords (these events are not committee events and thus don't have letter deadlines)
    search_words = ['Calendar', 'File', 'Concurrence', 'Reading']  # Define your list of search words
    pattern = '|'.join(r'\b' + word + r'\b' for word in search_words)
    bill_events['letter_deadline'] = np.where(bill_events['event_text'].str.contains(pattern, na=False), None, bill_events['letter_deadline'])

    return bill_events

bill_events = load_bill_events()
#st.write(bill_events.head(5))  # Display the first few rows of the bill events DataFrame for debugging


######################### ADD FILTERS / SIDE BAR ###################################

# Define event classes based on type
event_classes = {
    "Legislative": "legislative",
    "Senate": "senate",
    "Assembly": "assembly",
    "Letter Deadline": "letter-deadline",
}

# Also define event flags based on event status and revised status
def get_event_flags(status, revised):
    '''
    Gets the event status and revised status and returns a class name for the event in order to produce visual flags in the calendar.
    '''
    # Category 1: Revised events
    if status == 'active' and revised == True:
        return 'event-revised'
    
    # Category 2: Moved events
    elif status == 'moved' and revised == False:
        return 'event-moved'
    
    # Category 3: Normal events
    elif status == 'active' and revised == False:
        return 'event-normal'
    else:
        return 'event-normal'
    
# Identify moved events -- THIS NEEDS DEVELOPMENT!
def get_moved_events(bill_events):
    events_copy = bill_events.copy()

    # Create a unique identifier for each event based on openstates_bill_id, chamber_id, and event_text -- DO NOT USE EVENT DATE BC THIS WILL BE DIFF FOR THE MOVED EVENT PAIR
    unique_event_id = events_copy['openstates_bill_id'] + '_' + str(events_copy['chamber_id']) + '_' + events_copy['event_text']
    events_copy['unique_event_id'] = unique_event_id
 
    # Find all duplicated unique_event_ids (must appear exactly twice)
    dupe_groups = events_copy.groupby('unique_event_id').filter(lambda x: len(x) == 2 and x['event_status'].nunique() > 1)

    # Get only the rows with status == 'active' -- this is the updated event
    moved_to_active_events = dupe_groups[dupe_groups['event_status'] == 'active']

    # Check assumption that events appear exactly twice, i.e. that events are not moved more than once
    assert all(dupe_groups['unique_event_id'].value_counts() == 2), "Some IDs don't appear exactly twice!"

    # Return only the 'active' event in the pair (i.e., the event it was moved to)
    moved_to_active_events = dupe_groups[dupe_groups['event_status'] == 'active']

    return moved_to_active_events
    
# Define letter of support class
def get_letter_deadline_class(letter_deadline):
    if letter_deadline != 'N/A':
        return 'letter-deadline'
    else:
        return ''

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
    st.sidebar.markdown("### Filter by Bill")

    # Initialize variables to handle both filtering scenarios
    selected_types = []
    bill_filter_active = False
    selected_bills_for_calendar = []

    # Option to show only bills from ORG Dashboard
    show_org_dashboard_bills = st.sidebar.checkbox(f"Only show events for bills from {org_name}'s Dashboard")

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
    show_dashboard_bills = st.sidebar.checkbox("Only show events for bills from My Dashboard")

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


# Process location and room data from bill_events -- NOT IN ACTIVE USE RIGHT NOW
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
            # Generate a unique ID
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

    #if row.get('event_status') == 'moved':
    #    emojis.append("⚠️")
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
    

from datetime import datetime, timedelta

def safe(val):
    ''' Helper function to safely convert values to string or return None if NaN.'''
    if pd.isna(val):
        return None
    return val


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
                'billNumber': safe(row['bill_number']),
                'billName': safe(row['bill_name']),
                'eventText': safe(row['event_text']),
                'eventTime': safe(row['event_time']),
                'status': safe(row['status']),
                'date_introduced': str(safe(row['date_introduced'])),
                'letter_deadline': safe(row['letter_deadline']),
                'openstates_bill_id': safe(row.get('openstates_bill_id', 'N/A')),
            })

        # Add letter of support deadline events for all bill events
        for _, row in filtered_bill_events.iterrows():

            # If the letter deadline is not None, create a letter deadline event
            if row['letter_deadline'] is not None:

                # Get letter deadline class -- for css color coding
                #letter_deadline_class = get_letter_deadline_class(row['letter_deadline'])
                
                # Convert to JSON
                calendar_events.append({
                    # Add key info to title -- this will be text displayed on the calendar event blocks
                    'title': f"✉️ LETTER OF SUPPORT DUE! {row['bill_number']} - {row['event_text']}",
                    'start': row['letter_deadline'], 
                    'end': row['letter_deadline'],
                    #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
                    'type': 'Letter Deadline',
                    'className': "letter-deadline",  # Assign class -- corresponds to color coding from css file
                    'billNumber': safe(row['bill_number']),
                    'billName': safe(row['bill_name']),
                    'eventText': safe(row['event_text']),
                    'eventTime': safe(row['event_time']),
                    'status': safe(row['status']),
                    'date_introduced': str(safe(row['date_introduced'])),
                    'letter_deadline': safe(row['letter_deadline']),
                    'openstates_bill_id': safe(row.get('openstates_bill_id', 'N/A')),
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
                'className': f"{event_classes.get('Legislative', '')} event-normal", # Assign class -- corresponds to color coding from css file            
                'billNumber': 'N/A',
                'billName': 'N/A',
                'eventText': 'N/A',
                'eventTime': 'N/A',
                'status': 'N/A', #this is bill status, not event status
                'date_introduced': 'N/A',
                'letter_deadline': 'N/A',
                'openstates_bill_id': 'N/A',
            })
        
        # Add letter of support deadline events if selected
        if "Letter Deadline" in selected_types:
            letter_events = bill_events[bill_events['letter_deadline'].notnull()]
            
            for _, row in letter_events.iterrows():

                    # Get letter deadline class -- for css color coding
                    #letter_deadline_class = get_letter_deadline_class(row['letter_deadline'])
                    
                    # Convert to JSON
                    calendar_events.append({
                        # Add key info to title -- this will be text displayed on the calendar event blocks
                        'title': f"✉️ LETTER OF SUPPORT DUE! {row['bill_number']} - {row['event_text']}",
                        'start': row['letter_deadline'],
                        'end': row['letter_deadline'],
                        #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
                        'type': 'Letter Deadline',
                        'className': "letter-deadline",  # Assign class -- corresponds to color coding from css file
                        'billNumber': safe(row['bill_number']),
                        'billName': safe(row['bill_name']),
                        'eventText': safe(row['event_text']),
                        'eventTime': safe(row['event_time']),
                        'status': safe(row['status']),
                        'date_introduced': str(safe(row['date_introduced'])),
                        'letter_deadline': safe(row['letter_deadline']),
                        'openstates_bill_id': safe(row.get('openstates_bill_id', 'N/A')),

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
                    'billNumber': safe(row['bill_number']),
                    'billName': safe(row['bill_name']),
                    'eventText': safe(row['event_text']),
                    'eventTime': safe(row['event_time']),
                    'status': safe(row['status']),
                    'date_introduced': str(safe(row['date_introduced'])),
                    'letter_deadline': safe(row['letter_deadline']),
                    'openstates_bill_id': safe(row.get('openstates_bill_id', 'N/A')),
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
                    'billNumber': safe(row['bill_number']),
                    'billName': safe(row['bill_name']),
                    'eventText': safe(row['event_text']),
                    'eventTime': safe(row['event_time']),
                    'status': safe(row['status']),
                    'date_introduced': str(safe(row['date_introduced'])),
                    'letter_deadline': safe(row['letter_deadline']),
                    'openstates_bill_id': safe(row.get('openstates_bill_id', 'N/A')),

                })
    
    return calendar_events, initial_date
    
# Get filtered events
calendar_events, initial_date = filter_events(selected_types, selected_bills_for_calendar, bill_filter_active)

# Update session state with filtered events
st.session_state.calendar_events = calendar_events

# Display a count of filtered events (optional, for debugging)
#st.sidebar.markdown(f"**Total number of events**: {len(calendar_events)}")
#st.write(st.session_state.calendar_events)  # Display the filtered events for debugging 


################################## CREATE CALENDAR EVENTS ###################################

# WORKING ON REFACTORING THESE FUNCTIONS IN ORDER TO REPLACE THE FILTER-EVENTS FUNCTION ABOVE! 

def create_legislative_events(leg_events):
    '''
    Creates legislative events for the calendar.
    '''
    # Initiate empty list of calendar events
    calendar_events = []
    
    # Build legislative events
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
            'eventTime': 'N/A',
            'status': 'N/A', #this is bill status, not event status
            'date_introduced': 'N/A',
            'letter_deadline': 'N/A',
        })

        return calendar_events

def create_bill_events(bill_events, include_letter_deadlines=True):
    '''
    Creates Senate and Assembly events for the calendar based on selected event types.

    Optionally includes letter of support deadlines for each event.
    '''   
    # Initiate empty list of calendar events
    calendar_events = []
        
    # Build Assembly events
    for _, row in bill_events.iterrows():

        # For events with a specific time, parse the event_time string to time object (combined date and time)
        start_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time'])))
        end_time = str(convert_datetime(event_date=str(row['event_date']), event_time=str(row['event_time']), add_hours=1))

        # Define event status and event class
        event_status = get_event_flags(row['event_status'], row['revised'])
        event_class = 'assembly' if row['chamber_id'] == 1 else 'senate'
                
        base_event = {
            'title': build_title(row),                 
            'start': start_time if not row['allDay'] else row['event_date'], 
            'end': end_time if not row['allDay'] else row['event_date'],
            #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
            'type': 'Assembly',
            'className': f"{event_class} {event_status}",  # Assign class -- corresponds to color coding from css file
            'billNumber': safe(row['bill_number']),
            'billName': safe(row['bill_name']),
            'eventText': safe(row['event_text']),
            'eventTime': safe(row['event_time']),
            'status': safe(row['status']),
            'date_introduced': str(safe(row['date_introduced'])),
            'letter_deadline': safe(row['letter_deadline']),
            'openstates_bill_id': safe(row.get('openstates_bill_id', 'N/A')),
        }

        calendar_events.append(base_event)

        # Add letter of support deadline events for applicable events if flag is set to True
        if include_letter_deadlines:
            for _, row in bill_events.iterrows():

                # If the letter deadline is not None, create a letter deadline event
                if row['letter_deadline'] is not None:
                    
                    letter_deadline_event = {
                        'title': f"✉️ LETTER OF SUPPORT DUE! {row['bill_number']} - {row['event_text']}",
                        'start': row['letter_deadline'],
                        'end': row['letter_deadline'],
                        #'allDay': bool(row['allDay']), #  Turned off bc events now have specific times
                        'type': 'Assembly',
                        'className': "letter-deadline",  # Assign class -- corresponds to color coding from css file
                        'billNumber': safe(row['bill_number']),
                        'billName': safe(row['bill_name']),
                        'eventText': safe(row['event_text']),
                        'eventTime': safe(row['event_time']),
                        'status': safe(row['status']),
                        'date_introduced': str(safe(row['date_introduced'])),
                        'letter_deadline': safe(row['letter_deadline']),
                        'openstates_bill_id': safe(row.get('openstates_bill_id', 'N/A')),
                    }
                    
                    calendar_events.append(letter_deadline_event)
        
    return calendar_events


@st.cache_data
def create_all_events():
    """
    Creates all events for the calendar by combining bill events and legislative events.
    """
    # Create bill events
    bill_events_list = create_bill_events(bill_events, include_letter_deadlines=True)

    # Create legislative events
    legislative_events_list = create_legislative_events(leg_events)

    # Combine both lists
    all_events = bill_events_list + legislative_events_list

    return all_events


def filter_calendar_events(selected_types, selected_bills_for_calendar, bill_filter_active):
    """
    Filters events for the calendar based on selected bills and/or event types.
    Returns calendar events (as JSON) and an initial date to center the calendar on.
    """
    calendar_events = []
    initial_date = str(datetime.now())  # Default

    # Determine bill-level filtering
    filtered_bill_events = bill_events.copy() # copy bill events df

    # If bill-specific filter is active, then filter the df for the selected bills
    if bill_filter_active:
        filtered_bill_events = filtered_bill_events[
            filtered_bill_events['bill_number'].isin(selected_bills_for_calendar)]

        # Determine initial date

        # If user only selects one bill, then:
        if len(selected_bills_for_calendar) == 1 and not filtered_bill_events.empty:
            active_events = filtered_bill_events[filtered_bill_events['event_status'] == 'active'] # subset to active events
            if not active_events.empty: # if there are active events, then:
                initial_date = str(pd.to_datetime(active_events['event_date'].min())) # grab the soonest active event
            else:
                initial_date = str(pd.to_datetime(filtered_bill_events['event_date'].min())) # otherwise grab the soonest event overall

    # Further filter by event type (Assembly/Senate) if applicable
    # If the user has selected specific event types, filter the bill events DataFrame accordingly
    if selected_types:
        chamber_filter = []
        if "Assembly" in selected_types:
            chamber_filter.append(1)
        if "Senate" in selected_types:
            chamber_filter.append(2)

        if chamber_filter:
            filtered_bill_events = filtered_bill_events[
                filtered_bill_events['chamber_id'].isin(chamber_filter)
            ]

    # Add bill-related events
    calendar_events += create_bill_events(filtered_bill_events, include_letter_deadlines=True)

    # Add legislative events (these are not bill-specific)
    if not bill_filter_active and "Legislative" in selected_types:
        calendar_events += create_legislative_events(leg_events)

    else:
        calendar_events = create_bill_events(filtered_bill_events, include_letter_deadlines=True)

    return calendar_events, initial_date


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

def create_ics_file(events):
    cal = Calendar()

    for event_data in events:
        event = Event()  # Create a new event
        event.name = f"{event_data['billNumber']} - {event_data['eventText']}"  # Set the event title
        
        # Build the description with your specified format
        description = f"Bill Name: {event_data.get('billName', 'No name provided')}\n"
        #description += f"Type: {event_data.get('type', 'Unknown')}\n" -- turned off for now bc it was confusing when bills went to opposite house
        description += f"Event Details: {event_data.get('title', 'No details provided')}\n"
        
        # Format the date range for the description (check if there's an 'end' date)
        start_date = event_data.get('start', 'Unknown Start Date')
        end_date = event_data.get('end', None)

        # Set the description
        event.description = description

        # Logic for all day events
        if event_data['eventTime'] == 'N/A' or event_data['eventTime'] == '' or "adjourn" in event_data['eventTime']:
            try:
                event.begin = pd.to_datetime(start_date).to_pydatetime()
                event.end = pd.to_datetime(start_date).to_pydatetime()
                event.make_all_day()
            except Exception as e:
                print(f"Start date is 'N/A', null, or None -- skipping: {e}")
                continue

            # Handle letter deadline events
            if "LETTER" in event_data['title']:
                try:
                    # Make all day
                    event.begin = pd.to_datetime(start_date).to_pydatetime()
                    event.end = pd.to_datetime(start_date).to_pydatetime()
                    event.make_all_day()
                    # Update the title
                    event.name = f"✉️ LETTER OF SUPPORT DUE - {event_data['billNumber']} - {event_data['eventText']}"
                except Exception as e:
                    # If start = N/A then skip
                    print(f"Start date is 'N/A', null, or None -- assuming this is not a valid letter of support and skipping: {e}")
                    continue

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
        label="📅 Download Events (.ics)",
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

    # Resources
    "resources": calendar_resources,  # Your resource list
    "resourceAreaWidth": "15%",
    "resourceLabelText": "Locations",
    "resourceOrder": "title",  # Sort resources by room title
    
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
