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
        st.session_state.status_filter = ""
    if 'author_filter' not in st.session_state:
        st.session_state.author_filter = []
    if 'bill_number_filter' not in st.session_state:
        st.session_state.bill_number_filter = ""
    if 'date_from_filter' not in st.session_state:
        st.session_state.date_from_filter = None
    if 'date_to_filter' not in st.session_state:
        st.session_state.date_to_filter = None
    if 'bill_name_filter' not in st.session_state:
        st.session_state.bill_name_filter = ""
    if 'keyword_filter' not in st.session_state:
        st.session_state.keyword_filter = ""    
    if 'org_position_filter' not in st.session_state:
        st.session_state.org_position_filter = []
    if 'assigned_to_filter' not in st.session_state:
        st.session_state.assigned_to_filter = []     
    


def clear_filters():
    """
    Callback function to clear all filter values
    """
    st.session_state.topic_filter = []
    st.session_state.status_filter = ""
    st.session_state.author_filter = []
    st.session_state.bill_number_filter = ""
    st.session_state.date_from_filter = None
    st.session_state.date_to_filter = None
    st.session_state.bill_name_filter = ""
    st.session_state.keyword_filter = ""
    st.session_state.org_position_filter = []
    st.session_state.assigned_to_filter = []


def display_bill_filters(bills_df, 
                        show_bill_number=True,
                        show_bill_name=True,
                        show_status=True,
                        show_topic=True,
                        show_author=True,
                        show_date_filters=True,
                        show_keyword_search=True,
                        show_org_position=False,
                        show_assigned_to=False):
    """
    Display filter UI components for bills
    
    Args:
        bills_df: DataFrame containing bills data
        show_bill_number: Whether to show bill number filter (default: True)
        show_bill_name: Whether to show bill name filter (default: True)
        show_status: Whether to show status filter (default: True)
        show_topic: Whether to show topic filter (default: True)
        show_author: Whether to show author filter (default: True)
        show_date_filters: Whether to show date range filters (default: True)
        show_keyword_search: Whether to show keyword search (default: True)
        show_org_position: Whether to show org position filter (default: False)
        show_assigned_to: Whether to show assigned to filter (default: False)
    
    Returns:
        dict: Dictionary containing all filter values with keys matching filter names
    """
    
    # Initialize all filter values
    bill_number_search = ""
    bill_name_search = ""
    status_search = ""
    selected_topics = []
    selected_authors = []
    date_from = None
    date_to = None
    keyword_search = ""
    selected_org_positions = []
    selected_assigned_to = []
    
    # Collect all filters in order
    all_filters = []
    
    if show_bill_number:
        all_filters.append('bill_number')
    if show_bill_name:
        all_filters.append('bill_name')
    if show_status:
        all_filters.append('status')
    if show_topic:
        all_filters.append('topic')
    if show_date_filters:
        all_filters.append('date_from')
        all_filters.append('date_to')
    if show_author:
        all_filters.append('author')
    if show_keyword_search:
        all_filters.append('keyword')
    if show_org_position:
        all_filters.append('org_position')
    if show_assigned_to:
        all_filters.append('assigned_to')
    
    # Calculate number of rows needed (3 filters per row)
    filters_per_row = 3
    num_filters = len(all_filters)
    
    if num_filters == 0:
        return {
            'selected_topics': selected_topics,
            'status_search': status_search,
            'selected_authors': selected_authors,
            'bill_number_search': bill_number_search,
            'bill_name_search': bill_name_search,
            'date_from': date_from,
            'date_to': date_to,
            'keyword_search': keyword_search,
            'selected_org_positions': selected_org_positions,
            'selected_assigned_to': selected_assigned_to,
        }
    
    # Display filters in rows of 3
    filter_idx = 0
    while filter_idx < num_filters:
        # Get filters for this row (up to 3)
        row_filters = all_filters[filter_idx:filter_idx + filters_per_row]
        
        # Create 3 columns
        cols = st.columns(3)
        
        # Display each filter in this row
        for col_idx, filter_type in enumerate(row_filters):
            with cols[col_idx]:
                if filter_type == 'bill_number':
                    bill_number_search = st.text_input(
                        "Bill Number:",
                        placeholder="ex: AB 123",
                        key="bill_number_filter"
                    )
                elif filter_type == 'bill_name':
                    bill_name_search = st.text_input(
                        "Bill Name:",
                        placeholder="Search bill name...",
                        key="bill_name_filter"
                    )
                elif filter_type == 'status':
                    status_search = st.text_input(
                        "Bill Status:",
                        placeholder="ex: Introduced",
                        key="status_filter"
                    )
                elif filter_type == 'topic':
                    # Get unique topics
                    unique_topics = list(topic_config.keys())
                    unique_topics.append("Other")
                    selected_topics = st.multiselect(
                        "Bill Topic:",
                        options=unique_topics,
                        key="topic_filter"
                    )
                elif filter_type == 'date_from':
                    date_from = st.date_input(
                        "Introduced From:",
                        value=None,
                        key="date_from_filter"
                    )
                elif filter_type == 'date_to':
                    date_to = st.date_input(
                        "Introduced To:",
                        value=None,
                        key="date_to_filter"
                    )
                elif filter_type == 'author':
                    # Get unique list of authors and sort alphabetically
                    unique_authors = bills_df['author'].dropna().unique().tolist()
                    unique_authors.sort()

                    selected_authors = st.multiselect(
                        "Author(s):",
                        options=unique_authors,
                        key="author_filter"
                    )
                elif filter_type == 'keyword':
                    keyword_search = st.text_input(
                        "Keyword Search:",
                        placeholder="ex: artificial intelligence",
                        key="keyword_filter"
                    )
                elif filter_type == 'org_position':
                    # Get unique list of org positions
                    unique_positions = bills_df['org_position'].dropna().unique().tolist()

                    selected_org_positions = st.multiselect(
                        "Org Position:",
                        options=unique_positions,
                        key="org_position_filter",
                        help="Only existing values appear in this dropdown. Dropdown options update based on new data entered in Custom Advocacy Details."
                    )
                elif filter_type == 'assigned_to':
                    # Get unique list of assigned to
                    unique_assigned_to = bills_df['assigned_to'].dropna().unique().tolist()

                    selected_assigned_to = st.multiselect(
                        "Assigned To:",
                        options=unique_assigned_to,
                        key="assigned_to_filter",
                        help="Only existing values appear in this dropdown. Dropdown options update based on new data entered in Custom Advocacy Details."
                    )
        
        filter_idx += filters_per_row
    
    # Clear filters button
    st.button("🔄 Clear All Filters", on_click=clear_filters)
    
    st.markdown("---")

    # Return as dictionary for easier handling
    return {
        'selected_topics': selected_topics,
        'status_search': status_search,
        'selected_authors': selected_authors,
        'bill_number_search': bill_number_search,
        'bill_name_search': bill_name_search,
        'date_from': date_from,
        'date_to': date_to,
        'keyword_search': keyword_search,
        'selected_org_positions': selected_org_positions,
        'selected_assigned_to': selected_assigned_to,
    }


