#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Original display bill info function
Created on Jan 6, 2024
@author: danyasherbini
"""

import streamlit as st
import pandas as pd


@st.dialog('Bill Info', width='large')
def display_bill_info(selected_rows):
    '''
    Displays bill information in a dialog pop-up box when a row is selected in
    an Ag Grid data frame.
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
    
    # Initialize 'selected_bills' if it doesn't exist
    if 'selected_bills' not in st.session_state:
       st.session_state.selected_bills = []
      
    # Container for bill number and chamber
    with st.container(key='number_chamber'):
        # Display two columns in this container
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Bill No.')
            st.markdown(number)
        with col2:
            st.markdown('##### Chamber')
            st.markdown(chamber)

    with st.container(key='name'):
        st.markdown('##### Bill Name')
        st.markdown(name)
          
    # Container for authors
    with st.container(key='authors'):
        # Display two columns in this container
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Author')
            st.markdown(author)
        with col2:
            st.markdown('##### Coauthor')
            st.markdown(coauthors)
      
    # Container for status
    with st.container(key='status'):
        st.markdown('##### Status')
        st.markdown(status)
      
    # Container for date and session
    with st.container(key='date_session'):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Date Introduced')
            st.markdown(date)
        with col2:
            st.markdown('##### Legislative Session')
            st.markdown(session)
      
    # Button to leg info link
    with st.container(key='leginfo_link'):
        st.markdown('##### Link to Bill')
        st.link_button('leginfo.ca.gov', str(link))
      
    # Expander for bill text
    with st.container(key='bill_text'):
        st.markdown('##### Bill Text')
        expander = st.expander('See bill text')
        expander.write(text)
      
    # Expander for bill history
    with st.container(key='bill_history'):
        st.markdown('##### Bill History')
        expander = st.expander('See bill history')
        expander.markdown(history)
        
   # Button to add bill to dashboard
    with st.container(key='add_to_dashboard'):
        if st.button('Add to Dashboard'):
            # Avoid duplicates in the dashboard by checking the bill_number
            if not any(bill['bill_number'] == number for bill in st.session_state.selected_bills):
                # Add the bill to the session state if not already in the dashboard
                st.session_state.selected_bills.append({
                    'bill_number': number,
                    'bill_name': name,
                    'author': author,
                    'coauthors': coauthors,
                    'status': status,
                    'date_introduced': date,
                    'chamber': chamber,
                    'leginfo_link': link,
                    'full_text': text,
                    'bill_history': history
                })
                st.success(f'Bill {number} added to dashboard!')
            else:
                st.warning(f'Bill {number} is already in the dashboard.')
