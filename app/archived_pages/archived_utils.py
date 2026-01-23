#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
archived_utils.py
Created on May 12, 2025

Deprecated or outdated functions no longer in active use.

"""

import streamlit as st
import pandas as pd
from db.query import get_custom_bill_details, save_custom_bill_details, add_bill_to_dashboard, remove_bill_from_dashboard, add_bill_to_org_dashboard, remove_bill_from_org_dashboard, BILL_COLUMNS  

##############################################################################

# WARNING! THIS FUNCTION IS NOT UP TO DATE TO REFLECT LATEST CAPABILITIES OF DASHBOARD, ETC.
# USE display_bill_info_text() !

def display_bill_info_expander(selected_rows):
    '''
    Displays bill information in an expander when a row is selected in
    an Ag Grid data frame.
    
    Note: expanders cannot exist within another expander.
    '''
    # Extract the values from the selected row
    number = selected_rows['bill_number'].iloc[0]
    name = selected_rows['bill_name'].iloc[0]
    author = selected_rows['author'].iloc[0]
    coauthors = selected_rows['coauthors'].iloc[0]
    status = selected_rows['status'].iloc[0]
    date = selected_rows['date_introduced'].iloc[0]
    session = selected_rows['leg_session'].iloc[0]
    chamber = selected_rows['chamber'].iloc[0]
    link = selected_rows['leginfo_link'].iloc[0]
    text = selected_rows['bill_text'].iloc[0]
    history = selected_rows['bill_history'].iloc[0]
      
    with st.expander("View Bill Details", expanded=True):

        # Containter with add to dashboard button in the top-right corner
        with st.container(key='header_expander'):
            col1, col2 = st.columns([7.5, 2.5])  # Adjust column widths as needed
            with col1:
                st.markdown('### Bill Details')
            with col2:
                if st.button('Add to Dashboard', width='stretch',):
                    # Call the function to add the bill to the dashboard
                    add_bill_to_dashboard(number, name, author, coauthors, status, date, chamber, link, text, history)
        
        # Add empty row of space  
        st.write("")
        
        # Container for bill number and chamber
        with st.container(key='number_chamber_expander'):
            # Display columns with spacers
            col1, spacer1, col2, spacer2, col3 = st.columns([3, 0.5, 3, 0.5, 3])
            with col1:
                st.markdown('##### Bill Number')
                st.markdown(number)
            with col2:
                st.markdown('##### Bill Name')
                st.markdown(name)
            with col3:
                st.markdown('##### Chamber')
                st.markdown(chamber)

        # Add empty row of space    
        st.write("")
      
        # Container for authors
        with st.container(key='authors_expander'):
            # Display columns with spacers
            col1, spacer1, col2, spacer2, col3 = st.columns([3, 0.5, 3, 0.5, 3])
            with col1:
                st.markdown('##### Author')
                st.markdown(author)
            with col2:
                st.markdown('##### Co-author(s)')
                st.markdown(coauthors)
            with col3:
                st.markdown('##### Legislative Session')
                st.markdown(session)
        
        # Add empty row of space    
        st.write("")
  
        # Container for status
        with st.container(key='status_expander'):
            # Display columns with spacers
            col1, spacer1, col2, spacer2, col3 = st.columns([3, 0.5, 3, 0.5, 3])
            with col1:
                st.markdown('##### Status')
                st.markdown(status)
            with col2:
                st.markdown('##### Date Introduced')
                st.markdown(date)
            with col3:
                st.markdown('##### Link to Bill')
                st.link_button('leginfo.ca.gov', str(link))
          
        # Add empty row of space    
        st.write("")
            
        # Scrollable text area for bill text
        with st.container(key='bill_text_expander'):
            st.markdown('##### Bill Excerpt')
            st.text_area('For full bill text, refer to bill link.', text, height=300)
          
        # Scrollable text area for bill history
        with st.container(key='bill_history_expander'):
            st.markdown('##### Bill History')
            st.text_area('For more details, refer to bill link.', history, height=300)

###############################################################################

# WARNING! THIS FUNCTION IS NOT UP TO DATE TO REFLECT LATEST CAPABILITIES OF DASHBOARD, ETC.
# USE display_bill_info_text() !

@st.dialog('Bill Details', width='large')
def display_bill_info_dialog(selected_rows):
    '''
    Displays bill information in a dialog pop-up box when a row is selected in
    an Ag Grid data frame.
    
    Note: this can be slow to load.
    '''
    # Extract the values from the selected row
    number = selected_rows['bill_number'].iloc[0]
    name = selected_rows['bill_name'].iloc[0]
    author = selected_rows['author'].iloc[0]
    coauthors = selected_rows['coauthors'].iloc[0]
    status = selected_rows['status'].iloc[0]
    date = selected_rows['date_introduced'].iloc[0]
    session = selected_rows['leg_session'].iloc[0]
    chamber = selected_rows['chamber'].iloc[0]
    link = selected_rows['leginfo_link'].iloc[0]
    text = selected_rows['bill_text'].iloc[0]
    history = selected_rows['bill_history'].iloc[0]
      
    # Containter with add to dashboard button in the top-right corner
    with st.container(key='header_dialog'):
        col1, col2 = st.columns([7.5, 2.5])  # Adjust column widths as needed
        with col1:
            st.write("")
        with col2:
            if st.button('Add to Dashboard', width='stretch',):
                # Call the function to add the bill to the dashboard
                add_bill_to_dashboard(number, name, author, coauthors, status, date, chamber, link, text, history)
    
    # Add empty row of space  
    st.write("")
    
    # Container for bill number and chamber
    with st.container(key='number_chamber_dialog'):
        # Display columns with spacers
        col1, spacer1, col2, spacer2, col3 = st.columns([3, 0.5, 3, 0.5, 3])
        with col1:
            st.markdown('##### Bill Number')
            st.markdown(number)
        with col2:
            st.markdown('##### Bill Name')
            st.markdown(name)
        with col3:
            st.markdown('##### Chamber')
            st.markdown(chamber)

    # Add empty row of space    
    st.write("")
  
    # Container for authors
    with st.container(key='authors_dialog'):
        # Display columns with spacers
        col1, spacer1, col2, spacer2, col3 = st.columns([3, 0.5, 3, 0.5, 3])
        with col1:
            st.markdown('##### Author')
            st.markdown(author)
        with col2:
            st.markdown('##### Co-author(s)')
            st.markdown(coauthors)
        with col3:
            st.markdown('##### Legislative Session')
            st.markdown(session)
    
    # Add empty row of space    
    st.write("")

    # Container for status
    with st.container(key='status_dialog'):
        # Display columns with spacers
        col1, spacer1, col2, spacer2, col3 = st.columns([3, 0.5, 3, 0.5, 3])
        with col1:
            st.markdown('##### Status')
            st.markdown(status)
        with col2:
            st.markdown('##### Date Introduced')
            st.markdown(date)
        with col3:
            st.markdown('##### Link to Bill')
            st.link_button('leginfo.ca.gov', str(link))
      
    # Add empty row of space    
    st.write("")
    
    # Expander for bill text
    with st.container(key='bill_text_dialog'):
        st.markdown('##### Bill Excerpt')
        expander = st.expander('See bill text')
        expander.write(text)
      
    # Expander for bill history
    with st.container(key='bill_history_dialog'):
        st.markdown('##### Bill History')
        expander = st.expander('See bill history')
        expander.markdown(history)