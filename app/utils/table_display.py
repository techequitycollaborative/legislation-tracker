#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for displaying tables and filters for Streamlit dataframes
"""

import streamlit as st
import pandas as pd
from utils.general import topic_config


def initialize_filter_state():
    """
    Initialize session state for all filters
    """
    if 'topic_filter' not in st.session_state:
        st.session_state.topic_filter = []
    if 'status_filter' not in st.session_state:
        st.session_state.status_filter = []
    if 'author_filter' not in st.session_state:
        st.session_state.author_filter = ""
    if 'bill_number_filter' not in st.session_state:
        st.session_state.bill_number_filter = ""
    if 'date_from_filter' not in st.session_state:
        st.session_state.date_from_filter = None
    if 'date_to_filter' not in st.session_state:
        st.session_state.date_to_filter = None


def clear_filters():
    """
    Callback function to clear all filter values
    """
    st.session_state.topic_filter = []
    st.session_state.status_filter = []
    st.session_state.author_filter = ""
    st.session_state.bill_number_filter = ""
    st.session_state.date_from_filter = None
    st.session_state.date_to_filter = None


def display_bill_filters(bills_df, show_date_filters=True):
    """
    Display filter UI components for bills
    
    Args:
        bills_df: DataFrame containing bills data
        show_date_filters: Whether to show date range filters (default: True)
    
    Returns:
        tuple: (selected_topics, selected_statuses, author_search, bill_number_search, date_from, date_to)
    """
    # Get unique topics
    unique_topics = list(topic_config.keys())
    unique_topics.append("Other")
    
    # Display filters    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        selected_topics = st.multiselect(
            "Filter by Topic(s):",
            options=unique_topics,
            key="topic_filter"
        )
    
    with filter_col2:
        all_statuses = bills_df['status'].unique().tolist()
        selected_statuses = st.multiselect(
            "Filter by Status:",
            options=all_statuses,
            key="status_filter"
        )
    
    with filter_col3:
        author_search = st.text_input(
            "Search Author:",
            placeholder="Enter author name...",
            key="author_filter"
        )
    
    # Additional filters row
    if show_date_filters:
        filter_col4, filter_col5, filter_col6 = st.columns(3)
        
        with filter_col4:
            bill_number_search = st.text_input(
                "Search Bill Number:",
                placeholder="e.g., AB 123",
                key="bill_number_filter"
            )
        
        with filter_col5:
            date_from = st.date_input(
                "Introduced From:",
                value=None,
                key="date_from_filter"
            )
        
        with filter_col6:
            date_to = st.date_input(
                "Introduced To:",
                value=None,
                key="date_to_filter"
            )
    else:
        bill_number_search = st.text_input(
            "Search Bill Number:",
            placeholder="e.g., AB 123",
            key="bill_number_filter"
        )
        date_from = None
        date_to = None
    
    # Clear filters button
    st.button("🔄 Clear All Filters", on_click=clear_filters)
    
    st.markdown("---")

    return selected_topics, selected_statuses, author_search, bill_number_search, date_from, date_to


def apply_bill_filters(bills_df, selected_topics, selected_statuses, author_search, 
                       bill_number_search, date_from, date_to):
    """
    Apply filters to bills dataframe
    
    Args:
        bills_df: DataFrame to filter
        selected_topics: List of selected topics
        selected_statuses: List of selected statuses
        author_search: Author search string
        bill_number_search: Bill number search string
        date_from: Start date for date range
        date_to: End date for date range
    
    Returns:
        DataFrame: Filtered bills dataframe
    """
    filtered_bills = bills_df.copy()
    
    # Topic filter
    if selected_topics:
        filtered_bills = filtered_bills[
            filtered_bills['bill_topic'].apply(
                lambda topics: any(topic in topics for topic in selected_topics)
            )
        ]
    
    # Status filter
    if selected_statuses:
        filtered_bills = filtered_bills[filtered_bills['status'].isin(selected_statuses)]
    
    # Author filter
    if author_search:
        filtered_bills = filtered_bills[
            filtered_bills['author'].str.contains(author_search, case=False, na=False)
        ]
    
    # Bill number filter
    if bill_number_search:
        filtered_bills = filtered_bills[
            filtered_bills['bill_number'].str.contains(bill_number_search, case=False, na=False)
        ]
    
    # Date filters
    if date_from:
        filtered_bills = filtered_bills[
            pd.to_datetime(filtered_bills['date_introduced']) >= pd.to_datetime(date_from)
        ]
    
    if date_to:
        filtered_bills = filtered_bills[
            pd.to_datetime(filtered_bills['date_introduced']) <= pd.to_datetime(date_to)
        ]
    
    return filtered_bills


def display_bills_table(df):
    """
    Display bills dataframe using Streamlit's dataframe component
    """
    # Get unique topics
    unique_topics = list(topic_config.keys())
    unique_topics.append("Other")

    data = st.dataframe(
        df,
        #width="stretch",
        #height="auto",
        hide_index=True,
        key="bills_table",
        selection_mode='single-row',
        on_select="rerun",
        column_config={
            "bill_number": "Bill Number",
            "bill_name": "Bill Name",
            "date_introduced": "Date Introduced",
            "status": "Status",
            "last_updated_on": "Last Updated",
            "author": "Author",
            "bill_topic": st.column_config.MultiselectColumn(
                            "Topic(s)",
                            help="The categories of the app",
                            options=unique_topics,
                            color="auto",
                        ),
            #"bill_event": "Most Recent Event Date", # Hiding bill_event for now, but it's still accessible like the other hidden columns are
        },
        column_order=['bill_number', 'bill_name', 'date_introduced', 'status', 'last_updated_on', 'author', 'bill_topic'],
    )
    return data