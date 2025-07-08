#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/org_dashboard.py
Created on Oct 15, 2024
@author: danyasherbini

Utility function for displaying bill details on the ORG DASHBOARD page.

"""

import streamlit as st
import pandas as pd
from db.query import get_custom_bill_details_with_timestamp, save_custom_bill_details_with_timestamp, remove_bill_from_org_dashboard

def display_org_dashboard_details(selected_rows):
    '''
    Displays bill details on the ORG DASHBOARD page when a row is selected; features a button to remove a bill from your dashboard.
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
    
    # Get the org and user details from session state
    org_id = st.session_state.get('org_id', 'Unknown Org ID')
    org_name = st.session_state.get('org_name', 'Unknown Org')
    user_email = st.session_state.get('user_email', 'Unknown User')

    # Correct escaped newlines for bill excerpt
    bill_text = bill_text.replace("\\n\\n", "\n\n")
    
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
            if st.button(f"Remove from {org_name} Dashboard", use_container_width=True, type='primary'):
                # Call the function to remove the bill from the dashboard
                remove_bill_from_org_dashboard(openstates_bill_id, bill_number)
                
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

    # Retrieve saved custom details
    custom_details = get_custom_bill_details_with_timestamp(openstates_bill_id, org_id)

    # Form for custom user-entered fields
    st.markdown('#### Custom Advocacy Details')
    st.markdown('Use this section to enter custom details for this bill. <span title="These fields are also viewable on the My Dashboard page if you add this bill to your personal dashboard, but are only editable from your Organization Dashboard." style="cursor: help;">💬</span>', unsafe_allow_html=True)

    with st.form(key='custom_fields', clear_on_submit=False, enter_to_submit=True, border=True):
        # First row with 4 columns
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            
            with col1:
                st.markdown('##### Org Position')
                org_position_options = ['','Needs Decision', 'Neutral/No Position', 'Support',
                                    'Support, if Amended', 'Oppose', 'Oppose, unless Amended']
                
                # Get the index
                org_position_default = 0
                if custom_details and 'org_position' in custom_details and custom_details['org_position'] in org_position_options:
                    org_position_default = org_position_options.index(custom_details['org_position'])
                    
                org_position = st.selectbox('Select Org Position', 
                                            org_position_options,
                                            index=org_position_default)
            
            with col2:
                st.markdown('##### Priority Tier')
                priority_tier_options = ['','Sponsored', 'Priority', 'Position', 'No Priority']
                
                # Get the index
                priority_tier_default = 0
                if custom_details and 'priority_tier' in custom_details and custom_details['priority_tier'] in priority_tier_options:
                    priority_tier_default = priority_tier_options.index(custom_details['priority_tier'])
                    
                priority_tier = st.selectbox('Select Priority Tier', 
                                            priority_tier_options,
                                            index=priority_tier_default)
            
            with col3:
                st.markdown('##### Community Sponsor')
                community_sponsor = st.text_input('Enter Community Sponsor',
                                                value=custom_details.get('community_sponsor', '') if custom_details else '')
            
            with col4:
                st.markdown('##### Coalition')
                coalition = st.text_input('Enter Coalition',
                                        value=custom_details.get('coalition', '') if custom_details else '')

        # Add empty rows of space    
        st.write("")
        st.write("")
        
        # Second row with 4 columns
        with st.container():
            col5, col6, col7, col8 = st.columns([2, 2, 2, 2])
            
            with col5:
                st.markdown('##### Action Taken')
                action_taken_options = ['','None', 'Letter of Support In Progress',
                                    'Letter of Support Drafted', 'Letter of Support Submitted']
                
                # Get the index
                action_taken_default = 0
                if custom_details and 'action_taken' in custom_details and custom_details['action_taken'] in action_taken_options:
                    action_taken_default = action_taken_options.index(custom_details['action_taken'])
                    
                action_taken = st.selectbox('Select Action Taken', 
                                        action_taken_options,
                                        index=action_taken_default)
            
            with col6:
                st.markdown('##### Assigned To')
                assigned_to = st.text_input('Enter Name',
                                        value=custom_details.get('assigned_to', '') if custom_details else '')
            
            with col7:
                st.markdown('##### Letter of Support')
                letter_of_support = st.text_input('Enter link to letter of support',
                                                value=custom_details.get('letter_of_support', '') if custom_details else '')
            
            with col8:
                if letter_of_support:
                    st.markdown('##### View Support Letter')
                    st.markdown('Open link to (must be valid URL in previous field)')
                    st.link_button('Open Link', str(letter_of_support))
                else:
                    st.markdown('')
                    st.markdown('')
                    st.markdown('')
        
        # Submit button - make sure it's properly within the form
        submitted = st.form_submit_button(
            label="Save Custom Bill Details",
            help='Click to save/update custom details for this bill',
            type='primary'
        )

        # Add message below the form displaying who last saved the custom details
        st.write("")
        with st.container():
            if custom_details:
                # Get the user who saved the details, but remove .com/.us slug from email so it doesn't hyperlink the text
                saved_by = custom_details.get('last_updated_by', 'Unknown')
                who = saved_by.split('.')[0]

                # Get date
                when = custom_details.get('last_updated_on', 'Unknown')
                when = when.strftime('%m-%d-%Y') # Format date to MM-DD-YYYY

                # Display message
                st.markdown(f"*Custom details last saved by {who} on {when}.*")

    # Handle form submission outside the form
    if submitted:
        try:
            # Update function call if needed
            save_custom_bill_details_with_timestamp( 
                bill_number, 
                org_position, 
                priority_tier, 
                community_sponsor,
                coalition, 
                letter_of_support, 
                openstates_bill_id,
                assigned_to, 
                action_taken,
                user_email,
                org_id,
                org_name
            )
            st.success(f"Custom details for bill {bill_number} saved successfully by {user_email} from {org_name}.")
            
        except Exception as e:
            st.error(f"Error saving details: {str(e)}")
    
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
    with st.container(key='bill_history_dialog'):
        st.markdown('##### Bill History')
        expander = st.expander('See bill history')
        expander.markdown(bill_history)
