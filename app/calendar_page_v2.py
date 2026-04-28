#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar Page
Created on March 16, 2026
@author: danyasherbini

Alternative calendar page using native Streamlit widgets only (not using third-party streamlit-calendar library).
Calendar is structured in two tabs: 
- Tab 1 contains committee hearings and letter deadlines, displayed in the following format: 
    - Date headers
    - Under each date, are expanders for each committee hearing. 
    - Under each committee hearing are the bills on the agenda.
    - Each bill has a popover button that displays additional details (event details, bill details)
    - Letter deadlines exist as separate expanders, with the committee name as the expander header, 
    and the committee hearing date + list of bills underneath.
    - Committee hearings and letter deadlines have color-coded badges: Assembly, Senate, and Letter Deadline.
    - Filters (bill, dashboard, and event type) are now floating headers above the events instead of being in the sidebar.
- Tab 2 contains a legislative event calendar, displayed monthly.
    - Each event is rendered as an event pill/block using html.
    - Today's date is denoted with a colored circle around the date number.
    - There are no filters or clickable event buttons on this tab.

Additionally, in Tab 1, there are buttons and instructions for users to access their calendar URLs 
in order to add their calendars to an external calendar app (Google Calendar, Apple Calendar, Outlook, etc.).

"""

import calendar
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from db.query import get_my_dashboard_bills, get_org_dashboard_bills, get_working_group_bills
from utils.calendar_utils import load_leg_events, load_bill_events, load_css, render_bill, get_badge_color, get_user_token, get_org_token
from utils.profiling import track_rerun
from collections import defaultdict
track_rerun("Calendar")


# Page title
st.title("📅 Calendar")

# About this page
with st.expander("About this page", icon="ℹ️", expanded=False):
    st.markdown(
        """
        - This page displays two calendars: one for committee hearings and associated letter deadlines, and one for overall legislative events.
        - Committee hearings are sourced from Assembly and Senate calendar websites directly, so only available events are shown.
        - Letter Deadlines are auto-generated for 7 days before a committee hearing.
        - Event times are displayed in Pacific Time.
        """
    )

# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'authenticated' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Access user info from session state
org_id = st.session_state.get('org_id')
org_name = st.session_state['org_name']
org_nickname = st.session_state.get('nickname')
user_email = st.session_state['user_email']

# Get user's calendar tokens and URLs
def get_cal_URLs(org_id, user_email):
    try:
        user_token = get_user_token(user_email)
        org_token = get_org_token(org_id)

        user_url = f"http://leg-calendar-feed-btmit.ondigitalocean.app/feed/user/{user_token}"
        org_url = f"http://leg-calendar-feed-btmit.ondigitalocean.app/feed/org/{org_token}"
        wg_url = "http://leg-calendar-feed-btmit.ondigitalocean.app/feed/working-group/gFrfnhaAQGTWyiAfWjLh_dZG4Sh1jihbdHKNzJkqYF8"

        return user_url, org_url, wg_url
    except Exception as e:
        st.error(f"Error fetching calendar tokens: {e}")
        return None, None, None
    
user_url, org_url, wg_url = get_cal_URLs(org_id, user_email)

# Build user workflow to retrieve calendar URLs
st.markdown("### Get Your Calendar URLs")
st.caption(
    """
    Add your personalized calendar feed to your calendar app of choice (Google Calendar, Apple Calendar, Outlook, etc.). 
    Copy the URLs below and follow the instructions for your calendar app.
    """
)

col1, col2, col3 = st.columns(3)

def copy_button_html(url, label):
    return f"""
    <div style="margin-bottom: 8px;">
        <div style="
            background: #f0f2f6;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            padding: 10px 12px;
            font-family: monospace;
            font-size: 12px;
            word-break: break-all;
            color: #1f2937;
            margin-bottom: 8px;
        ">{url}</div>
        <button onclick="
            navigator.clipboard.writeText('{url}');
            this.textContent = '✓ Copied!';
            this.style.background = '#16a34a';
            this.style.borderColor = '#16a34a';
            setTimeout(() => {{
                this.textContent = '⎘ Copy URL';
                this.style.background = '#FF4B4B';
                this.style.borderColor = '#FF4B4B';
            }}, 2000);
        " style="
            width: 100%;
            padding: 0.25rem 0.75rem;
            background: #FF4B4B;
            color: white;
            border: 1px solid #FF4B4B;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 14px;
            font-weight: 400;
            font-family: 'Source Sans Pro', sans-serif;
            height: 2.5rem;
        ">⎘ Copy URL</button>
    </div>
    """

# Get dashboard bills
if "dashboard_bills" not in st.session_state or not len(st.session_state.dashboard_bills):
    st.session_state.dashboard_bills = get_my_dashboard_bills(user_email)

if "org_dashboard_bills" not in st.session_state or st.session_state.org_dashboard_bills is None:
    st.session_state.org_dashboard_bills = get_org_dashboard_bills(org_id)

if "wg_dashboard_bills" not in st.session_state or st.session_state.wg_dashboard_bills is None:
    st.session_state.wg_dashboard_bills = get_working_group_bills()

# Load data
leg_events  = load_leg_events()
bill_events = load_bill_events()

# Load css
custom_css = load_css('styles/calendar.css')

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
span[data-baseweb="tag"]:has(span[title="Senate"]) {
  color: #BD4043;
  background-color: #FFE8E8;
}

span[data-baseweb="tag"]:has(span[title="Assembly"]) {
  color: #158237;
  background-color: #E8FAF0;
}

span[data-baseweb="tag"]:has(span[title="Letter Deadline"]) {
  color: #E2660C;
  background-color: #FFF5E6;
}
</style>
""", unsafe_allow_html=True)


