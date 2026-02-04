#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/org_dashboard.py
Created on Oct 15, 2024

Utility function for displaying bill details on the ORG DASHBOARD page.

"""

import streamlit as st
import pandas as pd
from db.query import get_custom_bill_details_with_timestamp, save_custom_bill_details_with_timestamp, remove_bill_from_org_dashboard, get_letter_history, add_letter_to_history, get_bill_activity_history
from .general import bill_topic_grid, clean_markdown
from .profiling import profile, timer

@profile("utils/org_dashboard.py - display_org_dashboard_details")
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
    bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') if bill_event is not None and pd.notna(bill_event) else None
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'
    
    # Get the org and user details from session state
    org_id = st.session_state.get('org_id', 'Unknown Org ID')
    org_name = st.session_state.get('org_name', 'Unknown Org')
    user_email = st.session_state.get('user_email', 'Unknown User')
    user_name = st.session_state.get('user_name', 'Unknown User Name')

    # Un-escape and escape special characters in bill text for Markdown
    bill_text = clean_markdown(bill_text)
    
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
            if st.button(f"Remove from {org_name} Dashboard", width='stretch', type='primary'):
                # Call the function to remove the bill from the dashboard
                with timer("utils/org_dashboard.py - remove_bill_from_org_dashboard"):
                    remove_bill_from_org_dashboard(openstates_bill_id, bill_number)
                
                    # Deselect the row and stop execution
                    st.session_state.selected_rows = None
                    st.rerun()  # Refresh the app to reflect the change

    # Add empty rows of space  
    st.write("")
    st.write("")
    
    st.markdown('#### Main Bill Details')
    st.markdown("View primary bill data for this bill, sourced from LegInfo.")

    # Expander for main bill details section
    with st.expander('Click to view main bill details'):
        # Container for bill number and chamber
        with st.container(key='main_details_container_dashboard'):
            # Display columns with spacers
            col1, col2, col3, col4, col5 = st.columns([6, 1, 4, 1, 4])
            with col1:
                st.markdown('##### Bill Name')
                st.markdown(bill_name)

                st.markdown('')

                st.markdown('##### Last Updated')
                st.markdown(last_updated)
                
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

                st.markdown('##### Link to Bill')
                st.link_button('leginfo.ca.gov', str(leginfo_link))

        # Expander for bill text
        with st.container(key='bill_text_text'):
            st.markdown('##### Bill Excerpt')
            expander = st.expander('Click to view bill excerpt')
            expander.write(bill_text)

        # Add empty rows of space    
        st.write("")

        # Expander for bill history
        with st.container(key='bill_history_dialog'):
            st.markdown('##### Bill History')
            expander = st.expander('See bill history')
            expander.markdown(bill_history)

    # Add empty row of space
    st.write("")

    # Retrieve saved custom details
    custom_details = get_custom_bill_details_with_timestamp(openstates_bill_id, org_id)

    # Form for custom user-entered fields
    st.markdown('#### Custom Advocacy Details')
    st.markdown('Use this section to enter custom details for this bill. <span title="These fields are also viewable on the My Dashboard page if you add this bill to your personal dashboard, but are only editable from your Organization Dashboard." style="cursor: help;">💬</span>', unsafe_allow_html=True)

    # Wrap in expander
    with st.expander('Click to view/edit custom advocacy details'):
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
            
            # Second row
            with st.container():
                col5, col6, col7 = st.columns([2, 4, 2])

                with col5:
                    st.markdown('##### Assigned To')
                    assigned_to = st.text_input('Enter Name',
                                            value=custom_details.get('assigned_to', '') if custom_details else '',
                                            help='Enter the name of the person assigned to this bill within your organization.')
            

                with col6:
                    st.markdown('##### Action Taken')
                    # Action taken -- text input
                    action_taken = st.text_area('Enter notes on action taken',
                                            value=custom_details.get('action_taken', '') if custom_details else '',
                                            help='Enter any notes on recent action taken for this bill, e.g., "letter for judiciary committee sent" etc. ' \
                                            'For full list of actions taken on this bill, see Activity section.')

                    # Action taken -- dropdown select
                    #action_taken_options = ['','None', 'Letter In Progress',
                    #                    'Letter Drafted', 'Letter Submitted']
                    
                    # Get the index
                    #action_taken_default = 0
                    #if custom_details and 'action_taken' in custom_details and custom_details['action_taken'] in action_taken_options:
                    #    action_taken_default = action_taken_options.index(custom_details['action_taken'])
                        
                    #action_taken = st.selectbox('Select Action Taken', 
                    #                        action_taken_options,
                    #                        index=action_taken_default)
                

                
            # Space
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
        
    # Add empty row of space
    st.write("")
    
    # Letter History Section
    st.markdown('#### Letter History')
    st.markdown('View all previous letters for this bill.')

    with st.expander('Click to view letter history'):
        letter_history = get_letter_history(openstates_bill_id, org_id)
    
        # Button to add new letter
        with st.form(key='add_letter_form', border=True):
            st.markdown('##### Add New Letter')
            new_letter_name = st.text_input('Letter Name', help='Enter a name for the letter')
            new_letter_url = st.text_input('Letter URL', help='Enter valid URL to the letter')
            add_letter_btn = st.form_submit_button('Add Letter to History', type='primary')
            
            if add_letter_btn and new_letter_url and new_letter_name:
                try:
                    add_letter_to_history(openstates_bill_id, bill_number, org_id, org_name,
                                                new_letter_name, new_letter_url, user_name)
                    st.success(f"Letter added to history!")
                    st.rerun()
                except Exception as e:
                        st.error(f"Error adding letter: {str(e)}")
                else:
                    st.warning("Please enter both a letter name and URL")
        
        st.divider()
        st.markdown('##### Letters')
        st.text('View all added letters for this bill below. Letters appear in reverse chronological order (most recent first).')
            
        # Display letter history in a table
        if letter_history:
            for idx, letter in enumerate(letter_history):
                with st.container(border=True):
                    st.markdown(f"**{letter['letter_name']}**")
                    st.link_button('Open Letter', letter['letter_url'])
                        
                    created_date = letter['created_on'].strftime('%m-%d-%Y')
                    st.markdown(f"**Date:** {created_date}")
                    st.markdown(f"**Added By:** {letter['created_by'].split('.')[0]}")
                    
        else:
            st.info('No letters in history yet. Add your first letter above.')

    # Space
    st.markdown('')

    # Activity Feed Section
    st.markdown('#### Activity Feed')
    st.markdown('View all updates made to this bill by your team.')

    with st.expander('Click to view activity feed'):
        activity_feed = get_bill_activity_history(openstates_bill_id, org_id)
        
        if not activity_feed:
            st.info("No activity recorded yet. Updates to bill details and letters will appear here.")
        else:
            # Filter options
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                activity_types = ['All', 'Field Changes', 'Letters']
                selected_type = st.selectbox('Filter by type:', activity_types)
            
            with col_filter2:
                users = ['All Users'] + list(set([item['user'] for item in activity_feed if item['user']]))
                selected_user = st.selectbox('Filter by user:', users)
            
            # Apply filters
            filtered_feed = activity_feed
            if selected_type == 'Field Changes':
                filtered_feed = [item for item in filtered_feed if item['activity_type'] == 'field_change']
            elif selected_type == 'Letters':
                filtered_feed = [item for item in filtered_feed if item['activity_type'] == 'letter']
            
            if selected_user != 'All Users':
                filtered_feed = [item for item in filtered_feed if item['user'] == selected_user]
            
            st.caption(f"Showing {len(filtered_feed)} of {len(activity_feed)} activities")
            st.divider()
            
            # Display activities
            for item in filtered_feed:
                col1, col2 = st.columns([2, 4])
                
                with col1:
                    if item['activity_type'] == 'field_change':
                        field_display = item['field_name'].replace('_', ' ').title()
                        st.markdown(f"**{field_display}** updated")
                        
                        if item['old_value'] and item['old_value'].strip():
                            st.caption(f"From: _{item['old_value']}_")
                        else:
                            st.caption("From: _(empty)_")
                        st.caption(f"To: **{item['new_value']}**")
                    
                    elif item['activity_type'] == 'letter':
                        st.markdown(f"📄 **Letter Added:** {item['field_name']}")
                        if item['old_value']:
                            st.markdown(f"[View Letter]({item['old_value']})")
                
                with col2:
                    st.markdown(f"**👤 User:** {item['user']}")
                    if item['date']:
                        st.markdown(f"**📅 Date:** {item['date'].strftime('%m/%d/%Y')}")
                    if item['timestamp']:
                        st.markdown(f"**🕐 Time:** {item['timestamp'].strftime('%I:%M %p')}")
                
                st.divider()