#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/my_dashboard.py
Created on Oct 15, 2024
@author: danyasherbini

Utility function for displaying bill details on the MY DASHBOARD page.

"""
import streamlit as st
import pandas as pd
from db.query import get_custom_bill_details_with_timestamp, remove_bill_from_dashboard

def display_dashboard_details(selected_rows):
    '''
    Displays bill details on the MY DASHBOARD page when a row is selected.
    Features a button to remove a bill from your dashboard.
    '''
    # Extract the values from the selected row
    openstates_bill_id = selected_rows['openstates_bill_id'].iloc[0]
    bill_number = selected_rows['bill_number'].iloc[0]
    bill_name = selected_rows['bill_name'].iloc[0]
    author = selected_rows['author'].iloc[0]
    coauthors = selected_rows['coauthors'].iloc[0]
    status = selected_rows['status'].iloc[0]
    date_introduced = selected_rows['date_introduced'].iloc[0]
    leg_session = selected_rows['leg_session'].iloc[0]
    chamber = selected_rows['chamber'].iloc[0]
    leginfo_link = selected_rows['leginfo_link'].iloc[0]
    bill_text = selected_rows['bill_text'].iloc[0]
    bill_history = selected_rows['bill_history'].iloc[0]
    bill_topic = selected_rows['bill_topic'].iloc[0]
    bill_event = selected_rows['bill_event'].iloc[0]
    event_text = selected_rows['event_text'].iloc[0]
    last_updated = selected_rows['last_updated_on'].iloc[0]

    # Format dates MM-DD-YYYY in the bill details
    date_introduced = pd.to_datetime(date_introduced).strftime('%m-%d-%Y') if date_introduced is not None else None
    bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') if bill_event is not None else None
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'

    # Access org and user info from session state
    org_id = st.session_state.get('org_id', 'Unknown Org ID')
    org_name = st.session_state.get('org_name', 'Unknown Org')
    user_email = st.session_state.get('user_email', 'Unknown User')
    
    # Display Bill Info Below the Table
    st.markdown('### Bill Details')
    st.divider()
    
    # Container with remove from dashboard button in the top-right corner
    with st.container(key='title_button_container'):
        col1, col2 = st.columns([7, 3])  # Adjust column widths as needed
        with col1:
            st.markdown(f'### {bill_number}')
        with col2:
            # If button is clicked: 
            if st.button('Remove from My Dashboard', use_container_width=True, type='primary'):
                # Call the function to remove the bill from the dashboard
                remove_bill_from_dashboard(openstates_bill_id, bill_number)
                
                # Deselect the row and stop execution
                st.session_state.selected_rows = None
                st.rerun()  # Refresh the app to reflect the change

    # Add empty rows of space  
    st.write("")
    st.write("")
    
    st.markdown('#### Main Bill Details')
    st.markdown(f"_Main bill data is sourced from LegInfo. Data is updated 2x per day. LegInfo data for this bill was last updated on: {last_updated}_")

    # Container for bill number and chamber
    with st.container(key='main_details_container_dashboard'):
        # Display columns with spacers
        col1, col2, col3, col4, col5 = st.columns([6, 1, 4, 1, 4])
        with col1:
            st.markdown('##### Bill Name')
            st.markdown(bill_name)

            st.markdown('')

            st.markdown('##### Chamber')
            st.markdown(chamber)
            
            st.markdown('')

            st.markdown('##### Status')
            st.markdown(status)

            st.markdown('')

            if bill_event is not None:
                st.markdown('##### Bill Event Date')
                st.markdown(bill_event)
            else:
                st.markdown('#### ')
                st.markdown('')
        
        with col2:
            st.markdown('')
        
        with col3:
            st.markdown('##### Author')
            st.markdown(author)

            st.markdown('')

            st.markdown('##### Legislative Session')
            st.markdown(leg_session)            

            st.markdown('')

            st.markdown('##### Date Introduced')
            st.markdown(date_introduced)

            st.markdown('')

            if event_text is not None:
                st.markdown('##### Bill Event Type/Location')
                st.markdown('_Committee hearing, floor session, etc._')
                st.markdown(event_text)
            else:
                st.markdown('#### ')
                st.markdown('')
        
        with col4:
            st.markdown('')
        
        with col5:
            if coauthors is not None:
                st.markdown('##### Co-author(s)')
                st.markdown(coauthors)
            else:
                st.markdown('#### ')
                st.markdown('')
            
            st.markdown('')

            if bill_topic:
                st.markdown('##### Bill Topic')
                st.markdown(bill_topic)
            else:
                st.markdown('#### ')
                st.markdown('')

            st.markdown('')

            st.markdown('##### Link to Bill')
            st.link_button('leginfo.ca.gov', str(leginfo_link))

    # Add empty rows of space    
    st.write("")
    st.write("")

    # Retrieve saved custom details
    custom_details = get_custom_bill_details_with_timestamp(openstates_bill_id, org_id)

    # Form for custom user-entered fields
    st.markdown('#### Custom Bill Details')
    st.markdown(f'This section contains information entered by members of your organization. <span title="These fields are only editable from your Organization Dashboard." style="cursor: help;">💬</span>', unsafe_allow_html=True)
    
    with st.container(key='custom_fields_container', border=True):
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.markdown('##### Org Position')
                st.text(custom_details.get('org_position', '') if custom_details else '')
                
            with col2:
                st.markdown('##### Priority Tier')
                st.text(custom_details.get('priority_tier', '') if custom_details else '')
                
            with col3:
                st.markdown('##### Community Sponsor')
                st.text(custom_details.get('community_sponsor', '') if custom_details else '')      
            
            with col4:
                st.markdown('##### Coalition')
                st.text(custom_details.get('coalition', '') if custom_details else '')

            # Add empty rows of space    
            st.write("")
            st.write("")
        
        # Second row with 4 columns
        with st.container():
            col5, col6, col7, col8 = st.columns([2, 2, 2, 2])
            with col5:
                st.markdown('##### Action Taken')
                st.text(custom_details.get('action_taken', '') if custom_details else '')

            with col6:
                st.markdown('##### Assigned To')
                st.text(custom_details.get('assigned_to', '') if custom_details else '')

            with col7:
                st.markdown('##### Letter of Support')
                letter_of_support = custom_details.get('letter_of_support', '') if custom_details else ''
                if letter_of_support:
                    st.link_button('Open Link', str(letter_of_support))
                
            with col8:
                    st.markdown('')
                    st.markdown('')
                    st.markdown('')

        # Add message below the form displaying who last saved the custom details
        st.write("")
        with st.container():
            if custom_details:
                # Get the user who saved the details, but remove .com/.us slug from email so it doesn't hyperlink the text
                saved_by = custom_details.get('last_updated_by', 'Unknown User')
                who = saved_by.split('.')[0]

                # Get date
                when = custom_details.get('last_updated_on', 'Unknown Date')
                when = when.strftime('%m-%d-%Y') # Format date to MM-DD-YYYY

                # Display message
                st.markdown(f"*Custom details last saved by {who} on {when}.*")
                
    # Add empty rows of space    
    st.write("")
    st.write("")

    # Expander for bill text
    with st.container(key='bill_text_text'):
        st.markdown('#### Bill Excerpt')
        expander = st.expander('Click to view bill excerpt')
        expander.write(bill_text)

    # Add empty rows of space    
    st.write("")

    # Expander for bill history
    with st.container(key='bill_history_text'):
        st.markdown('#### Bill History')
        expander = st.expander('Click to view bill history')
        expander.markdown(bill_history)