#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/ai_working_group.py
Created on July 10, 2025

Function for displaying bills on the AI Working Group page.
"""

import streamlit as st
import pandas as pd
from db.query import get_all_custom_bill_details_for_bill, remove_bill_from_wg_dashboard, save_wg_comment, get_wg_comments
from .general import bill_topic_grid, clean_markdown
from .profiling import profile, timer

@profile("utils/ai_working_group.py - display_working_group_bill_details")
def display_working_group_bill_details(selected_rows):
    '''
    Displays bill details on the AI WORKING GROUP DASHBOARD page when a row is selected.
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
    bill_event_dt = pd.to_datetime(bill_event, errors='coerce')
    bill_event = bill_event_dt.strftime('%m-%d-%Y') if pd.notna(bill_event_dt) else None
    last_updated = pd.to_datetime(last_updated).strftime('%m-%d-%Y') if last_updated is not None else 'Unknown'

    # Access org and user info from session state
    org_id = st.session_state.get('org_id', 'Unknown Org ID')
    org_name = st.session_state.get('org_name', 'Unknown Org')
    user_email = st.session_state.get('user_email', 'Unknown User')
    user_name = st.session_state.get('user_name', 'Unknown User Name')
    
    # Un-escape and escape special characters in bill text for Markdown
    bill_text = clean_markdown(bill_text)
    
    # Display Bill Info Below the Table

    # Container with remove from dashboard button in the top-right corner
    with st.container(key='title_button_container'):
        col1, col2, col3 = st.columns([7, 1, 3])  # Adjust column widths as needed
        with col1:
            st.markdown('')
        
        with col2:
            st.markdown('')

        with col3:
            # If button is clicked: 
            if st.button('Remove Bill from Dashboard', width='stretch', type='primary'):
                # Call the function to remove the bill from the dashboard
                remove_bill_from_wg_dashboard(openstates_bill_id, bill_number)
                
                # Deselect the row and stop execution
                st.session_state.selected_rows = None
                st.rerun()  # Refresh the app to reflect the change

    # Add empty row of space  
    st.write("")
    
    # Display bill number and name
    st.markdown(f'### {bill_number}')
    st.markdown(bill_name)
    st.markdown('')

    st.markdown(f'#### Main Bill Details')
    with st.expander('Click to view main bill details'):
        with st.container(border=True, key='bill_details_container'):
            
            with st.container(key='status'):   
                col1, col2 = st.columns([2, 2])

                with col1:
                    st.markdown('##### Status')
                    st.markdown(status)

                with col2:
                    st.markdown('##### Last Updated')
                    st.markdown(last_updated)

                st.markdown('')

            with st.container(key='dates'):
                col1, col2 = st.columns([2, 2])

                with col1:
                    st.markdown('##### Date Introduced')
                    st.markdown(date_introduced)

                with col2:
                    if bill_event is not None:
                        st.markdown('##### Upcoming Event')
                        st.markdown(f"{event_text}: {bill_event}")
                    else:
                        st.markdown('')
                        st.markdown('')

                st.markdown('')
                
            with st.container(key='authors'):
                col1, col2 = st.columns([2, 2])

                with col1:
                    st.markdown('##### Author')
                    st.markdown(author)
                    
                with col2:
                    if coauthors is not None:
                        st.markdown('##### Co-author(s)')
                        st.markdown(coauthors)
                    else:
                        st.markdown('')
                        st.markdown('')        

                st.markdown('')

            with st.container(key='button'):
                st.markdown('##### Link to Bill')
                st.link_button('leginfo.ca.gov', str(leginfo_link))

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

            # Add empty rows of space    
            st.write("")
            st.write("")

    st.markdown('')

    # Discussion comments section
    st.markdown('#### Working Group Discussion')
    with st.expander('Click to view discussion comments on this bill'):
        with st.container(border=True, key='wg_discussion_comments'):
            
            # Text area for entering a comment
            comment = st.text_area('Enter a comment about this bill',
                                    value='',
                                    help='Enter any comments or discussion points about this bill for your working group members to see.')
            
            # Save comment button
            if st.button('Submit Comment', type='primary'):
                # Save the comment to the database
                save_wg_comment(
                    bill_number=bill_number,
                    user_name=user_name,
                    user_email=user_email,
                    org_id=org_id,
                    org_name=org_name,
                    comment=comment,
                )
                st.success('Comment submitted successfully!')
            
            st.markdown('---')
            
            # Display all comments
            st.markdown('##### All Comments')
            # Retrieve all comments for this bill
            comments = get_wg_comments(bill_number)
            if comments:
                for row in comments:
                    st.markdown(row['comment'])
                    st.caption(f"— {row['user_name']} on *{pd.to_datetime(row['added_on']).strftime('%m-%d-%Y')}*")
                    st.markdown('---')
            else:
                st.markdown('No comments yet. Be the first to comment!')



                    
