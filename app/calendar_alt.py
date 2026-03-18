#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar Page
Created on March 16, 2026
@author: danyasherbini

Alternative calendar page using native Streamlit widgets only (not using third-party streamlit-calendar library).
Calendar is structured in two tabs: 
- Tab 1 contains a legislative event calendar, displayed monthly.
    - Each event is rendered as an event pill/block using html.
    - Today's date is denoted with a colored circle around the date number.
    - There are no filters or clickable event buttons on this tab.
- Tab 2 contains committee hearings and letter deadlines, displayed in the following format: 
    - Date headers
    - Under each date, are expanders for each committee hearing. 
    - Under each committee hearing are the bills on the agenda.
    - Each bill has a popover button that displays additional details (event details, bill details)
    - Letter deadlines exist as separate expanders, with the committee name as the expander header, 
    and the committee hearing date + list of bills underneath.
    - Committee hearings and letter deadlines have color-coded badges: Assembly, Senate, and Letter Deadline.
    - Filters (bill, dashboard, and event type) are now floating headers above the events instead of being in the sidebar.

"""

import calendar
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from db.query import get_my_dashboard_bills, get_org_dashboard_bills, get_working_group_bills
from utils.calendar_utils import load_leg_events, load_bill_events, create_ics_file, load_css, render_bill, get_badge_color, create_ics_all, create_ics_single
from utils.profiling import track_rerun
from collections import defaultdict
 
track_rerun("Calendar")

# Page title
st.title("📅 Calendar")

# About this page
with st.expander("About this page", icon="ℹ️", expanded=False):
    st.markdown(
        """
        This page displays two calendars: one for overall legislative events,
        and another for committee hearings and associated letter deadlines.
        Committee hearings are sourced from Assembly and Senate calendar websites directly, so only available current and upcoming events are shown.
        Letter deadlines are auto-generated for 7 days before a committee hearing.

        **Notes:**
        - **Time zone:** Events times are displayed in Pacific Time.
        - **Downloading events:** You can download committee hearing events and letter deadlines as an .ics file to add to your personal calendar.
        
        """
    )

# Session state
# Get user info
user_email = st.session_state["user_email"]
org_id     = st.session_state["org_id"]
org_name   = st.session_state["org_name"]

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


# Group bills by event_text and event_date; store event details in a dict for easy access in the popover
bill_events_sorted = bill_events.sort_values(['event_date', 'agenda_order'])

# Convert to nested dict: {date -> {committee -> {'chamber_id': ..., 'bills': [...]}}}
structured = defaultdict(lambda: defaultdict(lambda: {'chamber_id': None, 'bills': []}))

for _, row in bill_events_sorted.iterrows():
    date_key = str(row['event_date'])
    committee_name = row['event_text']

    bill = {
        'bill_number': row['bill_number'],
        'bill_name': row['bill_name'],
        'details': {
            'status': row['status'],
            'date_introduced': str(row['date_introduced']),
            'chamber_id': row['chamber_id'],
            'agenda_order': row['agenda_order'],
            'event_text': row['event_text'],
            'event_date': str(row['event_date']),
            'event_time': str(row['event_time']),
            'event_location': row['event_location'],
            'event_room': row['event_room'],
            'revised': row['revised'],
            'event_status': row['event_status'],
            'letter_deadline': str(row['letter_deadline']),
        }
    }

    structured[date_key][committee_name]['chamber_id'] = row['chamber_id']
    structured[date_key][committee_name]['bills'].append(bill)

structured = {date_key: dict(committees) for date_key, committees in structured.items()}

## Build the calendar display
# Two tabs
tab1, tab2 = st.tabs(["📅 Legislative Calendar", "📋 Committee Hearings"]) 

## Legislative calendar tab
with tab1:
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
        events_by_date[row['date']].append(row['title'])

    # Iterate through each month and render a calendar grid
    current_month = min_month
    while current_month <= max_month:
        year = current_month.year
        month = current_month.month
        month_label = current_month.strftime("%B %Y")

        st.markdown(f"### {month_label}")

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
                            "<div style='min-height:80px; "
                            "border:1px solid var(--border-color, rgba(128,128,128,0.2)); "
                            "background:var(--secondary-background-color);'></div>",
                            unsafe_allow_html=True
                        )
                    else:
                        day_date = date(year, month, day_num)
                        day_events = events_by_date.get(day_date, [])
                        is_today = day_date == date.today()

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
                            f"<div style='min-height:80px; "
                            f"border:1px solid var(--border-color, rgba(128,128,128,0.2)); "
                            f"padding:6px 8px; vertical-align:top;'>"
                            f"<div style='text-align:right; margin-bottom:4px;'>"
                            f"<span style='{day_num_style}'>{day_num}</span></div>"
                            f"{events_html}</div>",
                            unsafe_allow_html=True
                        )

        st.divider()

        # Advance to next month
        if month == 12:
            current_month = current_month.replace(year=year + 1, month=1)
        else:
            current_month = current_month.replace(month=month + 1)

## Committee hearings tab
with tab2:

    # Inline filters for bill number, dashboard, and event type
    st.markdown("#### Filters")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        unique_bills = sorted(bill_events['bill_number'].unique())
        selected_bills = st.multiselect(
            "Bill Number",
            options=unique_bills,
            default=[],
            placeholder="Search by bill number...",
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
        )

    with filter_col3:
        event_type_options = ["Senate", "Assembly", "Letter Deadline"]
        selected_event_types = st.multiselect(
            "Event Type",
            options=event_type_options,
            default=event_type_options,
            placeholder="Filter by event type...",
        )

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
            filtered_events['letter_deadline'].notna() &
            (filtered_events['letter_deadline'] != '') &
            (filtered_events['letter_deadline'] != 'nan')
        ].copy()

    # Build filtered_structured from hearing_events only
    filtered_sorted = hearing_events.sort_values(['event_date', 'agenda_order']) if not hearing_events.empty else pd.DataFrame()
    filtered_structured = defaultdict(lambda: defaultdict(lambda: {'chamber_id': None, 'bills': []}))

    for _, row in filtered_sorted.iterrows():
        date_key = str(row['event_date'])
        committee_name = row['event_text']
        bill = {
            'bill_number': row['bill_number'],
            'bill_name': row['bill_name'],
            'details': {
                'status': row['status'],
                'date_introduced': str(row['date_introduced']),
                'chamber_id': row['chamber_id'],
                'agenda_order': row['agenda_order'],
                'event_text': row['event_text'],
                'event_date': str(row['event_date']),
                'event_time': str(row['event_time']),
                'event_location': row['event_location'],
                'event_room': row['event_room'],
                'revised': row['revised'],
                'event_status': row['event_status'],
                'letter_deadline': str(row['letter_deadline']),
            }
        }
        filtered_structured[date_key][committee_name]['chamber_id'] = row['chamber_id']
        filtered_structured[date_key][committee_name]['bills'].append(bill)

    filtered_structured = {date_key: dict(committees) for date_key, committees in filtered_structured.items()}

    # Build deadline_structured from deadline_events only -- i.e. letter deadlines
    deadline_structured = defaultdict(lambda: defaultdict(list))
    
    for _, row in deadline_events.iterrows():
        deadline_key = str(row['letter_deadline'])
        committee_name = row['event_text']
        deadline_structured[deadline_key][committee_name].append({
            'bill_number': row['bill_number'],
            'bill_name': row['bill_name'],
            'event_date': str(row['event_date']),  # This is the event of the commmitee hearing that the letter deadline corresponds to
        })

    deadline_structured = {k: dict(v) for k, v in deadline_structured.items()}

    # Download all events button
    all_ics = create_ics_all(filtered_structured, deadline_structured)
    download_col1, download_col2 = st.columns([8, 2])
    with download_col1:
        st.markdown("")
    with download_col2:
        st.download_button(
            label="📥 Download All Events (.ics)",
            data=all_ics,
            file_name="committee_hearings.ics",
            mime="text/calendar",
            key="download_all_button",
            width='stretch',
            type="secondary"
        )

    # Render events
    all_dates = sorted(set(list(filtered_structured.keys()) + list(deadline_structured.keys())))

    if not all_dates:
        st.info("No committee hearings match the current filters.")
    else:
        for event_date in all_dates:
            friendly_date = pd.to_datetime(event_date).strftime("%A, %B %d, %Y")
            st.markdown(f"#### 📅 {friendly_date}")

            # Committee hearing events
            if event_date in filtered_structured:
                committees = filtered_structured[event_date]
                committees = dict(sorted(committees.items(), key=lambda x: x[1]['chamber_id']))

                for committee_name, committee_data in committees.items():
                    chamber_id = committee_data['chamber_id']
                    bills = committee_data['bills']

                    col1, col2 = st.columns([1, 9])
                    with col1:
                        st.badge(
                            label="Assembly" if chamber_id == 1 else "Senate",
                            color=get_badge_color(chamber_id)
                        )
                    with col2:
                        with st.expander(committee_name, expanded=False):
                            for bill in bills:
                                render_bill(bill)

            # Letter deadline events
            if event_date in deadline_structured:
                for committee_name, bills in deadline_structured[event_date].items():
                    col1, col2 = st.columns([1, 9])
                    with col1:
                        st.badge(label="Letter Deadline", color="orange")
                    with col2:
                        with st.expander(committee_name, expanded=False):
                            # Show the committee hearing date once at the top
                            hearing_date = pd.to_datetime(bills[0]['event_date']).strftime("%A, %B %d, %Y")
                            st.caption(f"📅 Committee Hearing: {hearing_date}")
                            for bill in bills:
                                st.markdown(f"- **{bill['bill_number']}** — {bill['bill_name']}")

            st.divider()