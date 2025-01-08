#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils.py
Created on Oct 15, 2024
@author: danyasherbini

Custom functions for Legislation Tracker streamlit app

"""
import streamlit as st
from utils.session_manager import initialize_session_state

###############################################################################

import ast

def ensure_set(x):
    '''
    Converts a string to a set.
    Needed to reformat the bill history column in the bills data set.
    '''
    if isinstance(x, str):
        try:
            # Convert string representation of a set to an actual set
            return ast.literal_eval(x)
        except (ValueError, SyntaxError):
            # If it's not a valid string representation, return an empty set
            return set()
    elif isinstance(x, set):
        return x
    else:
        # Return an empty set if the type is not recognized
        return set()


###############################################################################

import re

def format_bill_history(element_set):
    '''
    Reformats Bill History into a more readable/cleaner format for Streamlit,
    with extra empty lines between entries using Markdown formatting. Necessary 
    because we use st.markdown() to display bill_history text on the streamlit app.
    '''
    result = ''
    current_date = None
    
    for element in element_set:
        # Replace '>>' with ':' in the entire set
        element = element.replace('>>', ':')
        
        # Check if the element starts with a date
        if re.match(r'^\d{4}-\d{2}-\d{2}', element):
            # If it's a date, start a new line with Markdown-friendly formatting
            if current_date is not None:
                result += "\n\n  "  # Two spaces after \n forces a newline in Markdown
            
            # Add the date element
            result += element
        
            # Store the date for the next iteration
            current_date = element.split()[0].split('-')[0]
    
    return result.strip()


###############################################################################

def add_bill_to_dashboard(number, name, author, coauthors, status, date, chamber, link, text, history):
    """
    Adds a selected bill from the bills page to the dashboard page via the 'Add to Dashboad' button.
    """
    # Check if the bill is already in the selected_bills list
    if not any(bill['bill_number'] == number for bill in st.session_state.selected_bills):
        bill = {
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
        }
        
        # Add the bill to the session state
        st.session_state.selected_bills.append(bill)
        st.success(f'Bill {number} added to dashboard!')
    else:
        st.warning(f'Bill {number} is already in the dashboard.')

###############################################################################

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
    #if 'selected_bills' not in st.session_state:
       #st.session_state.selected_bills = []
      
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
            # Call the function to add the bill to the dashboard and update the cache
            add_bill_to_dashboard(number, name, author, coauthors, status, date, chamber, link, text, history)


###############################################################################

from io import BytesIO

def to_csv(df) -> bytes:
    '''
    Downloads data from the app to csv file. To be used with st.download_button()
    '''
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output.getvalue()
