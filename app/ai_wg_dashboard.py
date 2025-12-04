#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_wg_dashboard.py
Created on July 10, 2025

AI Working Group Dashboard
"""

import streamlit as st
import pandas as pd
from utils.aggrid_styler import draw_bill_grid
from db.query import (
    get_working_group_bills,
    get_discussion_comments,
    save_comment,
    get_ai_members,
    get_all_custom_bill_details
)
from utils.bill_history import format_bill_history
from utils.general import to_csv
from utils.ai_working_group import display_working_group_bill_details
from utils.css_utils import load_css_with_fallback, DEFAULT_FALLBACK_CSS
from utils.profiling import timer, profile, show_performance_metrics, track_rerun, track_event
from utils.table_display import initialize_filter_state, display_bill_filters, apply_bill_filters, display_bills_table

track_rerun("AI Working Group Dashboard")
#################################### PAGE SETUP ####################################

# Load custom CSS with fallback
load_css_with_fallback(
    primary_css='styles/ai_working_group.css',
    fallback_css=DEFAULT_FALLBACK_CSS
)

#### Page title and description ###
st.markdown("""
<div class="main-header">
    <h1>AI Working Group Dashboard</h1>
</div>
""", unsafe_allow_html=True)

st.expander("ℹ️ About this page", expanded=False).markdown("""
- Use this page to track bills as a working group.
- To add a bill to this dashboard, select a bill on the 📝 Bills page and then click the "Add to AI Working Group Dashboard" button.
- Only approved and logged in members of the AI Working Group can view this page and add bills to it.                                                        
""")

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")

### Authentication and user info ###
# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'authenticated' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Access user info
user_email = st.session_state['user_email']
user_name = st.session_state['user_name']
first_name = user_name.split()[0] # get first name from user name

# Initialize session state for dashboard bills
if 'working_group_bills' not in st.session_state or st.session_state['working_group_bills'] is None:
    st.session_state['working_group_bills'] = pd.DataFrame()

# Initialize session state for filters
initialize_filter_state()


############################# FETCH BILLS ###########################################

# Load bills data for the dashboard
@profile("DB - Fetch AI WG DASHBOARD table data")
@st.cache_data(show_spinner="Loading your dashboard...", ttl=30) # Cache dashboard data and refresh every 30 seconds
def load_ai_dashboard_table():
    # Fetch the user's saved bills from the database
    wg_bills = get_working_group_bills()

    # Process bills data if not empty
    if not wg_bills.empty:
        # Now remove timestamp from date_introduced and bill_event (for formatting purposes in other display areas)
        
        # KEEP AS Y-M-D FORMAT FOR AG GRID DATE FILTERING TO WORK
        wg_bills['date_introduced'] = pd.to_datetime(wg_bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestamp from date introduced
        wg_bills['bill_event'] = pd.to_datetime(wg_bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
        wg_bills['last_updated_on'] = pd.to_datetime(wg_bills['last_updated_on']).dt.strftime('%Y-%m-%d') # Remove timestamp from last_updated_on

        # Minor data processing to match bills table
        # wg_bills = get_bill_topics_multiple(wg_bills, keyword_dict= keyword_to_topics, keyword_regex=global_keyword_regex)  # Get bill topics
        # Wrangle assigned-topic string to a Python list for web app manipulation
        wg_bills['bill_topic'] = wg_bills['assigned_topics'].apply(lambda x: set(x.split("; ")) if x else ["Other"])
        wg_bills = wg_bills.drop(columns=['assigned_topics'])

        wg_bills['bill_history'] = wg_bills['bill_history'].apply(format_bill_history) #Format bill history

        # Default sorting: by upcoming bill_event
        wg_bills = wg_bills.sort_values(by='bill_event', ascending=False)
    
    return wg_bills

# TODO: unify with session_state storage of data, not page variable
wg_bills = load_ai_dashboard_table()


############################## HEADER SECTION ##############################

# Key metrics row to show total bills, recent updates, members, and letters of support
st.markdown('<h3 class="section-header">Overview</h3>', unsafe_allow_html=True)
metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

with metrics_col1:
    total_bills = len(wg_bills) if not wg_bills.empty else 0
    st.metric("📊 Total Bills", total_bills)

with metrics_col2:
    # Get bills updates today
    #recent_bills_count = len(wg_bills[wg_bills['last_updated_on'] >= pd.Timestamp.now().strftime('%Y-%m-%d')]) if not wg_bills.empty else 0
    
    # Get bills updated in the last 7 days
    # TODO: move to loading function, or a metrics function
    recent_bills_count = len(wg_bills[wg_bills['last_updated_on'] >= (pd.Timestamp.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')]) if not wg_bills.empty else 0
    
    st.metric("🕒 Bills Updated This Week", recent_bills_count)

with metrics_col3:
    # TODO: move to loading function, or a metrics function
    ai_members = get_ai_members()
    member_count = len(ai_members) if not ai_members.empty else 0
    st.metric("👥 Working Group Members", member_count)

with metrics_col4:
    # TODO: move to loading function, or a metrics function
    custom_details = pd.DataFrame(get_all_custom_bill_details())
    letters_count = 0
    if not custom_details.empty and 'letter_of_support' in custom_details.columns:
        letters_count = len(custom_details[
            pd.notna(custom_details['letter_of_support']) &
            custom_details['letter_of_support'].str.startswith("http")
        ])
    st.metric("📄 Letters Available", letters_count)

# Add space
st.markdown(" ")

############################## TABS SECTION ##############################
# Tabs for different sections
st.markdown('<h3 class="section-header">Working Group Info</h3>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🕒 Recently Updated Bills", "📄 Letters", "👥 Working Group Members",])

############################## Recently Updated Bills ##############################
with tab1:
    st.markdown(" ")
    if not wg_bills.empty:
        recent_bills = wg_bills.sort_values(by='last_updated_on', ascending=False).head(8)
        # Display recent bills -- rows of 4 columns each
        bills_list = list(recent_bills.iterrows())
        for i in range(0, len(bills_list), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(bills_list):
                    _, bill = bills_list[i + j]
                    with cols[j]:
                        # Build the upcoming event bullet point if data exists
                        #if (pd.notna(bill['bill_event']) and bill['bill_event'] and 
                        #    pd.notna(bill['event_text']) and bill['event_text']):
                        #    upcoming_event = f"<strong>Upcoming Event:</strong> <br>{bill['event_text']} - {bill['bill_event']}"
                        #else: 
                        #    upcoming_event = "<strong>Upcoming Event:</strong> None"
                        
                        # Create the complete HTML for the card
                        card_html = f"""
                        <div class="bill-card">
                            <h4>{bill['bill_number']}</h4>
                            <p>{bill['bill_name']}</p>
                            <ul>
                                <li><strong>Last Updated:</strong> {bill['last_updated_on']}</li>
                                <li><strong>Status:</strong> {bill['status']}</li>
                            </ul>
                        </div>
                        """
                        
                        st.markdown(card_html, unsafe_allow_html=True)
                    
    else:
        st.markdown("""
        <div class="info-card">
            <p>No bills have been added to the working group yet.</p>
        </div>
        """, unsafe_allow_html=True)

############################## Letters of Support ##############################

with tab2:
    st.markdown(" ")

    # Load custom bill details from all orgs
    custom_details = pd.DataFrame(get_all_custom_bill_details())

    if custom_details.empty or 'letter_of_support' not in custom_details.columns:
        st.info("No letters available.")
    else:
        # Filter only rows with valid links
        valid_letters = custom_details[
            pd.notna(custom_details['letter_of_support']) &
            custom_details['letter_of_support'].str.startswith("http")
        ]

        if valid_letters.empty:
            st.info("No valid letter links found.")
        else:
            # Group by bill_number and display
            grouped = valid_letters.groupby("bill_number")

            for bill_number, group in grouped:
                st.markdown(f"**{bill_number}**")
                for _, row in group.iterrows():
                    org_name = row.get("last_updated_org_name", "Unknown Org")
                    letter_link = row["letter_of_support"]
                    st.markdown(f"- [{org_name}'s Letter of Support]({letter_link})")
                st.markdown("---")

############################## Working Group Members ##############################

with tab3:
    st.markdown(" ")

    ai_members = get_ai_members()

    def filter_ai_members(df):
        # Create filter controls in columns at the top
        filter_col1, filter_col2, _ = st.columns([3, 3, 1])  # last col is just for spacing
        
        with filter_col1:
            member_filter = st.text_input(
                "Filter by Name",
                placeholder="Type to search..."
            )

        with filter_col2:
            org_filter = st.multiselect(
                "Filter by Organization",
                options=sorted(df['org_name'].dropna().unique()),
                default=[],
                placeholder="All organizations"
            )
        
        # Apply filters
        filtered_df = df.copy()

        if member_filter:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(member_filter, case=False, na=False)
            ]
        if org_filter:
            filtered_df = filtered_df[
                filtered_df['org_name'].isin(org_filter)
            ]

        return filtered_df


    if ai_members.empty:
        st.info("No working group members found.")
    else:
        filtered_members = filter_ai_members(ai_members)
        st.data_editor(
            filtered_members,
            use_container_width=True,
            column_config={
                "name": st.column_config.Column("Name"),
                "email": st.column_config.Column("Email"),
                "org_name": st.column_config.Column("Organization"),
            },
            hide_index=True,
            disabled=True  # Table is not editable
        )


############################## Bill Selection & Details ##############################
# Add space
st.markdown(" ")

st.markdown('<h3 class="section-header">Bill Tracking</h3>', unsafe_allow_html=True)
st.markdown("Select a bill to view more details.")

############################ FILTERS #############################
# Display filters and get filter values
filter_values = display_bill_filters(wg_bills, show_date_filters=True)
selected_topics, selected_statuses, selected_authors, bill_number_search, date_from, date_to = filter_values

# Apply filters
filtered_bills = apply_bill_filters(
    wg_bills, 
    selected_topics, 
    selected_statuses, 
    selected_authors, 
    bill_number_search, 
    date_from, 
    date_to
)

# Update total bills count
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    total_bills = len(filtered_bills)
    st.markdown(f"#### Total bills: {total_bills:,}")
    if len(filtered_bills) < len(wg_bills):
        st.caption(f"(filtered from {len(wg_bills):,} total)")

###############################################################

with st.container(key='dashboard_bills_table_container'):
    if not wg_bills.empty:
        with timer("AI working group dashboard - draw streamlit df"):
            data = display_bills_table(filtered_bills)

        # Assign variable to selection property
        selected = data.selection

        # Access selected rows
        if selected != None and selected.rows:
            track_event("Row selected")
            selected_index = selected.rows[0]  # Get first selected row index
            selected_bill_data = filtered_bills.iloc[[selected_index]]  # Double brackets to keep as DataFrame for display function
            display_working_group_bill_details(selected_bill_data)

    elif wg_bills.empty:
        st.write('No bills added yet.')



