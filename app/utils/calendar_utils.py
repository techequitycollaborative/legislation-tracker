#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calendar_utils.py
Created on Nov 27, 2024
@author: danyasherbini

Utility functions for the Calendar page
"""

import pandas as pd
import streamlit as st
from db.query import query_table
from datetime import datetime, timedelta, date
import pytz
import numpy as np
from ics import Calendar, Event
from .profiling import profile
import re

##################################### HELPER FUNCTIONS #############################
# Control for events that don't have an actual time (e.g. "Upon adjournment")
relative_time_keywords = [
    'upon',
    'adjournment',
    'after',
    'before',
    'session'
]
RT_KEYWORDS = re.compile(r'|'.join(r'\b' + word + r'\b' for word in relative_time_keywords))

deadline_event_keywords = ['Calendar', 'File', 'Concurrence', 'Reading']  # Define your list of search words

DE_KEYWORDS = re.compile(r'|'.join(r'\b' + word + r'\b' for word in deadline_event_keywords))

####################################### LOAD DATA ###################################

# Load legislative calendar events for 2025-2026 leg session (this is in a CSV file for now)
@st.cache_data(show_spinner="Loading legislative events...")
def load_leg_events():
    leg_events = pd.read_csv('./data/20262027_leg_dates.csv')
    return leg_events

# Load events specific to individual bills
@profile("Calendar - load bill events")
@st.cache_data(show_spinner="Loading bill events...",ttl=60 * 60 * 6) # Cache bills data and refresh every 6 hours
def load_bill_events():
    bill_events = query_table('app', 'calendar_mv') # Get bill info from processed_bills table

    # Format event_date as date string without time for display purposes
    bill_events['hearing_date'] = pd.to_datetime(bill_events['hearing_date'])
    bill_events['hearing_date'] = bill_events['hearing_date'].dt.strftime('%Y-%m-%d')


    # Format dates as strings AFTER all datetime operations
    #bill_events['hearing_date'] = bill_events['hearing_date'].dt.strftime('%Y-%m-%d')
    #bill_events['deadline_date'] = bill_events['deadline_date'].dt.strftime('%Y-%m-%d')

    return bill_events


################# DATE TIME FORMATTING ###############

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


######################### CONVERT DATA ###################################

def build_title(row):
    '''
    Helper function to build the title text for the calendar event blocks for display in streamlit-calendar.
    Combines bill number, chamber, hearing name, location, and room.
    '''
    
    # Derive chamber name from chamber_id
    chamber_id = row.get('chamber_id')
    if chamber_id == 1:
        chamber_name = 'Assembly'
    elif chamber_id == 2:
        chamber_name = 'Senate'
    else:
        chamber_name = ''

    # Build the title
    parts = []

    if row.get('billNumber') and row.get('hearingName'):
        parts.append(f"{row['billNumber']} - {chamber_name} {row['hearingName']} Committee")
    elif row.get('billNumber'):
        parts.append(row['billNumber'])
    elif row.get('hearingName'):
        parts.append(row['hearingName'])
    if row.get('hearing_location'):
        parts.append(row['hearing_location'])
    if row.get('hearing_room'):
        parts.append(row['hearing_room'])

    # Handle file order
    file_order = row.get('file_order')
    if file_order not in (None, '', float('nan')):
        try:
            parts.append(f"File order: {int(file_order)}")
        except (ValueError, TypeError):
            pass

    # Combine emoji prefix (if any) with rest of title
    title_body = ' | '.join(parts)
    row["title"] = title_body
    return row

def safe(val, is_id=False, is_date=False):
    ''' Helper function to safely convert values to string or return None if NaN.'''
    if pd.isna(val):
        if is_id:
            return "N/A"
        return None
    if is_date:
        return str(val)
    return val

def create_event_start_end(row):
    if row['is_allday']:
        row['start'] = str(row['hearing_date'])
        row['end'] = str(row['hearing_date'])
    else:
        row['start'] = str(convert_datetime(event_date=str(row['hearing_date']), event_time=str(row['hearingTimeVerbatim'])))
        row['end'] = str(convert_datetime(event_date=str(row['hearing_date']), event_time=str(row['hearingTimeVerbatim']), add_hours=1))
    return row

def sanitize_event(event: dict) -> dict:
    for key, value in event.items():
        if hasattr(value, 'isoformat'):
            event[key] = value.isoformat()
        elif isinstance(value, float) and pd.isna(value):
            event[key] = None
    return event

def filter_events(bill_events, leg_events, selected_types, selected_bills_for_calendar, bill_filter_active):
    '''
    Filters calendar events by bill and event type, and converts data to json format for rendering in streamlit calendar.
    '''
    # Initiate empty list of calendar events
    calendar_events = []
    initial_date = str(datetime.now())  # Default to current date if no events are selected
    
    # Map bill_data column names to camel case for downstream streamlit-calendar usage
    bill_events = bill_events.rename(
        columns = {
            'bill_number': 'billNumber',
            'bill_name': 'billName',
            'hearing_name': 'hearingName',
            'hearing_time_verbatim': 'hearingTimeVerbatim'
        }
    )

    # For events with a specific time, parse the event_time string to time object (combined date and time)
    bill_events = bill_events.apply(create_event_start_end, axis=1)

    # Special case for safe values: openstates bill ID
    bill_events['openstates_bill_id'] = bill_events['openstates_bill_id'].apply(
        lambda x: safe(x, is_id=True)
    )

    # Special case for safe values: date introduced
    bill_events['date_introduced'] = bill_events['date_introduced'].apply(
        lambda x: safe(x, is_date=True)
    )

    # Now check every cell to get safe values with map
    bill_events = bill_events.map(safe)

    # If filtering by bills (either dashboard bills or individually selected bills)
    if bill_filter_active:
        
        # Filter the bill_events DataFrame to only include selected bills
        filtered_bill_events = bill_events[bill_events['billNumber'].isin(selected_bills_for_calendar)]

        # If user only selects one bill, then set initial date to that bill's event date in order to jump to the event date on the calendar
        if len(selected_bills_for_calendar) == 1 and len(filtered_bill_events) == 1:
            initial_date = str(pd.to_datetime(filtered_bill_events.iloc[0]['hearing_date'])) # make sure its a string so its JSON compatible

        # If user selects one bill but there are multiple events for that bill:
        elif len(selected_bills_for_calendar) == 1 and len(filtered_bill_events) > 1:
            active_events = filtered_bill_events[filtered_bill_events['event_status'] == 'active']# Pick the soonest event overall, even if inactive or in the past
            soonest_event = filtered_bill_events.loc[pd.to_datetime(filtered_bill_events['event_date']).idxmin()]
            initial_date = str(pd.to_datetime(soonest_event['event_date']))

        # Add each filtered bill event to the calendar event list 
        # Build title
        filtered_bill_events = filtered_bill_events.apply(build_title, axis=1)

        # Assign event details
        filtered_bill_events["type"] = ""
        filtered_bill_events["event_class"] = ""
        filtered_bill_events['type'] = np.where(
            filtered_bill_events['chamber_id'] == 1,
            'Assembly',
            'Senate'
            )

        filtered_bill_events['event_class'] = np.where(
            filtered_bill_events['chamber_id'] == 1,
            'assembly',
            'senate'
            )
        
        filtered_bill_events['className'] = filtered_bill_events['event_class']

        # Convert to list of dictonaries and add to calendar events
        calendar_events.extend(filtered_bill_events.to_dict(orient='records'))

        # Add letter of support deadline events for all bill events
        letter_events = filtered_bill_events[filtered_bill_events['deadline_date'].notnull()].copy()
        
        # Letter event SPECIFIC columns
        letter_events['chamber_name'] = np.where(letter_events['chamber_id'] == 1, 'Assembly', 'Senate')
        letter_events['title'] = '✉️ LETTER DUE! ' + \
                letter_events['billNumber'].fillna('') + ' - ' + \
                letter_events['chamber_name'] + ' ' + \
                letter_events['hearingName'].fillna('')
        letter_events['start'] = letter_events['deadline_date']
        letter_events['end'] = letter_events['deadline_date']
        letter_events['type'] = 'Letter Deadline'
        letter_events['className'] = 'letter-deadline'
        # Convert to list of dictonaries and add to calendar events
        calendar_events.extend(letter_events.to_dict(orient='records'))

    # If filtering by event type, not bill
    elif not bill_filter_active and selected_types:

        # Add legislative events if selected
        if "Legislative" in selected_types:
            # Default title if missing
            leg_events[leg_events["title"].isna()]["title"] = "Legislative Event"
            leg_events["type"] = "Legislative"
            leg_events["billNumber"] = "N/A"
            leg_events["billName"] = "N/A"
            leg_events["hearingName"] = "N/A"
            leg_events["hearingTimeVerbatim"] = "N/A"
            leg_events["status"] = "N/A"
            leg_events["date_introduced"] = "N/A"
            leg_events["deadline_date"] = "N/A"
            leg_events["openstates_bill_id"] = "N/A"
            leg_events["className"] = "legislative event-normal"
            calendar_events.extend(leg_events.to_dict(orient='records'))
        
        # Add letter of support deadline events if selected
        if "Letter Deadline" in selected_types:
            # Only bills with letter deadlines need letter events
            letter_events = bill_events[bill_events['deadline_date'].notnull()].copy()
            
            # Letter event SPECIFIC columns
            letter_events['chamber_name'] = np.where(letter_events['chamber_id'] == 1, 'Assembly', 'Senate')
            letter_events['title'] = '✉️ LETTER DUE! ' + \
                letter_events['billNumber'].fillna('') + ' - ' + \
                letter_events['chamber_name'] + ' ' + \
                letter_events['hearingName'].fillna('')
            letter_events['start'] = letter_events['deadline_date']
            letter_events['end'] = letter_events['deadline_date']
            letter_events['type'] = 'Letter Deadline'
            letter_events['className'] = 'letter-deadline'

            # Convert to list of dictonaries and add to calendar events
            calendar_events.extend(letter_events.to_dict(orient='records'))

        # Add Assembly bill events if selected
        if "Assembly" in selected_types:
            assembly_events = bill_events[bill_events['chamber_id'] == 1].copy()
            
            # Build title
            assembly_events = assembly_events.apply(build_title, axis=1)

            # Assign event details
            assembly_events["event_class"] = "assembly" # All events are already filtered
            assembly_events['className'] = assembly_events['event_class'] 

            calendar_events.extend(assembly_events.to_dict(orient='records'))

        # Add Senate bill events if selected
        if "Senate" in selected_types:
            senate_events = bill_events[bill_events['chamber_id'] != 1].copy()

            # Build title
            senate_events = senate_events.apply(build_title, axis=1)
            # Assign event details
            senate_events["event_class"] = "senate" # All events are already filtered
            senate_events['className'] = senate_events['event_class']

            # Convert to list of dictonaries and add to calendar events
            calendar_events.extend(senate_events.to_dict(orient='records'))
    
    calendar_events = [sanitize_event(e) for e in calendar_events]
    
    return calendar_events, initial_date


################################## CSS ###################################

# Load external CSS file
def load_css(file_path):
    with open(file_path, "r") as f:
        return f"<style>{f.read()}</style>"

################## DOWNLOAD .ICS FILE ##########################

def create_ics_file(events):
    cal = Calendar()

    for event_data in events:
        event = Event()  # Create a new event
        
        # Build event title
        chamber_id = event_data.get('chamber_id')
        chamber_name = 'Assembly' if chamber_id == 1 else 'Senate' if chamber_id == 2 else ''
        event.name = f"{event_data['billNumber']} - {chamber_name} {event_data['hearingName']} Committee"
        
        # Build the description: bill name, event details (location, room), file order
        description = f"Bill Name: {event_data.get('billName', 'No name provided')}\n"
        description += f"Event Details: {event_data.get('title', 'No details provided')}\n"
        
        # Format the date range for the description (check if there's an 'end' date)
        start_date = event_data.get('start', 'Unknown Start Date')
        end_date = event_data.get('end', None)

        # Set the description
        event.description = description

        # Logic for all day events
        if event_data['hearingTimeVerbatim'] == 'N/A' or event_data['hearingTimeVerbatim'] == '' or "adjourn" in event_data['hearingTimeVerbatim']:
            try:
                event.begin = pd.to_datetime(start_date).to_pydatetime()
                event.end = pd.to_datetime(start_date).to_pydatetime()
                event.make_all_day()
            except Exception as e:
                print(event_data)
                # print(f"Start date is 'N/A', null, or None -- skipping: {e}")
                continue

            # Handle letter deadline events
            if "LETTER" in event_data['title']:
                try:
                    # Make all day
                    event.begin = pd.to_datetime(start_date).to_pydatetime()
                    event.end = pd.to_datetime(start_date).to_pydatetime()
                    event.make_all_day()
                    # Update the title
                    event.name = f"✉️ LETTER DUE - {event_data['billNumber']} - {chamber_name} {event_data['hearingName']} Committee"
                except Exception as e:
                    # If start = N/A then skip
                    # print(event_data)
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
    
    # return str(cal)  # Return the .ics content as a string
    return cal.serialize()