def apply_bill_filters(bills_df, 
                       selected_topics=None, 
                       status_search=None, 
                       selected_authors=None, 
                       bill_number_search=None, 
                       bill_name_search=None, 
                       date_from=None, 
                       date_to=None, 
                       keyword_search=None,
                       selected_org_positions=None,
                       selected_assigned_to=None,
                       filter_dict=None):
    """
    Apply filters to bills dataframe
    
    Args:
        bills_df: DataFrame to filter
        selected_topics: List of selected topics
        status_search: Status search string
        selected_authors: List of selected authors
        bill_number_search: Bill number search string
        bill_name_search: Bill name search string
        date_from: Start date for introduced date range
        date_to: End date for introduced date range
        keyword_search: General keyword search string
        selected_org_positions: List of selected org positions
        selected_assigned_to: List of selected assigned to
        filter_dict: Optional dictionary containing all filters (returned from display_bill_filters)
                    If provided, individual parameters are ignored
    
    Returns:
        DataFrame: Filtered bills dataframe
    """
    filtered_bills = bills_df.copy()
    
    # If filter_dict is provided, use it instead of individual parameters
    if filter_dict is not None:
        selected_topics = filter_dict.get('selected_topics')
        status_search = filter_dict.get('status_search')
        selected_authors = filter_dict.get('selected_authors')
        bill_number_search = filter_dict.get('bill_number_search')
        bill_name_search = filter_dict.get('bill_name_search')
        date_from = filter_dict.get('date_from')
        date_to = filter_dict.get('date_to')
        keyword_search = filter_dict.get('keyword_search')
        selected_org_positions = filter_dict.get('selected_org_positions')
        selected_assigned_to = filter_dict.get('selected_assigned_to')
    
    # Topic filter
    if selected_topics:
        filtered_bills = filtered_bills[
            filtered_bills['bill_topic'].apply(
                lambda topics: any(topic in topics for topic in selected_topics)
            )
        ]
    
    # Status filter (text search)
    if status_search:
        filtered_bills = filtered_bills[
            filtered_bills['status'].str.contains(status_search, case=False, na=False)
        ]
    
    # Author filter
    if selected_authors:
        filtered_bills = filtered_bills[filtered_bills['author'].isin(selected_authors)]
    
    # Bill number filter
    if bill_number_search:
        filtered_bills = filtered_bills[
            filtered_bills['bill_number'].str.contains(bill_number_search, case=False, na=False)
        ]
    
    # Bill name filter
    if bill_name_search:
        filtered_bills = filtered_bills[
            filtered_bills['bill_name'].str.contains(bill_name_search, case=False, na=False)
        ]
    
    # Introduced date filters
    if date_from:
        filtered_bills = filtered_bills[
            pd.to_datetime(filtered_bills['date_introduced']) >= pd.to_datetime(date_from)
        ]
    
    if date_to:
        filtered_bills = filtered_bills[
            pd.to_datetime(filtered_bills['date_introduced']) <= pd.to_datetime(date_to)
        ]
    
    # Keyword search across all columns
    if keyword_search:
        # Create a mask that checks if the keyword appears in any column
        mask = filtered_bills.apply(
            lambda row: row.astype(str).str.contains(keyword_search, case=False, na=False).any(), 
            axis=1
        )
        filtered_bills = filtered_bills[mask]
    
    # Org position filter
    if selected_org_positions and 'org_position' in filtered_bills.columns: # Make sure org_position column exists
        filtered_bills = filtered_bills[filtered_bills['org_position'].isin(selected_org_positions)]

    # Assigned to filter
    if selected_assigned_to and 'assigned_to' in filtered_bills.columns: # Make sure assigned_to column exists
        filtered_bills = filtered_bills[filtered_bills['assigned_to'].isin(selected_assigned_to)]
    
    return filtered_bills


