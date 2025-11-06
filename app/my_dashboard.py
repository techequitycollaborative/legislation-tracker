#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My Dashboard
Created on Dec 2, 2024
@author: danyasherbini

Page to add bills to user's private dashboard
"""

import streamlit as st
import pandas as pd
from utils.aggrid_styler import draw_bill_grid
from utils.general import to_csv
from db.query import Query
from utils.my_dashboard import display_dashboard_details
from utils.bill_history import format_bill_history
from utils.profiling import profile

# Page title
st.title('📌 My Dashboard')
st.session_state.curr_page = "My Dashboard"

st.expander("About this page", icon="ℹ️", expanded=False).markdown(f"""
- Use this page to track bills relevant to you.
- Only you can view this page and all bills saved to it.
- To add bills to this dashboard, select a bill on the 📝 Bills page and then click the "Add to My Dashboard" button.
- To add custom advocacy details to a bill, go to your 🏢 Organization Dashboard. Custom advocacy details are viewable on this page, but editable only from your 🏢 Organization Dashboard.
""")

# Add space between expander and main content
st.markdown(" ")
st.markdown(" ")

# Ensure user info exists in the session (i.e. ensure the user is logged in)
if 'authenticated' not in st.session_state:
    st.error("User not authenticated. Please log in.")
    st.stop()  # Stop execution if the user is not authenticated

# Access user info
#user_info = st.session_state['user_info']
#user_email = st.session_state["user_info"].get("email")
user_email = st.session_state['user_email']
user_name = st.session_state['user_name']
first_name = user_name.split()[0]  # Get the first name for a more personal greeting

# Clear dashboard button
col1, col2 = st.columns([4, 1])
with col2:
    if st.button('Clear Dashboard', use_container_width=True, type='primary'):
        clear_q = f"""
            DELETE FROM public.user_bill_dashboard WHERE user_email = {user_email}
        """
        clear_success_msg = "User dashboard cleared."

        clear_query = Query(
            page_name="my_dashboard",
            query=clear_q,
            success_msg=clear_success_msg
        )

        clear_query.update_records()  # Actually remove the bills from the DB
        st.session_state.selected_bills = []
        st.session_state.dashboard_bills = pd.DataFrame()  # Clear in-memory DataFrame
        st.success('Dashboard cleared!')

# Initialize session state for dashboard bills
if 'dashboard_bills' not in st.session_state or st.session_state.dashboard_bills is None:
    st.session_state.dashboard_bills = pd.DataFrame()  # Initialize as empty DataFrame

@profile("my_dashboard.py - get_user_dashboard_data")
def get_user_dashboard_data():
    @st.cache_data
    def user_dashboard_cache():
        user_dashboard_q = f"""
            SELECT 
                b.openstates_bill_id,
                b.bill_number,
                b.bill_name,
                b.status,
                b.date_introduced,
                b.leg_session,
                b.author,
                b.coauthors, 
                b.chamber,
                b.leginfo_link,
                b.bill_text,
                b.bill_history,
                b.bill_event,
                b.event_text,
                b.assigned_topics,
                b.last_updated_on
            FROM public.bills_2025_2026 b
            LEFT JOIN public.user_bill_dashboard ubd
                ON ubd.openstates_bill_id = b.openstates_bill_id
            WHERE ubd.user_email = '{user_email}';
        """
        db_bills = Query(
            page_name="my_dashboard",
            query=user_dashboard_q
        ).fetch_records()

        # Update session state with user's dashboard bills
        #st.session_state.dashboard_bills = db_bills

        # Now remove timestamp from date_introduced and bill_event (for formatting purposes in other display areas)
        # KEEP AS Y-M-D FORMAT FOR AG GRID DATE FILTERING TO WORK
        db_bills['date_introduced'] = pd.to_datetime(db_bills['date_introduced']).dt.strftime('%Y-%m-%d') # Remove timestamp from date introduced
        db_bills['bill_event'] = pd.to_datetime(db_bills['bill_event']).dt.strftime('%Y-%m-%d') # Remove timestamp from bill_event
        db_bills['last_updated_on'] = pd.to_datetime(db_bills['last_updated_on']).dt.strftime('%Y-%m-%d') # Remove timestamp from last_updated_on

        # Minor data processing to match bills table
        # Wrangle assigned-topic string to a Python list for web app manipulation
        db_bills['bill_topic'] = db_bills['assigned_topics'].apply(lambda x: set(x.split("; ")) if x else ["Other"])
        db_bills = db_bills.drop(columns=['assigned_topics'])
        db_bills['bill_history'] = db_bills['bill_history'].apply(format_bill_history) #Format bill history

        # Default sorting: by upcoming bill_event
        db_bills = db_bills.sort_values(by='bill_event', ascending=False)
        return db_bills
    user_dashboard = user_dashboard_cache()
    return user_dashboard

db_bills = get_user_dashboard_data()
st.session_state.dashboard_bills = db_bills

# Mapping between user-friendly labels and internal theme values
theme_options = {
    'narrow': 'streamlit',
    'wide': 'alpine'
}

# Initialize session state for theme if not set
if 'theme' not in st.session_state:
    st.session_state.theme = 'streamlit'  # Default theme

# Reverse mapping to get the label from the internal value
label_from_theme = {v: k for k, v in theme_options.items()}

# Create a two-column layout
col1, col2, col3 = st.columns([1, 7, 2])
with col1:
    selected_label = st.selectbox(
        'Change grid theme:',
        options=list(theme_options.keys()),
        index=list(theme_options.keys()).index(label_from_theme[st.session_state.theme])
    )
    
with col2:    
    st.markdown("")

with col3:
    st.download_button(
            label='Download Data as CSV',
            data=to_csv(db_bills),
            file_name='my_bills.csv',
            mime='text/csv',
            use_container_width=True
        )

# Update session state if the user picks a new theme
selected_theme = theme_options[selected_label]
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme

# Use the persisted theme
theme = st.session_state.theme

if not db_bills.empty:
    total_db_bills = len(db_bills)
    st.markdown(f"#### {first_name}'s saved bills: {total_db_bills} total bills")
    data = draw_bill_grid(db_bills, theme=theme)

    # Display bill details for dashboard bills
    if 'selected_bills' not in st.session_state:
        st.session_state.selected_bills = []
        
    selected_rows = data.selected_rows

    if selected_rows is not None and len(selected_rows) != 0:
            display_dashboard_details(selected_rows)

elif db_bills.empty:
    st.write('No bills selected yet.')