# Group bills by hearing_name and hearing_date; store event details in a dict for easy access in the popover
bill_events_sorted = bill_events.sort_values(['hearing_date', 'file_order'])

# Convert to nested dict: {date -> {committee -> {'chamber_id': ..., 'bills': [...]}}}
structured = defaultdict(lambda: defaultdict(lambda: {'chamber_id': None, 'bills': []}))

for _, row in bill_events_sorted.iterrows():
    date_key = str(row['hearing_date'])
    committee_name = row['hearing_name']

    bill = {
        'bill_number': row['bill_number'],
        'bill_name': row['bill_name'],
        'details': {
            'status': row['status'],
            'date_introduced': str(row['date_introduced']),
            'chamber_id': row['chamber_id'],
            'file_order': row['file_order'],
            'hearing_name': row['hearing_name'],
            'hearing_date': str(row['hearing_date']),
            'hearing_time': str(row['hearing_time']),
            'hearing_location': row['hearing_location'],
            'hearing_room': row['hearing_room'],
            'deadline_date': str(row['deadline_date']),
        }
    }

    structured[date_key][committee_name]['chamber_id'] = row['chamber_id']
    structured[date_key][committee_name]['bills'].append(bill)

structured = {date_key: dict(committees) for date_key, committees in structured.items()}

## Build the calendar display
# Two tabs
tab1, tab2 = st.tabs(["🏛️ Committee Hearings", "📅 Legislative Calendar"]) 

