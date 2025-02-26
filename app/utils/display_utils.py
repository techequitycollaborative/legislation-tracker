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
from db.query import get_custom_bill_details, save_custom_bill_details, add_bill_to_dashboard_with_db, remove_bill_from_dashboard  

def display_bill_info_text(selected_rows):
    '''
    Displays bill information as markdown text when a row is selected in
    an Ag Grid data frame.
    '''
    # Extract the values from the selected row
    bill_id = selected_rows['bill_id'].iloc[0]
    bill_number = selected_rows['bill_number'].iloc[0]
    bill_name = selected_rows['bill_name'].iloc[0]
    author = selected_rows['author'].iloc[0]
    coauthors = selected_rows['coauthors'].iloc[0]
    status = selected_rows['status'].iloc[0]
    date_introduced = selected_rows['date_introduced'].iloc[0]
    leg_session = selected_rows['leg_session'].iloc[0]
    chamber = selected_rows['chamber'].iloc[0]
    leginfo_link = selected_rows['leginfo_link'].iloc[0]
    full_text = selected_rows['full_text'].iloc[0]
    bill_history = selected_rows['bill_history'].iloc[0]
    bill_topic = selected_rows['bill_topic'].iloc[0]
    upcoming_comm_mtg = selected_rows['upcoming_comm_mtg'].iloc[0]
    referred_committee = selected_rows['referred_committee'].iloc[0]
    
    # Display Bill Info Below the Table
    st.markdown('### Bill Details')
    st.divider()
    
    # Containter with add to dashboard button in the top-right corner
    with st.container(key='title_button_container'):
        col1, col2 = st.columns([7, 3])  # Adjust column widths as needed
        with col1:
            st.markdown(f'### {bill_number}')
        with col2:
            if st.button('Add to My Dashboard', use_container_width=True,type='primary'):
                # Call the function to add the bill to the dashboard
                add_bill_to_dashboard_with_db(bill_id, bill_number, bill_name, status, date_introduced, leg_session, 
                              author, coauthors, chamber, leginfo_link, full_text, bill_history, bill_topic)
    
    # Add empty rows of space  
    st.write("")
    st.write("")
    
    st.markdown('#### Main Bill Details')
    st.write("")
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

            if upcoming_comm_mtg is not None:
                st.markdown('##### Upcoming Committee Meeting')
                st.markdown(upcoming_comm_mtg)
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

            if referred_committee is not None:
                st.markdown('##### Referred Committee')
                st.markdown(referred_committee)
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

            if bill_topic != 'Uncategorized':
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
    custom_details = get_custom_bill_details(bill_id)

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
            save_custom_bill_details(bill_id, bill_number, org_position, priority_tier, community_sponsor, letter_of_support)
            st.success("Custom details saved successfully!")

    # Add empty rows of space    
    st.write("")
    st.write("")

    # Expander for bill text
    with st.container(key='bill_text_text'):
        st.markdown('##### Bill Excerpt')
        expander = st.expander('Click to view bill excerpt')
        expander.write(full_text)

    # Add empty rows of space    
    st.write("")

    # Expander for bill history
    with st.container(key='bill_history_text'):
        st.markdown('##### Bill History')
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

def display_dashboard_details(selected_rows):
    '''
    Displays bill details on the dashboard page when a row is selected; features a button to remove a bill from your dashboard.
    '''
    # Extract the values from the selected row
    bill_id = selected_rows['bill_id'].iloc[0]
    bill_number = selected_rows['bill_number'].iloc[0]
    bill_name = selected_rows['bill_name'].iloc[0]
    author = selected_rows['author'].iloc[0]
    coauthors = selected_rows['coauthors'].iloc[0]
    status = selected_rows['status'].iloc[0]
    date_introduced = selected_rows['date_introduced'].iloc[0]
    leg_session = selected_rows['leg_session'].iloc[0]
    chamber = selected_rows['chamber'].iloc[0]
    leginfo_link = selected_rows['leginfo_link'].iloc[0]
    full_text = selected_rows['full_text'].iloc[0]
    bill_history = format_bill_history_dashboard(selected_rows['bill_history'].iloc[0])
    bill_topic = selected_rows['bill_topic'].iloc[0]
    upcoming_comm_mtg = selected_rows['upcoming_comm_mtg'].iloc[0]
    referred_committee = selected_rows['referred_committee'].iloc[0]
    
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
                remove_bill_from_dashboard(bill_id)
                
                # Deselect the row and stop execution
                st.session_state.selected_rows = None
                st.rerun()  # Refresh the app to reflect the change

    # Add empty rows of space  
    st.write("")
    st.write("")
    
    st.markdown('#### Main Bill Details')
    st.write("")
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

            if upcoming_comm_mtg is not None:
                st.markdown('##### Upcoming Committee Meeting')
                st.markdown(upcoming_comm_mtg)
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

            if referred_committee is not None:
                st.markdown('##### Referred Committee')
                st.markdown(referred_committee)
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

            if bill_topic != 'Uncategorized':
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
    custom_details = get_custom_bill_details(bill_id)

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
            save_custom_bill_details(bill_id, bill_number, org_position, priority_tier, community_sponsor, letter_of_support)
            st.success("Custom details saved successfully!")

    # Add empty rows of space    
    st.write("")
    st.write("")

    # Expander for bill text
    with st.container(key='bill_text_text'):
        st.markdown('##### Bill Excerpt')
        expander = st.expander('Click to view bill excerpt')
        expander.write(full_text)

    # Add empty rows of space    
    st.write("")

    # Expander for bill history
    with st.container(key='bill_history_text'):
        st.markdown('##### Bill History')
        expander = st.expander('Click to view bill history')
        expander.markdown(bill_history)


###############################################################################

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
    text = selected_rows['full_text'].iloc[0]
    history = selected_rows['bill_history'].iloc[0]
      
    with st.expander("View Bill Details", expanded=True):

        # Containter with add to dashboard button in the top-right corner
        with st.container(key='header_expander'):
            col1, col2 = st.columns([7.5, 2.5])  # Adjust column widths as needed
            with col1:
                st.markdown('### Bill Details')
            with col2:
                if st.button('Add to Dashboard', use_container_width=True,):
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
    text = selected_rows['full_text'].iloc[0]
    history = selected_rows['bill_history'].iloc[0]
      
    # Containter with add to dashboard button in the top-right corner
    with st.container(key='header_dialog'):
        col1, col2 = st.columns([7.5, 2.5])  # Adjust column widths as needed
        with col1:
            st.write("")
        with col2:
            if st.button('Add to Dashboard', use_container_width=True,):
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