def display_bills_table(df):
    """
    Display bills dataframe using Streamlit's dataframe component
    """
    # Get unique topics
    unique_topics = list(topic_config.keys())
    unique_topics.append("Other")

    # Create a copy of the df
    display_df = df.copy()

    column_config = {
        "bill_number": st.column_config.Column(
            "Bill Number",
            #pinned=True, # Can pin the column, but not really necessary since the df is not that wide. Pinning also greys the text
        ),

        "bill_name": st.column_config.Column(
            "Bill Name",
            help="The bill's official name.",  
        ),

        "date_introduced": st.column_config.DateColumn(
            "Date Introduced",
            help="The date the bill was introduced in the legislature.",  
        ),

        "status": st.column_config.Column(
            "Status",
            help="The bill's most recent status.",  
        ),

        "last_updated_on": st.column_config.Column(
            "Last Updated",
            help="The date the bill data was last updated on LegInfo.",  
        ),

        "author": st.column_config.Column(
            "Author",
            help="The bill's primary author. Select a bill to view co-authors.",  
        ),

        "bill_topic": st.column_config.MultiselectColumn(
                            "Topic(s)",
                            help="Primary topics of the bill, as assigned by TechEquity.",
                            options=unique_topics,
                            color="auto",
                            width="large",
                        ),

        "bill_event": st.column_config.DateColumn(
            "Upcoming Hearing",
            help="The date of the bill's next scheduled event (committee hearing, floor session, etc.).",  
        ),

        # Config for hidden columns -- these columns only show up in bill details, but user can add them to the display dataframe by clicking the eye icon
        "leg_session": st.column_config.Column(
            "Legislative Session",
            help="The legislative session the bill belongs to.",
        ),

        "coauthors": st.column_config.Column(
            "Co-Authors",
            help="The bill's co-authors.",
        ),

        "chamber": st.column_config.Column(
            "Chamber",
            help="The legislative chamber the bill was introduced in (Assembly or Senate).",
        ),

        "leginfo_link": st.column_config.Column(
            "LegInfo Link",
            help="Link to the bill's page on LegInfo.",
        ),

        "bill_text": st.column_config.Column(
            "Bill Text",
            help="An excerpt from the bill's text.",
        ),

        "bill_history": st.column_config.Column(
            "Bill History",
            help="Chronological history of bill updates and status changes.",
        ),

        "event_text": st.column_config.Column(
            "Upcoming Event Location",
            help="The location of the bill's upcoming event (for ex: committee name).",
        ),

    }

    # Config for custom advocacy details columns, if they exist (ONLY FOR ORG DASHBOARD)
    if 'org_position' in display_df.columns:
        column_config["org_position"] = st.column_config.Column(
            "Org Position",
            help="Your organization's position on this bill.",
        )
    
    if 'assigned_to' in display_df.columns:
        column_config["assigned_to"] = st.column_config.Column(
            "Assigned To",
            help="Team member assigned to track this bill.",
        )

    # Build column order dynamically
    column_order = ['bill_number', 'author', 'bill_name', 'date_introduced', 'status', 'last_updated_on', 'bill_topic']
    
    # Add custom advocacy details columns to the order if they exist
    if 'org_position' in display_df.columns:
        column_order.append('org_position')
    
    if 'assigned_to' in display_df.columns:
        column_order.append('assigned_to')

    data = st.dataframe(
        display_df,
        #width="stretch",
        #height="auto",
        hide_index=True,
        key="bills_table",
        selection_mode='single-row',
        on_select="rerun",
        column_config=column_config,
        column_order=column_order,
    )
    return data