## Committee hearings tab
with tab1:

    # Inline filters for bill number, dashboard, and event type
    st.markdown("#### Filters")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        unique_bills = sorted(bill_events['bill_number'].dropna().unique())
        selected_bills = st.multiselect(
            "Bill Number",
            options=unique_bills,
            default=[],
            placeholder="Search by bill number...",
            help="Filter events by bill number. You can select multiple bills to see hearings and letter deadlines that include any of the selected bills."
        )

    with filter_col2:
        dashboard_options = []
        if st.session_state.get('dashboard_bills') is not None and len(st.session_state.dashboard_bills) > 0:
            dashboard_options.append("My Dashboard")
        if st.session_state.get('org_dashboard_bills') is not None and len(st.session_state.org_dashboard_bills) > 0:
            dashboard_options.append(f"{org_name}'s Dashboard")
        if st.session_state.get('wg_dashboard_bills') is not None and len(st.session_state.wg_dashboard_bills) > 0:
            dashboard_options.append("AI Working Group Dashboard")

        selected_dashboards = st.multiselect(
            "Dashboard",
            options=dashboard_options,
            default=[],
            placeholder="Filter by dashboard...",
            help="Filter events by dashboard. Selecting a dashboard will show hearings and letter deadlines for bills that are on that dashboard. You can select multiple dashboards to see events for bills that are on any of the selected dashboards."
        )

    with filter_col3:
        event_type_options = ["Senate", "Assembly", "Letter Deadline"]
        selected_event_types = st.multiselect(
            "Event Type",
            options=event_type_options,
            default=event_type_options,
            placeholder="Filter by event type...",
            help="Filter events by type. 'Senate' and 'Assembly' correspond to committee hearings for each chamber, while 'Letter Deadline' corresponds to letter deadlines for those hearings. You can select multiple event types to see all matching events."
        )

    st.markdown('')
    st.divider()

    # Apply filters
    filtered_events = bill_events.copy()

    # Apply bill number filter
    if selected_bills:
        filtered_events = filtered_events[filtered_events['bill_number'].isin(selected_bills)]

    # Apply dashboard filter
    if selected_dashboards:
        dashboard_bill_numbers = set()
        if "My Dashboard" in selected_dashboards and st.session_state.get('dashboard_bills') is not None:
            dashboard_bill_numbers.update(st.session_state.dashboard_bills['bill_number'].tolist())
        if f"{org_name}'s Dashboard" in selected_dashboards and st.session_state.get('org_dashboard_bills') is not None:
            dashboard_bill_numbers.update(st.session_state.org_dashboard_bills['bill_number'].tolist())
        if "AI Working Group Dashboard" in selected_dashboards and st.session_state.get('wg_dashboard_bills') is not None:
            dashboard_bill_numbers.update(st.session_state.wg_dashboard_bills['bill_number'].tolist())
        filtered_events = filtered_events[filtered_events['bill_number'].isin(dashboard_bill_numbers)]

    # Split into hearing events and deadline events based on selected event types
    hearing_events = pd.DataFrame()
    deadline_events = pd.DataFrame()

    if "Assembly" in selected_event_types and "Senate" in selected_event_types:
        hearing_events = filtered_events
    elif "Assembly" in selected_event_types:
        hearing_events = filtered_events[filtered_events['chamber_id'] == 1]
    elif "Senate" in selected_event_types:
        hearing_events = filtered_events[filtered_events['chamber_id'] == 2]

    if "Letter Deadline" in selected_event_types:
        deadline_events = filtered_events[
            filtered_events['deadline_date'].notna() &
            (filtered_events['deadline_date'] != '') &
            (filtered_events['deadline_date'] != 'nan')
        ].copy()

    # Build filtered_structured from hearing_events only
    filtered_sorted = hearing_events.sort_values(['hearing_date', 'file_order']) if not hearing_events.empty else pd.DataFrame()
    filtered_structured = defaultdict(lambda: defaultdict(lambda: {'chamber_id': None, 'bills': []}))

    for _, row in filtered_sorted.iterrows():
        date_key = str(row['hearing_date'])
        committee_name = row['hearing_name']
        bill = {
            'bill_number': row['bill_number'],
            'bill_name': row['bill_name'],
            'details': {
                'status': row['status'],
                'date_introduced': str(row['date_introduced']),
                'chamber_id': row['chamber_id'],
                'file_order': row['file_order'],
                'hearing_name': row['hearing_name'],
                'hearing_date': str(row['hearing_date']),
                'hearing_time': str(row['hearing_time']),
                'hearing_location': row['hearing_location'],
                'hearing_room': row['hearing_room'],
                'deadline_date': str(row['deadline_date']),
            }
        }
        filtered_structured[date_key][committee_name]['chamber_id'] = row['chamber_id']
        filtered_structured[date_key][committee_name]['bills'].append(bill)

    filtered_structured = {date_key: dict(committees) for date_key, committees in filtered_structured.items()}

    # Build deadline_structured from deadline_events only -- i.e. letter deadlines
    deadline_structured = defaultdict(lambda: defaultdict(list))
    
    for _, row in deadline_events.iterrows():
        deadline_key = str(row['deadline_date'])
        committee_name = row['hearing_name']
        deadline_structured[deadline_key][committee_name].append({
            'bill_number': row['bill_number'],
            'bill_name': row['bill_name'],
            'chamber_id': int(row['chamber_id']) if pd.notna(row['chamber_id']) else None,        
            'committee_name': row['hearing_name'],
            'hearing_date': str(row['hearing_date']),  # This is the event of the commmitee hearing that the letter deadline corresponds to
        })

    deadline_structured = {k: dict(v) for k, v in deadline_structured.items()}

    # Download all events button + total events count
    col1, col2 = st.columns([8, 2])
    with col1:
        # Display count of events being shown based on current filters
        today_str = date.today().isoformat()
        total_hearings = sum(len(committees) for d, committees in filtered_structured.items() if d >= today_str)
        total_deadlines = sum(len(committees) for d, committees in deadline_structured.items() if d >= today_str)
        # Adjust caption to account for pluralization
        hearing_text = "Committee Hearing" if total_hearings == 1 else "Committee Hearings"
        deadline_text = "Letter Deadline" if total_deadlines == 1 else "Letter Deadlines"
        st.caption(f"**Displaying:** 🏛️ {total_hearings} {hearing_text} | ✉️ {total_deadlines} {deadline_text}")

    with col2:
        st.markdown('')

    # Determine if filters are active -- this will determine whether to keep expanders open
    # or closed by default
    filters_active = bool(selected_bills or selected_dashboards)

    # Render events -- ONLY SHOW EVENTS TODAY OR AFTER
    all_dates = sorted(
        d for d in set(list(filtered_structured.keys()) + list(deadline_structured.keys()))
        if d >= today_str
    )

    if not all_dates:
        st.info("No committee hearings match the current filters.")
    else:
        for hearing_date in all_dates:
            friendly_date = pd.to_datetime(hearing_date).strftime("%A, %B %d, %Y")
            st.markdown(f"#### 📅 {friendly_date}")

            # Committee hearing events
            if hearing_date in filtered_structured:
                committees = filtered_structured[hearing_date]
                committees = dict(sorted(committees.items(), key=lambda x: x[1]['chamber_id']))

                for committee_name, committee_data in committees.items():
                    chamber_id = committee_data['chamber_id']
                    bills = committee_data['bills']

                    # Grab chamber name and hearing date for expander content below
                    chamber_name = f"{'Assembly' if chamber_id == 1 else 'Senate'}"

                    col1, col2 = st.columns([1, 9])
                    with col1:
                        # Apply color-coded badge to denote chamber
                        st.badge(
                            label="Assembly" if chamber_id == 1 else "Senate",
                            color=get_badge_color(chamber_id)
                        )
                    with col2:
                        # Build expander with content
                        with st.expander(committee_name, expanded=filters_active):

                            # Display info as captions                            
                            st.caption(f"📝 Bills on the agenda for {chamber_name} {committee_name} Committee")
                            st.caption(f"📅 Committee Hearing: {friendly_date}")
                            
                            # Display bills under the committee hearing expander
                            for bill in bills:
                                render_bill(bill)

            # Letter deadline events
            if hearing_date in deadline_structured:
                for committee_name, bills in deadline_structured[hearing_date].items():
                    
                    # Retrieve chamber_id, chamber name, and hearing date for expander content below
                    chamber_id = bills[0].get('chamber_id')
                    chamber_name = f"{'Assembly' if chamber_id == 1 else 'Senate'}"
                    hearing_date = pd.to_datetime(bills[0]['hearing_date']).strftime("%A, %B %d, %Y")

                    col1, col2 = st.columns([1, 9])
                    with col1:
                        # Apply color-coded badge to denote letter deadlines
                        st.badge(label="Letter Deadline", color="orange")

                    with col2:                        
                        # Build expander with content
                        with st.expander(committee_name, expanded=filters_active):

                            # Display chamber and hearing date as captions                            
                            st.caption(f"⚠️ Letter Deadline for {chamber_name} {committee_name} Committee")
                            st.caption(f"📅 Committee Hearing: {hearing_date}")

                            # Display bills under the letter deadline expander
                            for bill in bills:
                                st.markdown(f"- **{bill['bill_number']}** — {bill['bill_name']}")

            st.divider()

