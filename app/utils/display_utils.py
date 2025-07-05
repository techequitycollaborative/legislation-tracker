#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
display_utils.py
Created on Oct 15, 2024
@author: danyasherbini

Functions for displaying bill details in different formats and on different pages of the Legislation Tracker.

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
    #date_introduced = pd.to_datetime(date_introduced).strftime('%m-%d-%Y') 
    date_introduced = pd.to_datetime(date_introduced).strftime('%m-%d-%Y') if date_introduced is not None else None
    #bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') 
    bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') if bill_event is not None else None
    #last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') 
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'

    # Get the org details from session state
    org_id = st.session_state.get('org_id')
    org_name = st.session_state['org_name']
    
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


###############################################################################

def display_dashboard_details_with_custom_fields(selected_rows):
    '''
    Displays bill details on the MY DASHBOARD page when a row is selected; features a button to remove a bill from your dashboard.
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
    #date_introduced = pd.to_datetime(date_introduced).strftime('%m-%d-%Y') 
    date_introduced = pd.to_datetime(date_introduced).strftime('%m-%d-%Y') if date_introduced is not None else None
    #bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') 
    bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') if bill_event is not None else None
    #last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') 
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'
    
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
    custom_details = get_custom_bill_details(openstates_bill_id)

    # Form for custom user-entered fields
    st.markdown('#### Custom Bill Details')
    st.write('Use this section to enter custom details for this bill.')
    with st.form(key='custom_fields', clear_on_submit=False, enter_to_submit=True, border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

        with col1:
            st.markdown('##### Org Position')
            org_position = st.selectbox('Select Org Position', 
                                        ['','Needs Decision', 'Neutral/No Position', 'Support', 
                                        'Support, if Amended', 'Oppose', 'Oppose, unless Amended'],
                                        index=(['','Needs Decision', 'Neutral/No Position', 'Support', 
                                                'Support, if Amended', 'Oppose', 'Oppose, unless Amended']
                                            .index(custom_details['org_position']) if custom_details else 0))

        with col2:
            st.markdown('##### Priority Tier')
            priority_tier = st.selectbox('Select Priority Tier', 
                                        ['','Sponsored', 'Priority', 'Position', 'No Priority'],
                                        index=(['','Sponsored', 'Priority', 'Position', 'No Priority']
                                                .index(custom_details['priority_tier']) if custom_details else 0))

        with col3:
            st.markdown('##### Community Sponsor')
            community_sponsor = st.text_input('Enter Community Sponsor', 
                                            value=custom_details['community_sponsor'] if custom_details else '')

        #with col4:
        #    st.markdown('##### Coalition')
        #    coalition = st.text_input('Enter Coalition', 
        #                            value=custom_details['coalition'] if custom_details else '')

        with col4:
            st.markdown('##### Letter of Support')
            letter_of_support = st.text_input('Link to Letter of Support', 
                                            value=custom_details['letter_of_support'] if custom_details else '')

        # Submit button
        submitted = st.form_submit_button("Save Custom Bill Details", 
                                        help='Click to save/update custom details for this bill', 
                                        type='secondary')

        if submitted:
            save_custom_bill_details(openstates_bill_id, bill_number, org_position, priority_tier, community_sponsor, letter_of_support)
            st.success("Custom details saved successfully!")

    # Add empty rows of space    
    st.write("")
    st.write("")

    # Expander for bill text
    with st.container(key='bill_text_text'):
        st.markdown('##### Bill Excerpt')
        expander = st.expander('Click to view bill excerpt')
        expander.write(bill_text)

    # Add empty rows of space    
    st.write("")

    # Expander for bill history
    with st.container(key='bill_history_text'):
        st.markdown('##### Bill History')
        expander = st.expander('Click to view bill history')
        expander.markdown(bill_history)

###################################################################################

def display_dashboard_details(selected_rows):
    '''
    Displays bill details on the MY DASHBOARD page when a row is selected; features a button to remove a bill from your dashboard.
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
    #date_introduced = pd.to_datetime(date_introduced).strftime('%m-%d-%Y') 
    date_introduced = pd.to_datetime(date_introduced).strftime('%m-%d-%Y') if date_introduced is not None else None
    #bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') 
    bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') if bill_event is not None else None
    #last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') 
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'
    
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
    custom_details = get_custom_bill_details_with_timestamp(openstates_bill_id)

    # Access user info from session state
    org_id = st.session_state.get('org_id')
    org_name = st.session_state['org_name']
    user_email = st.session_state['user_email']

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
    #date_introduced = pd.to_datetime(date_introduced).strftime('%m-%d-%Y') 
    date_introduced = pd.to_datetime(date_introduced).strftime('%m-%d-%Y') if date_introduced is not None else None
    #bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') 
    bill_event = pd.to_datetime(bill_event).strftime('%m-%d-%Y') if bill_event is not None else None
    #last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') 
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'
    
    # Get the org detaila from session state
    org_id = st.session_state.get('org_id')
    org_name = st.session_state['org_name']

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
    custom_details = get_custom_bill_details_with_timestamp(openstates_bill_id)

    # Form for custom user-entered fields
    st.markdown('#### Custom Bill Details')
    st.markdown('Use this section to enter custom details for this bill. <span title="These fields are also viewable on the My Dashboard page if you add this bill to your personal dashboard, but are only editable from your Organization Dashboard." style="cursor: help;">💬</span>', unsafe_allow_html=True)

    # Access user info from session state
    org_id = st.session_state.get('org_id')
    org_name = st.session_state['org_name']
    user_email = st.session_state['user_email']

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
                openstates_bill_id, 
                bill_number, 
                org_position, 
                priority_tier, 
                community_sponsor,
                coalition, 
                letter_of_support, 
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
        expander.markdown(history)

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

