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
from utils.calendar_utils import load_leg_events, load_committee_events, load_css, render_bill, get_badge_color, get_user_token, get_org_token
from utils.profiling import track_rerun
from collections import defaultdict
from st_copy import copy_button # Streamlit component to make copy buttons
track_rerun("Calendar")


# Page title
st.title("📅 Calendar")

# About this page
with st.expander("About this page", icon="ℹ️", expanded=False):
    st.markdown(
        """
        This page displays three tabs: 

        **Tab 1: Committee Hearings & Deadlines**
        - This tab displays upcoming committee hearings and letter deadlines.
        - Committee hearings are sourced from Assembly and Senate calendar websites directly, so only available events are shown.
        - Only events today or in the future are displayed.
        - Letter Deadlines are auto-generated for 7 days before a committee hearing, and are only generated for hearings that have bills on the agenda.
        - Some committee hearings do not have any bills on their public agenda yet.
        - Event times are displayed in Pacific Time.

        **Tab 2: Legislative Event Calendar**
        - This tab displays a calendar view of legislative events sourced from this legislative cycle's public calendar.
        - Past months are collapsed by default.

        **Tab 3: My Calendar URLs**
        - This tab displays your custom URLs for calendar feeds that you can add to any external calendar app (Google Calendar, Apple Calendar, Outlook, etc.).
        - Copy your URLs and follow the instructions to add them to an external calendar app.
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

# Get dashboard bills
if "dashboard_bills" not in st.session_state or not len(st.session_state.dashboard_bills):
    st.session_state.dashboard_bills = get_my_dashboard_bills(user_email)

if "org_dashboard_bills" not in st.session_state or st.session_state.org_dashboard_bills is None:
    st.session_state.org_dashboard_bills = get_org_dashboard_bills(org_id)

if "wg_dashboard_bills" not in st.session_state or st.session_state.wg_dashboard_bills is None:
    st.session_state.wg_dashboard_bills = get_working_group_bills()

# Load data
leg_events  = load_leg_events()
hearings, hearing_bills, hearing_deadlines = load_committee_events()

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


# Convert hearing_date to string for consistent keying
hearings['hearing_date'] = hearings['hearing_date'].astype(str)
hearing_deadlines['deadline_date'] = hearing_deadlines['deadline_date'].astype(str)

# Build lookup dicts for fast access
# {hearing_id -> [bill rows]}
bills_by_hearing = hearing_bills.groupby('hearing_id')

# {hearing_id -> deadline row}
deadlines_by_hearing = hearing_deadlines.set_index('hearing_id').to_dict('index') if not hearing_deadlines.empty else {}

# Build structured dict: {date -> {committee_name -> {'hearing_row': ..., 'bills': [...]}}}
structured = defaultdict(dict)
for _, h_row in hearings.iterrows():
    date_key = h_row['hearing_date']
    committee_name = h_row['hearing_name']
    hearing_id = h_row['hearing_id']

    # Get bills for this hearing (empty list if none)
    if hearing_id in bills_by_hearing.groups:
        bills = [row for _, row in bills_by_hearing.get_group(hearing_id).iterrows()]
    else:
        bills = []

    # Get deadline for this hearing (None if none)
    deadline_row = deadlines_by_hearing.get(hearing_id)

    structured[date_key][committee_name] = {
        'hearing_row': h_row,
        'bills': bills,
        'deadline_row': deadline_row,
    }

structured = dict(structured)

## Build the calendar display
tab1, tab2, tab3 = st.tabs(["🏛️ Committee Hearings", "📅 Legislative Calendar", "🔗 My Calendar URLs"])

with tab1:

    st.markdown("#### Filters")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        unique_bills = sorted(hearing_bills['bill_number'].dropna().unique())
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

    # Build dashboard bill number sets for filtering
    dashboard_bill_numbers = set()
    if selected_dashboards:
        if "My Dashboard" in selected_dashboards and st.session_state.get('dashboard_bills') is not None:
            dashboard_bill_numbers.update(st.session_state.dashboard_bills['bill_number'].tolist())
        if f"{org_name}'s Dashboard" in selected_dashboards and st.session_state.get('org_dashboard_bills') is not None:
            dashboard_bill_numbers.update(st.session_state.org_dashboard_bills['bill_number'].tolist())
        if "AI Working Group Dashboard" in selected_dashboards and st.session_state.get('wg_dashboard_bills') is not None:
            dashboard_bill_numbers.update(st.session_state.wg_dashboard_bills['bill_number'].tolist())

    def filter_bills(bills: list, selected_bills: list, dashboard_bill_numbers: set) -> list:
        """Filter a list of bill rows by bill number and/or dashboard membership."""
        if selected_bills:
            bills = [b for b in bills if b.get('bill_number') in selected_bills]
        if dashboard_bill_numbers:
            bills = [b for b in bills if b.get('bill_number') in dashboard_bill_numbers]
        return bills

    # Apply filters and build filtered_structured and deadline_structured
    today_str = date.today().isoformat()
    filtered_structured = defaultdict(dict)
    deadline_structured = defaultdict(dict)  # {deadline_date -> {committee_name -> {hearing_row, bills, deadline_row}}}

    for date_key, committees in structured.items():
        for committee_name, data in committees.items():
            h_row = data['hearing_row']
            bills = data['bills']
            deadline_row = data['deadline_row']
            chamber_id = h_row.get('chamber_id')

            # Filter bills
            filtered_bills = filter_bills(bills, selected_bills, dashboard_bill_numbers)

            # If dashboard or bill filter is active, skip hearings with no matching bills
            if (selected_bills or selected_dashboards) and not filtered_bills:
                continue

            # Apply event type filter for hearings
            include_hearing = (
                ("Assembly" in selected_event_types and chamber_id == 1) or
                ("Senate" in selected_event_types and chamber_id == 2)
            )
            if include_hearing:
                filtered_structured[date_key][committee_name] = {
                    'hearing_row': h_row,
                    'bills': filtered_bills,
                    'deadline_row': deadline_row,
                }

            # Build deadline_structured — only include if there are bills associated with this deadline
            if "Letter Deadline" in selected_event_types and deadline_row and deadline_row.get('deadline_date') and filtered_bills:
                deadline_key = str(deadline_row['deadline_date'])
                if deadline_key >= today_str:
                    deadline_structured[deadline_key][committee_name] = {
                        'hearing_row': h_row,
                        'bills': filtered_bills,
                        'deadline_row': deadline_row,
                    }

    filtered_structured = dict(filtered_structured)
    deadline_structured = dict(deadline_structured)

    # Event counts
    col1, col2 = st.columns([8, 2])
    with col1:
        total_hearings = sum(len(committees) for d, committees in filtered_structured.items() if d >= today_str)
        total_deadlines = sum(len(committees) for d, committees in deadline_structured.items() if d >= today_str)
        hearing_text = "Committee Hearing" if total_hearings == 1 else "Committee Hearings"
        deadline_text = "Letter Deadline" if total_deadlines == 1 else "Letter Deadlines"
        st.caption(f"**Displaying:** 🏛️ {total_hearings} {hearing_text} | ✉️ {total_deadlines} {deadline_text}")
    with col2:
        st.markdown('')

    filters_active = bool(selected_bills or selected_dashboards)

    # Render events — today and future only
    all_dates = sorted(
        d for d in set(list(filtered_structured.keys()) + list(deadline_structured.keys()))
        if d >= today_str
    )

    if not all_dates:
        st.info("No committee hearings match the current filters.")
    else:
        for event_date in all_dates:
            friendly_date = pd.to_datetime(event_date).strftime("%A, %B %d, %Y")
            st.markdown(f"#### 📅 {friendly_date}")

            # Committee hearing events
            if event_date in filtered_structured:
                committees = filtered_structured[event_date]
                committees = dict(sorted(committees.items(), key=lambda x: x[1]['hearing_row'].get('chamber_id') or 99))

                for committee_name, data in committees.items():
                    h_row = data['hearing_row']
                    bills = data['bills']
                    deadline_row = data['deadline_row']
                    chamber_id = h_row.get('chamber_id')
                    chamber_name = 'Assembly' if chamber_id == 1 else 'Senate'

                    col1, col2 = st.columns([1, 9])
                    with col1:
                        st.badge(
                            label="Assembly" if chamber_id == 1 else "Senate",
                            color=get_badge_color(chamber_id)
                        )
                    with col2:
                        with st.expander(committee_name, expanded=filters_active):
                            st.caption(f"📝 Bills on the agenda for {chamber_name} {committee_name} Committee")
                            st.caption(f"📅 Committee Hearing: {friendly_date}")

                            if bills:
                                for bill_row in bills:
                                    render_bill(
                                        bill_number=bill_row.get('bill_number', 'N/A'),
                                        bill_name=bill_row.get('bill_name', 'N/A'),
                                        hearing_row=h_row,
                                        bill_row=bill_row,
                                        deadline_row=deadline_row,
                                    )
                            else:
                                st.caption("No bills on the agenda yet.")

            # Letter deadline events
            if event_date in deadline_structured:
                for committee_name, data in deadline_structured[event_date].items():
                    h_row = data['hearing_row']
                    bills = data['bills']
                    deadline_row = data['deadline_row']
                    chamber_id = h_row.get('chamber_id')
                    chamber_name = 'Assembly' if chamber_id == 1 else 'Senate'
                    hearing_friendly = pd.to_datetime(h_row.get('hearing_date')).strftime("%A, %B %d, %Y")

                    col1, col2 = st.columns([1, 9])
                    with col1:
                        st.badge(label="Letter Deadline", color="orange")
                    with col2:
                        with st.expander(committee_name, expanded=filters_active):
                            st.caption(f"⚠️ Letter Deadline for {chamber_name} {committee_name} Committee")
                            st.caption(f"📅 Committee Hearing: {hearing_friendly}")

                            if bills:
                                for bill_row in bills:
                                    st.markdown(f"- **{bill_row.get('bill_number')}** — {bill_row.get('bill_name')}")
                            else:
                                st.markdown("No bills associated with this deadline yet.")

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

## My calendar URLs tab
with tab3:
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
    st.markdown("### Get Your Personalized Calendar Feeds")
    st.markdown(
        """
        - Add your personalized calendar feeds to your calendar app of choice (Google Calendar, Apple Calendar, Outlook, etc.). 
        - These calendar feeds update every day with data from the CA Legislation Tracker so you can stay on top of hearings and deadlines for bills that matter to you.
        - Each calendar feed displays events for the bills on the corresponding dashboard(s):
            - *My Dashboard Calendar*: Events for bills on your personal dashboard.
            - *Organization Dashboard Calendar*: Events for bills on your organization's dashboard.
            - *AI Working Group Dashboard Calendar*: Events for bills on the AI Working Group dashboard.
        - When you add a bill to any of your dashboards, that bill's hearings and deadlines will automatically appear in the corresponding calendar feed.
        """
    )
    st.markdown('')
    st.markdown('### My Calendar URLs')
    st.caption("Copy the URLs below and import to your calendar app of choice.")

    # Columns for each calendar URL
    outer_col1, outer_col2, outer_col3 = st.columns(3)

    with outer_col1: 
        st.markdown(f"##### 🏢 {org_nickname} Dashboard")
        with st.container(border=True):
            st.code(org_url, language=None)

            org_col1, org_col2 = st.columns([8, 2])    
            with org_col1: 
                st.markdown("**Copy URL:**")
            with org_col2: 
                copy_button(
                    org_url,
                    icon='material_symbols',  # default, use 'st' as alternative
                    #tooltip='Any tooltip text',  # defaults to 'Copy'
                    #copied_label='Copied!',  # defaults to 'Copied!'
                    key='org_dash_url_copy',  # If omitted, a random key will be generated
                )
    
    with outer_col2:
        st.markdown("##### 📌 My Dashboard")
        with st.container(border=True):
            st.code(user_url, language=None)

            user_col1, user_col2 = st.columns([8, 2])    
            with user_col1: 
                st.markdown("**Copy URL:**")
            with user_col2: 
                copy_button(
                    user_url,
                    icon='material_symbols',  # default, use 'st' as alternative
                    #tooltip='Any tooltip text',  # defaults to 'Copy'
                    #copied_label='Copied!',  # defaults to 'Copied!'
                    key='my_dash_url_copy',  # If omitted, a random key will be generated
                )

    with outer_col3:
        st.markdown("##### 🤝 AI Working Group Dashboard")
        with st.container(border=True):
            st.code(wg_url, language=None)

            wg_col1, wg_col2 = st.columns([8, 2])
            with wg_col1: 
                st.markdown("**Copy URL:**")
            with wg_col2: 
                copy_button(
                    wg_url,
                    icon='material_symbols',  # default, use 'st' as alternative
                    #tooltip='Any tooltip text',  # defaults to 'Copy'
                    #copied_label='Copied!',  # defaults to 'Copied!'
                    key='wg_dash_url_copy',  # If omitted, a random key will be generated
                )

    # Instructions for adding calendar feed to external calendar apps
    st.markdown('')
    with st.expander("**How to add URLs to external calendar app**", icon="💡", expanded=False):
        st.markdown(
            """
            **Google Calendar**
            1. Copy the calendar URL.
            2. In Google Calendar, click the "+" button next to "Other calendars" on the left sidebar.
            3. Select "From URL".
            4. Paste the URL and click "Add calendar".

            **Apple Calendar (iOS)**
            1. Copy the calendar URL.
            2. Go to the Calendar app  on your Mac.
            3. Choose "File" > "New Calendar Subscription".
            4. Paste the URL, then click "Subscribe."

            For additional instructions from Apple, [see here.](https://support.apple.com/guide/calendar/subscribe-to-calendars-icl1022/mac)

            **Microsoft Outlook**
            1. Copy the calendar URL.
            2. Open your Outlook calendar, and on the Home tab, select "Add Calendar" > "From Internet".
            3. Paste the URL from your internet calendar and select OK.
            4. Outlook asks if you would like to add this calendar and subscribe to updates. Select Yes.

            For additional instructions from Microsoft,[see here.](https://support.microsoft.com/en-us/office/import-calendars-into-outlook-8e8364e1-400e-4c0f-a573-fe76b5a2d379)

            **Support**

            If you have any issues or need help, please contact us and we'd be happy to try to assist you:
            - Danya Sherbini, Lead Developer (danya@techequity.us)
            - Keirstan Schiedeck, Product Manager (keirstan@techequity.us)
            """
        )