## Legislative calendar tab
with tab2:
    # Normalize leg_events dates
    leg_events['date'] = pd.to_datetime(leg_events['start']).dt.date

    # Get range of months to display from leg_events
    if not leg_events.empty:
        min_month = leg_events['date'].min().replace(day=1)
        max_month = leg_events['date'].max().replace(day=1)
    else:
        today = date.today()
        min_month = today.replace(day=1)
        max_month = today.replace(day=1)

    # Build a lookup: {date -> [event titles]}
    events_by_date = defaultdict(list)
    for _, row in leg_events.iterrows():
        start = pd.to_datetime(row['start']).date()
        end = pd.to_datetime(row['end']).date()
        current = start
        while current < end:
            events_by_date[current].append(row['title'])
            current += timedelta(days=1)

    # Iterate through each month and render a calendar grid
    current_month = min_month
    today = date.today()

    while current_month <= max_month:
        year = current_month.year
        month = current_month.month
        month_label = current_month.strftime("%B %Y")

        # Collapse past months, expand current and future months
        is_past = (year, month) < (today.year, today.month)
        
        with st.expander(f"**{month_label}**", expanded=not is_past):

            # Count events for this month
            month_event_count = sum(
                len(titles)
                for d, titles in events_by_date.items()
                if d.year == year and d.month == month
            )
            hearing_name = "event" if month_event_count == 1 else "events"
            st.caption(f"📅 {month_event_count} legislative {hearing_name} this month")

            # Day-of-week headers
            day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            header_cols = st.columns(7, gap="small")
            for i, col in enumerate(header_cols):
                col.markdown(
                    f"<div style='text-align:right; font-weight:600; "
                    f"color:var(--text-color); opacity:0.5; "
                    f"font-size:0.8rem; padding:6px 8px 4px; "
                    f"border-bottom:2px solid var(--text-color);'>"
                    f"{day_headers[i]}</div>",
                    unsafe_allow_html=True
                )

            # Calendar weeks
            cal = calendar.monthcalendar(year, month)
            for week in cal:
                week_cols = st.columns(7, gap="small")
                for i, day_num in enumerate(week):
                    with week_cols[i]:
                        if day_num == 0:
                            st.markdown(
                                "<div style='min-height:130px; "
                                "border:1px solid var(--border-color, rgba(128,128,128,0.2)); "
                                "background:var(--secondary-background-color);'></div>",
                                unsafe_allow_html=True
                            )
                        else:
                            day_date = date(year, month, day_num)
                            day_events = events_by_date.get(day_date, [])
                            is_today = day_date == today

                            day_num_style = (
                                "font-weight:700; color:#fff; background:var(--primary-color, #1A1A2E); "
                                "border-radius:50%; width:22px; height:22px; display:inline-flex; "
                                "align-items:center; justify-content:center; font-size:0.8rem;"
                            ) if is_today else "font-weight:500; color:var(--text-color);"

                            events_html = "".join([
                                f"<div style='background-color:#dbeafe; color:#1e40af; border-radius:4px; "
                                f"padding:2px 6px; font-size:0.68rem; margin-bottom:3px; "
                                f"word-wrap:break-word; line-height:1.3;'>{title}</div>"
                                for title in day_events
                            ])

                            st.markdown(
                                f"<div style='min-height:130px; "
                                f"border:1px solid var(--border-color, rgba(128,128,128,0.2)); "
                                f"padding:6px 8px; vertical-align:top;'>"
                                f"<div style='text-align:right; margin-bottom:4px;'>"
                                f"<span style='{day_num_style}'>{day_num}</span></div>"
                                f"{events_html}</div>",
                                unsafe_allow_html=True
                            )

        # Advance to next month
        if month == 12:
            current_month = current_month.replace(year=year + 1, month=1)
        else:
            current_month = current_month.replace(month=month + 1)
