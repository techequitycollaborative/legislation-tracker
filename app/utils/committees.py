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
            if next_hearing is not None:
                st.markdown(next_hearing)
            else:
                st.markdown('*None scheduled*')

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
