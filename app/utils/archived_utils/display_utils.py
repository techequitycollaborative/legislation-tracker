#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/archived_utils/display_utils.py
Created on Oct 15, 2024
@author: danyasherbini

Functions for displaying bill details in different formats and on different pages of the Legislation Tracker.
IMPORTANT: THIS SCRIPT IS DEPRECATED. FUNCTIONS HAVE BEEN REFACTORED INTO INDIVIDUAL .PY FILES IN THE app/utils/ DIRECTORY.

"""
import streamlit as st
import pandas as pd
from db.query import get_custom_bill_details, get_custom_bill_details_with_timestamp, get_custom_contact_details_with_timestamp
from db.query import save_custom_bill_details, save_custom_bill_details_with_timestamp, save_custom_contact_details_with_timestamp
from db.query import add_bill_to_dashboard, remove_bill_from_dashboard, add_bill_to_org_dashboard, remove_bill_from_org_dashboard
from db.query import BILL_COLUMNS, COMMITTEE_COLUMNS, LEGISLATOR_COLUMNS

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
    user_email = st.session_state.get('user_email', 'Unknown User')
    
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
            if st.button(f"Add to {org_name} Dashboard", use_container_width=True, type='primary'):
                # Call the function to add the bill to the dashboard
                add_bill_to_org_dashboard(openstates_bill_id, bill_number)

            # Add to MY DASHBOARD button
            if st.button('Add to My Dashboard', use_container_width=True,type='secondary'):
                # Call the function to add the bill to the dashboard
                add_bill_to_dashboard(openstates_bill_id, bill_number)
    
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

            if bill_topic is not None:
                st.markdown('##### Bill Topic')
                st.markdown(bill_topic)
            else:
                st.markdown('#### ')
                st.markdown('')

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


###############################################################################

import re

def format_bill_history_dashboard(bill_history):
    '''
    Reformats bill_history variable into a descending chronological list for the bill history section of the DASHBOARD bill details page.
    '''
    if not bill_history:
        return ""

    # Split entries by new lines
    entries = bill_history.strip().split("\n")

    formatted_entries = []
    for entry in entries:
        # Match date and event in the format: YYYY-MM-DD: Event
        match = re.match(r"^(\d{4}-\d{2}-\d{2}):\s*(.+)", entry)
        if match:
            date, event = match.groups()
            formatted_entries.append((date, event))

    # Sort entries by date in descending order
    formatted_entries.sort(reverse=True, key=lambda x: x[0])

    # Format back into readable Markdown-style text
    return "\n\n".join([f"**{date}:** {event}" for date, event in formatted_entries])

###################################################################################

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

####################################################################################

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
    st.markdown('#### Custom Bill Details')
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

###############################################################################
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

############################################################

##### HELPER FUNCTIONS
# Styling the staffer contact rows
COLOR_SCHEME = {
    "office": {
        "background": "#FFFFFF",  # white
        "border": "#B8D9FF",
        "text": "#003366"
    },
    "committee": {
        "background": "#FFFFFF",  # White
        "border": "#ffe1e1",
        "text": "#9c0202"
    },
    "user": {
        "background": "#E6FFE6",  # Light green
        "border": "#B8FFB8",
        "text": "#006600"
    }
}

FILTER_SCHEME = {
    "Codex (automatic)": ["office", "committee"],
    "Office": ["office"],
    "Committee": ["committee"],
    "User-added": ["user"]
}
def apply_row_style(row):
    color = COLOR_SCHEME[row['staffer_type']]
    return [f"background-color: {color['background']}; color: {color['text']}"] * len(row)

def staffer_filter(df):
    # Create filter controls in columns at the top
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        issue_filter = st.multiselect(
            "Filter by Issue Area",
            options=sorted(df['issue_area'].unique()),
            default=None,
            placeholder="All issues"
        )
    
    with filter_col2:
        staffer_filter = st.text_input(
            "Filter by Staffer Name",
            placeholder="Type to search..."
        )
    
    with filter_col3:
        contact_type = st.selectbox(
            "Contact Type",
            options=["All", "Codex (automatic)", "Office", "Committee", "User-added"],
            index=0
        )

    # Apply filters
    filtered_df = df.copy()
    if issue_filter:
        filtered_df = filtered_df[filtered_df['issue_area'].isin(issue_filter)]
    if staffer_filter:
        filtered_df = filtered_df[
            filtered_df['staffer_contact'].str.contains(staffer_filter, case=False, na=False)
        ]
    if contact_type != "All":
        filtered_df = filtered_df[filtered_df['staffer_type'].isin(FILTER_SCHEME[contact_type])]
    return filtered_df

def staffer_directory_tab(df):
    # filtered_df = staffer_filter(df)
    # Display the filtered table
    st.dataframe(
        # filtered_df,
        df.style.apply(apply_row_style, axis=1),
        column_config={
            "issue_area": "Issue Area",
            "staffer_contact": "Primary Contact",
            "auto_email": "Default Email",
            "custom_contact": "Custom Contact",
            "custom_email": "Custom Email",
            "people_contact_id": None,
            "staffer_type": None
        },
        use_container_width=True,
        height=600,
        hide_index=True
    )

    # 5. Quick stats and export
    col1, col2, col3 = st.columns([4, 3, 1])
    with col1:
        st.caption(f"Showing {len(df)} of {len(st.session_state.contact_df)} records. Only visible records are exported.")
    with col2:
        st.markdown('')
    with col3:
        st.download_button(
            "Export Contacts to CSV",
            df.to_csv(index=False),
            "contacts.csv",
            "text/csv"
        )

def issue_editor_tab(df, openstates_people_id, org_id, org_name, user_email):
    with st.form("bulk_edit_form"):
        edited_df = st.data_editor(
            df.style.apply(apply_row_style, axis=1),
            disabled=["people_contact_id", "issue_area", "staffer_contact", "auto_email", "staffer_type"],
            column_config={
                "custom_contact": st.column_config.TextColumn("Custom Contact"),
                "custom_email": st.column_config.TextColumn("Custom Email"),
                "people_contact_id": None,
                "staffer_type": None,
                "issue_area": "Issue Area",
                "staffer_contact": "Codex Contact",
                "auto_email": "Auto-generated email"
            },
            use_container_width=True,
            hide_index=True,
            height=600
        )
        if st.form_submit_button("💾 Save All Changes"):

            # Get non-null rows for DB update
            changed_df = edited_df.loc[edited_df.custom_email.notnull() & edited_df.custom_contact.notnull()]
            changed_df.staffer_type = "user"
            st.session_state.contact_df.update(changed_df)

            # Update DB
            if save_custom_contact_details_with_timestamp(changed_df, openstates_people_id, user_email, org_id, org_name):
                st.success("Custom details updated")
                st.rerun()

##### CONTROLLER FUNCTION
def display_legislator_info_text(selected_rows):
    '''
    Displays legislator information as markdown text when a row is selected in
    an Ag Grid data frame.
    '''
    # Ensure values align with expected order of LEGISLATOR_COLUMNS, which is necessary for proper db querying
    assert selected_rows.columns.tolist() == LEGISLATOR_COLUMNS 

    ## SELECTING DATA POINTS FROM STREAMLIT STATE
    openstates_people_id = selected_rows['openstates_people_id'].iloc[0] 
    name = selected_rows['name'].iloc[0]
    party = selected_rows['party'].iloc[0]
    chamber = selected_rows['chamber'].iloc[0]
    district = selected_rows['district'].iloc[0]
    other_names = selected_rows['other_names'].iloc[0]
    ext_sources = selected_rows['ext_sources'].iloc[0]
    office_details = selected_rows['office_details'].iloc[0]
    issue_contacts = selected_rows['issue_contacts'].iloc[0]
    last_updated = selected_rows['last_updated_on'].iloc[0]

    # Access user info from session state
    org_id = st.session_state.get('org_id')
    org_name = st.session_state['org_name']
    user_email = st.session_state['user_email']

    ## TRANSFORMING FOR DISPLAY
    #### Legislator name(s)
    display_name = " ".join(name.split(", ")[::-1]) # reorder name parts
    display_other_names = '- ' + other_names.replace("; ", "\n- ") # add newlines and hyphens for bullet formatting
    
    #### Office details
    distinct_offices = set([o for o in office_details.split("\\n")]) # get unique set of offices
    display_offices = [d.split('@@') for d in distinct_offices] # split unique offices by separator characters

     #### Last updated date
    # Format dates MM-DD-YYYY in the bill details
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'

    # # Display Legislator Info Below the Table
    st.markdown(f"#### {display_name} ({chamber[0]}D {district} - {party.title()})")

    # Display other names as a pop-over
    with st.popover(f"_Other names_"):
        if other_names is not None:
            st.markdown(display_other_names)
        else:
            st.markdown('_No other recognized names._')

    st.caption(f"Last updated on {last_updated}")

    # OFFICES
    with st.container(border=True):
        st.markdown("##### Office Details")
        # Create an expander for each office
        for i, contents in enumerate(display_offices):
            office_name = f"**{contents[0]}**" # Write office name
            st.markdown(office_name)
            expander = st.expander('Click to view')
            with st.container(key=f"office_text_{i}"):
                phone_address = "\n\n".join(contents[1:])
                expander.write(phone_address)

    #### Codex details
    # Codex extracted contacts

    codex_data = issue_contacts.split("\\n") # Split up aggregated data points

    # Transform into unified dataframe for display and editing
    contact_df = pd.DataFrame(columns=["people_contact_id", "issue_area", "staffer_type", "staffer_contact", "auto_email", "custom_contact", "custom_email"])
    # Loop over the codex data
    for cd in codex_data:
        # extract contents of each contact data point
        snapshot_data = cd.split("@@")
        # extract relevant custom details
        contact_df.loc[len(contact_df)] = snapshot_data + [None, None] # add dummy value for custom details to fill in later

    # If custom data is not None, merge by people_contact_id
    with st.spinner("Loading custom contacts..."):
        custom_contact_data = get_custom_contact_details_with_timestamp(openstates_people_id) # a list of dictionaries
    if custom_contact_data != None:
        for ccd in custom_contact_data:
            # Update existing rows if possible
            contact_df.loc[contact_df.people_contact_id == str(ccd["people_contact_id"]), ["staffer_type", "custom_contact", "custom_email"]] = ["user", ccd["custom_staffer_contact"], ccd["custom_staffer_email"]]
    
    # Update session state by selection
    if st.session_state.selected_person != openstates_people_id:
        st.session_state.selected_person = openstates_people_id
        st.session_state.contact_df = contact_df
        st.session_state.filtered_df = contact_df
        st.rerun()

    with st.container(border=True):
        st.markdown('##### Staffers by Issue Area')
        # Filter columns of directory before generating tab(s)
        st.session_state.filtered_df = staffer_filter(st.session_state.contact_df)
        if st.session_state['org_id'] == 1: # Contact editor only for TechEquity folks
            # Tab layout to view and edit
            tab1, tab2 = st.tabs(["Directory View", "Contact Editor"])
                
            with tab1:
                staffer_directory_tab(st.session_state.filtered_df)
            
            with tab2:
                issue_editor_tab(st.session_state.filtered_df, openstates_people_id, org_id, org_name, user_email)
        else: # If not TechEquity, only display (interim)
            st.subheader('Staffer Directory View')
            staffer_directory_tab(st.session_state.filtered_df)

    if ext_sources is not None:
        with st.popover("_External sources_"):
            for source_link in ext_sources.split("\\n"):
                # remove URL prefixes >> split on slashes >> build base URL
                source_name = '.'.join(source_link.replace("https://", "").replace("www.", "").split("/")[0].split(".")[-4:])
                st.link_button(source_name, str(source_link))
    else:
        st.markdown('#### ')
        st.markdown('')
    