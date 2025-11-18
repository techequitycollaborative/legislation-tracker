#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/committees.py
@author: jessica wang

Utility function for displaying committee details on the Committees page.

"""

import streamlit as st
import pandas as pd
from db.query import COMMITTEE_COLUMNS


def display_committee_info_text(selected_rows):
    '''
    Displays committee information as markdown text when a row is selected in
    an Ag Grid data frame.
    '''
    # Ensure values align with expected order of COMMITTEE_COLUMNS, which is necessary for proper db querying
    assert selected_rows.columns.tolist() == COMMITTEE_COLUMNS 

    # Extract the values from the selected row, even unused
    committee_name = selected_rows['committee_name'].iloc[0]
    chamber = selected_rows['chamber'].iloc[0]
    next_hearing = selected_rows['next_hearing'].iloc[0]
    committee_chair = selected_rows['committee_chair'].iloc[0]
    committee_vice_chair = selected_rows['committee_vice_chair'].iloc[0]
    total_members = selected_rows['total_members'].iloc[0]
    webpage_link = selected_rows['webpage_link'].iloc[0]
    committee_members = selected_rows['committee_members'].iloc[0]
    member_count = selected_rows['member_count'].iloc[0]
    
    # Display Bill Info Below the Table
    st.markdown('### Committee Details')
    st.divider()
    
    # Container with committee name
    with st.container(key='title_button_container'):
        col1, col2 = st.columns([7, 3])  # Adjust column widths as needed
        with col1:
            st.markdown(f'### {committee_name}')
    
    # Add empty rows of space  
    st.write("")
    st.write("")

    # Container for committee details
    with st.container(key='main_details_container'):
        # Display columns with spacers
        col1, col2, col3, col4, col5 = st.columns([6, 1, 4, 1, 4])
        with col1:
            st.markdown('##### Chamber')
            st.markdown(chamber)
            
            st.markdown('')

            st.markdown('##### Chair')
            st.markdown(committee_chair)

            st.markdown('')

            st.markdown('##### Vice Chair')
            st.markdown(committee_vice_chair)

            st.markdown('')

        with col2:
            st.markdown('')
        
        with col3:
            st.markdown('##### Next Hearing')
            if next_hearing is not None and next_hearing != "*No upcoming hearing scheduled*" and pd.to_datetime(next_hearing, errors='coerce') > pd.Timestamp.today():
                st.markdown(next_hearing)
            else:
                st.markdown('*No upcoming hearings*')

            st.markdown('')

            st.markdown('##### Member(s)')
            if committee_members is not None:
                st.markdown(f"*{member_count} in total, {total_members} including chairs*")
                st.markdown(committee_members)
            else:
                st.markdown('*None assigned*')
        
        with col4:
            st.markdown('')
        
        with col5:
            st.markdown('##### Link to Homepage')
            st.link_button(f'{chamber.lower()}.ca.gov', str(webpage_link))


#################### FUNCTIONS FOR MAIN COMMITTEES TABLE -- STREAMLIT TABLE + FILTERS ####################

def initialize_filter_state():
    """
    Initialize session state for all filters
    """
    if 'name_filter' not in st.session_state:
        st.session_state.name_filter = []
    if 'chamber_filter' not in st.session_state:
        st.session_state.chamber_filter = None
    if 'hearing_filter' not in st.session_state:
        st.session_state.hearing_filter = None
    if 'chairperson_filter' not in st.session_state:
        st.session_state.chairperson_filter = ""
    if 'vice_chairperson_filter' not in st.session_state:
        st.session_state.vice_chairperson_filter = ""

def clear_filters():
    """
    Callback function to clear all filter values
    """
    st.session_state.name_filter = []
    st.session_state.chamber_filter = None
    st.session_state.hearing_filter = None
    st.session_state.chairperson_filter = ""
    st.session_state.vice_chairperson_filter = ""


def display_committee_filters(df):
    """
    Display filter UI components for committees page
    
    Args:
        df: DataFrame containing committees data
    
    Returns:
        tuple: (selected_name, selected_chamber, hearing_search, chairperson_search, vice_chairperson_search)
    """
 
    # Display filters    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        unique_committees = df['committee_name'].dropna().unique().tolist()
        unique_committees.sort()
        selected_name = st.multiselect(
            "Filter by Committee:",
            options=unique_committees,
            key="committee_filter"
        )
    
    with filter_col2:
        # Get unique chambers
        unique_chambers = df['chamber'].dropna().unique().tolist()
        unique_chambers.sort()
        selected_chamber = st.selectbox(
            "Filter by Chamber:",
            options=unique_chambers,
            key="chamber_filter",
            #format_func=lambda x: "All Chambers" if x is None else x
        )
    
    with filter_col3:
        hearing_search = st.date_input(
            "Upcoming Hearing Date:",
            value=None,
            key="hearing_filter"
            )
    
    # Second row of filters
    filter_col4, filter_col5, filter_col6 = st.columns(3)

    with filter_col4:
        chairperson_search = st.text_input(
            "Filter by Chairperson:",
            key="chairperson_filter"
        )
    
    with filter_col5:
        vice_chairperson_search = st.text_input(
            "Filter by Vice Chairperson:",
            key="vice_chairperson_filter"
        )

    with filter_col5:
        st.markdown("")  # Empty for alignment
    
    # Clear filters button
    st.button("🔄 Clear All Filters", on_click=clear_filters)
    
    st.markdown("---")

    return selected_name, selected_chamber, hearing_search, chairperson_search, vice_chairperson_search


def apply_committee_filters(df, selected_name, selected_chamber, hearing_search, chairperson_search, vice_chairperson_search):
    """
    Apply filters to committese dataframe
    
    Args:
        df: DataFrame to filter
        selected_name: Committee name selection
        selected_chamber: Chamber selection
        hearing_search: Hearing date search
        chairperson_search: Chairperson name search
        vice_chairperson_search: Vice Chairperson name search
    
    Returns:
        DataFrame: Filtered committees dataframe
    """
    filtered_committees = df.copy()
    
    # Name filter (case-insensitive partial match)
    if selected_name:
        filtered_committees = filtered_committees[filtered_committees['committee_name'].isin(selected_name)]
    
    # Chamber filter
    if selected_chamber:
        filtered_committees = filtered_committees[filtered_committees['chamber'] == selected_chamber]

    # Hearing date filter
    if hearing_search:
        filtered_committees = filtered_committees[
            pd.to_datetime(filtered_committees['next_hearing'], errors='coerce').dt.date == hearing_search
        ]

    # Chairperson filter (case-insensitive partial match)
    if chairperson_search:
        filtered_committees = filtered_committees[
            filtered_committees['committee_chair'].str.contains(chairperson_search, case=False, na=False)
        ]

    # Vice Chairperson filter (case-insensitive partial match)
    if vice_chairperson_search:
        filtered_committees = filtered_committees[
            filtered_committees['committee_vice_chair'].str.contains(vice_chairperson_search, case=False, na=False)
        ]
    
    return filtered_committees


def display_committee_table(df):
    """
    Display committees dataframe using Streamlit's dataframe component
    """
    # Create a copy of the df
    display_df = df.copy()

    column_config = {
        "committee_name": st.column_config.Column(
            "Committee Name",
        ),

        "chamber": st.column_config.Column(
            "Chamber",
        ),

        "party": st.column_config.Column(
            "Party",
        ),

        "next_hearing": st.column_config.Column(
            "Next Hearing",
            help="Date of the committee's next scheduled hearing, if available.",
        ),

        "committee_chair": st.column_config.Column(
            "Chairperson",
        ),

        "committee_vice_chair": st.column_config.Column(
            "Vice Chairperson",
        ),

    }

    data = st.dataframe(
        display_df,
        #width="stretch",
        #height="auto",
        hide_index=True,
        key="committee_table",
        selection_mode='single-row',
        on_select="rerun",
        column_config=column_config,
        column_order=['committee_name', 'chamber', 'next_hearing', 'committee_chair', 'committee_vice_chair']
    )
    return data
