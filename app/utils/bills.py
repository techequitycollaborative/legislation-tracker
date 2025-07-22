#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/bills.py
Created on Oct 15, 2024

Function for displaying bill details on the Bills Page.

"""
import streamlit as st
import pandas as pd
from db.query import add_bill_to_dashboard, add_bill_to_org_dashboard, add_bill_to_working_group_dashboard, BILL_COLUMNS
from .general import bill_topic_grid, clean_markdown

def display_bill_info_text(selected_rows):
    '''
    Displays bill information as markdown text when a row is selected in
    an Ag Grid data frame.
    '''
    # Extract the values from the selected row
    selected_data_dict = dict(zip(selected_rows.columns, selected_rows.iloc[0]))  # Convert selected row to a dictionary
    bill_values = [selected_data_dict.get(col, None) for col in BILL_COLUMNS] # Ensure values align with expected order of BILL_COLUMNS, which is necessary for proper db querying

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

    # Get the org and user details from session state
    org_id = st.session_state.get('org_id', 'Unknown Org ID')
    org_name = st.session_state.get('org_name', 'Unknown Org')
    org_nickname = st.session_state.get('nickname', 'Unknown Org')
    user_email = st.session_state.get('user_email', 'Unknown User')

    # Un-escape and escape special characters in bill text for Markdown
    bill_text = clean_markdown(bill_text)
    
    # Display Bill Info Below the Table
    st.markdown('### Bill Details')
    st.divider()
    
    # Containter with add to dashboard button in the top-right corner
    with st.container(key='title_button_container'):
        col1, col2 = st.columns([7, 3])  # Adjust column widths as needed
        with col1:
            st.markdown(f'### {bill_number}')
        with col2:
            # Add to ORG DASHBOARD button
            if st.button(f"Add to {org_nickname} Dashboard", use_container_width=True, type='primary'):
                # Call the function to add the bill to the dashboard
                add_bill_to_org_dashboard(openstates_bill_id, bill_number)

            # Add to MY DASHBOARD button
            if st.button('Add to My Dashboard', use_container_width=True,type='secondary'):
                # Call the function to add the bill to the dashboard
                add_bill_to_dashboard(openstates_bill_id, bill_number)

            if st.session_state.get('working_group', False):
                if st.button('Add to AI Working Group Dashboard', use_container_width=True,type='secondary'):
                    # Call the function to add the bill to the dashboard
                    add_bill_to_working_group_dashboard(openstates_bill_id, bill_number)
    
    # Add empty rows of space  
    st.write("")
    st.write("")
    
    st.markdown('#### Main Bill Details')
    st.markdown(f"_Main bill data is sourced from LegInfo. Data is updated 2x per day. LegInfo data for this bill was last updated on: {last_updated}_")

    # Container for bill number and chamber
    with st.container(key='main_details_container'):
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

            st.markdown('##### Bill Topic')
            bill_topic_grid(bill_topic)

            st.markdown('')

            if leginfo_link is not None:
                st.markdown('##### Link to Bill')
                st.link_button('leginfo.ca.gov', str(leginfo_link))
            else:
                st.markdown('#### ')
                st.markdown('')

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