# Styling the staffer contact rows
def color_code(COLOR_MAP, row):
    color = COLOR_MAP.get(row["staffer_type"], "white")
    return [f"background-color: {color}"] * len(row)

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
    display_offices = [o.split("@@") for o in office_details.split("\\n")]

    #### Codex details
    # Codex extracted contacts

    contact_data = issue_contacts.split("\\n") # Split up aggregated data points

    custom_contact_data = get_custom_contact_details_with_timestamp(openstates_people_id)
    contact_df = pd.DataFrame(columns=["people_contact_id", "issue_area", "staffer_type", "contact", "auto_email", "custom_email"])
    for cd in contact_data:
        # extract contents of each contact data point
        snapshot_data = cd.split("@@")
        # extract relevant custom details
        custom_details = None # TODO: link the auto-generated details with relevant custom corrections
        if custom_details is None:
            contact_df.loc[len(contact_df)] = snapshot_data + [None] # add dummy value for custom details to fill in later
        else:
            contact_df.loc[len(contact_df)] = snapshot_data + [custom_details["custom_staffer_email"]] # index into existing custom detail

    ## Codex diplsay specifics
    # Map snake case names to display names
    display_contact_column_config = {
    "people_contact_id": None,
    "issue_area": "Issue Area",
    "staffer_type": None,
    "contact": "Contact",
    "auto_email": "Auto-detected email",
    "custom_email": "User-added email"
    }   

    # map staffer types to color
    display_staffer_type_colors = {
    "office": "#869ec4",  
    "committee":"#d6d6d6",
    "user": "#FEA0A0"  
    }

    # Apply color coding
    display_contacts = contact_df.style.apply(
        lambda r: color_code(display_staffer_type_colors, r), 
        axis=1
    )

    #### Last updated date
    # Format dates MM-DD-YYYY in the bill details
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'
    
    ## STREAMLIT MARKDOWN

    # # Display Legislator Info Below the Table
    st.subheader(f"{display_name} ({chamber[0]}D {district})")
    st.caption(f"{party} party member")
    # TODO: is this update info even useful?
    st.markdown(f"_Last updated on: {last_updated}_")

    # Tabbed display for 45+ issues
    tab1, tab2 = st.tabs(["📋 Summary", "✏️ Staffers by Issue Area"])
    with tab1:
        # OTHER NAMES
        if other_names is not None:
            st.markdown('**Alternate Names**') 
            st.markdown(display_other_names)
        else:
            st.markdown('')
        
        # OFFICES
        # Create an expander for each office
        for contents in display_offices:
            office_name = f"**{contents[0]}**" # Write office name
            st.markdown(office_name)
            expander = st.expander('Click to view')
            with st.container(key=f"{contents[0].lower()}_office_text"):
                phone_address = "\n\n".join(contents[1:])
                expander.write(phone_address)

        # READ ONLY CONTACTS
        st.markdown("🗂️ **All Contacts by Issue Area (Read-Only)**")

        # COLOR CODE
        cols = st.columns(len(display_staffer_type_colors))
        for i, (staffer_type, color) in enumerate(display_staffer_type_colors.items()):
            with cols[i]:
                st.markdown(
                    f'<div style="display: inline-block; width: 15px; height: 15px; '
                    f'background-color: {color}; margin-right: 5px; outline: 2px black; "></div>'
                    f'<span>{staffer_type.title()}</span>',
                    unsafe_allow_html=True
                )
        with st.expander("Click to view", expanded=False):

            st.dataframe(
                display_contacts,
                height=600,
                use_container_width=True,
                hide_index=True,
                column_config=display_contact_column_config
            )
    
    with tab2:
        st.caption('Use this section to enter custom details for contacting staff.', unsafe_allow_html=True)
        # edited_df = st.data_editor(
        #     display_contacts,
        #     num_rows="fixed",
        #     disabled=["issue_area", "auto_email"],  # Lock these
        #     column_config={
        #         "custom_staffer_contact": st.column_config.TextColumn(
        #             "Your Custom Staffer Info",
        #             help="Editable field"
        #         ),
        #         "custom_staffer_contact": st.column_config.TextColumn(
        #             "Your Custom Staffer Email",
        #             help="Editable field"
        #         )
        #     }
        # )

    

    # with st.form(key='custom_fields', clear_on_submit=False, enter_to_submit=True, border=True):
    #     # First row with 4 columns
    #     with st.container():
    #         col1, col2= st.columns([2, 2])
            
    #         with col1:
    #             st.markdown('##### Staffer Contact')
    #             staff_name = st.text_input('Enter details',
    #                                             value=contact_details.get('custom_staffer_contact', '') if contact_details else '')
    #         with col2:
    #             st.markdown("##### Email")
    #             phone_number = st.text_input('Enter email',
    #                                          value = contact_details.get('custom_staffer_email', '') if contact_details else '')

    #     # Add empty rows of space    
    #     st.write("")
    #     st.write("")
    
    #  # Submit button - make sure it's properly within the form
    #     submitted = st.form_submit_button(
    #         label="Save Custom Contact Details",
    #         help='Click to save/update custom details for this legislator',
    #         type='primary'
    #     )

    #     # Add message below the form displaying who last saved the custom details
    #     st.write("")
    #     with st.container():
    #         if contact_details:
    #             # Get the user who saved the details, but remove .com/.us slug from email so it doesn't hyperlink the text
    #             saved_by = contact_details.get('last_updated_by', 'Unknown')
    #             who = saved_by.split('.')[0]

    #             # Get date
    #             when = contact_details.get('last_updated_on', 'Unknown')
    #             when = when.strftime('%m-%d-%Y') # Format date to MM-DD-YYYY

    #             # Display message
    #             st.markdown(f"*Custom details last saved by {who} on {when}.*")

    # # Handle form submission outside the form
    # if submitted:
    #     try:
    #         # Update function call if needed
    #         save_custom_contact_details_with_timestamp(
    #             openstates_people_id, 
    #             phone_number,
    #             staff_name,
    #             user_email,
    #             org_id,
    #             org_name
    #         )
    #         st.success(f"Custom details for point of contact {staff_name} saved successfully by {user_email} from {org_name}.")
            
    #     except Exception as e:
    #         st.error(f"Error saving details: {str(e)}")
    
    if ext_sources is not None:
        st.markdown('##### Source Links')
        for source_link in ext_sources.split("\\n"):
            # remove URL prefixes >> split on slashes >> build base URL
            source_name = '.'.join(source_link.replace("https://", "").replace("www.", "").split("/")[0].split(".")[-4:])
            st.link_button(source_name, str(source_link))
    else:
        st.markdown('#### ')
        st.markdown('')
    