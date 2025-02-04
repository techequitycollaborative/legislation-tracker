#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils.py
Created on Oct 15, 2024
@author: danyasherbini

Custom functions for Legislation Tracker streamlit app

"""
import streamlit as st
import pandas as pd
import numpy as np
import re
from db.query import get_custom_bill_details, save_custom_bill_details

###############################################################################

def clean_bill_data(bills):
    """
    Clean up the bills DataFrame by:
    - Adding a 'chamber' column based on 'origin_chamber_id'
    - Dropping unnecessary columns
    - Sorting by 'bill_number'

    Parameters:
    -----------
        bills: DataFrame containing bill data

    Returns:
    --------
        Cleaned DataFrame
    """
    # Make 'chamber' column and assign values
    bills['chamber'] = np.where(bills['origin_chamber_id'] == 1, 'Assembly', 'Senate')

    # Drop unnecessary columns
    bills = bills.drop(['openstates_bill_id', 'committee_id', 'origin_chamber_id'], axis=1)

    # Sort by 'bill_number'
    bills = bills.sort_values('bill_number', ascending=True)

    return bills


def get_bill_status(bills, history):
    """
    Get the most recent status of a bill based on the full bill history.

    Parameters:
    -----------
        bills: DataFrame containing bill data
        history: DataFrame containing the bill history data

    Returns:
    --------
        A DataFrame with status column added.
    """
    # Ensure event_date is in datetime format
    history['event_date'] = pd.to_datetime(history['event_date']) 
    
    # Get latest status for each bill by sorting bill_history df by event_date in descending order
    latest_status = ( 
        history.sort_values('event_date', ascending=False)
               .drop_duplicates(subset='bill_id', keep='first')
               .loc[:, ['bill_id', 'event_text']]
    )
    
    # Merge latest status df with bills df
    bills = bills.merge(latest_status, on='bill_id', how='left')
    
    # Reassign event_text column as status column, then drop event_text column
    bills['status'] = bills['event_text']
    bills.drop(columns=['event_text'], inplace=True)
    
    return bills

###############################################################################

def get_date_introduced(bills, history):
    """
    Get the earliest event_date (i.e. the date_introduced) for each bill and add date_introduced column to bills dataframe.

    Parameters:
    -----------
        bills: DataFrame containing bill data
        history: DataFrame containing the bill history data

    Returns:
    --------
        A DataFrame with date_introduced column added.
    """
    # Ensure event_date is in datetime format
    history['event_date'] = pd.to_datetime(history['event_date'], errors='coerce').dt.strftime('%m-%d-%Y')

    # Get the earliest event_date for each bill_id
    earliest_events = history.loc[history.groupby('bill_id')['event_date'].idxmin()]

    # Select the relevant columns: bill_id, event_date
    earliest_events = earliest_events[['bill_id', 'event_date']]
    
    # Rename column to date_introduced -- VERY IMPORTANT FOR AGRID STYLER FUNCTION TO WORK PROPERLY!!!
    earliest_events.rename(columns={'event_date': 'date_introduced'}, inplace=True)
    
    # Merge with bills df
    bills = bills.merge(earliest_events, on='bill_id', how='left')

    # Return the result
    return bills

###############################################################################

def create_bill_history(bills, history):
    """
    Create a DataFrame with bill_id and a full bill history
    
    Parameters:
        bills: DataFrame containing bill data
        history: DataFrame containing the bill history data
        
    Returns:
        DataFrame with bill_id and combined chunk of bill history text, which will be later formatted via format_bill_history utils function.
    """
    # Ensure event_date is in datetime format
    history['event_date'] = pd.to_datetime(history['event_date'])

    # Create the combined description in the desired format
    history['event_description'] = history['event_date'].dt.strftime('%Y-%m-%d') + " >> " + history['event_text']

    # Group by bill_id and combine all event descriptions into a list
    result = history.groupby('bill_id')['event_description'].apply(list).reset_index()

    # Convert the event_description list into a string format
    result['event_description'] = result['event_description'].apply(lambda x: ', '.join([f'"{event}"' for event in x]))

    # Rename the column to 'bill_history'
    result.rename(columns={'event_description': 'bill_history'}, inplace=True)
    
    # Merge with bills table
    bills = bills.merge(result, on='bill_id', how='left')

    return bills

###############################################################################

def format_bill_history(bill_history):
    '''
    Reformats bill_history variable into a descending chronological list for the bill history section of the bill details page.
    '''
    if not bill_history:
        return ""

    # Split entries using ", " (assuming this is how they are separated)
    entries = bill_history.split(", ")

    # Process entries into tuples (date, event)
    formatted_entries = []
    for entry in entries:
        # Ensure the format is `YYYY-MM-DD >> Event`
        match = re.match(r"^(\d{4}-\d{2}-\d{2})\s*>>\s*(.+)", entry)
        if match:
            date, event = match.groups()
            formatted_entries.append((date, event))

    # Sort by date in descending order
    formatted_entries.sort(reverse=True, key=lambda x: x[0])

    # Format back into readable Markdown-style text
    return "\n\n".join([f"**{date}:** {event}" for date, event in formatted_entries])


###############################################################################

def get_bill_topics(df, keyword_dict):
    """
    Tags each bill in the DataFrame with a topic based on keywords found in the bill_name column.

    Parameters:
        - df (DataFrame): Input DataFrame containing a 'bill_name' column.
        - keywords (dict): A dictionary where keys are tuples of keywords and
                            values are the corresponding topics to apply.

    Returns:
        -df (DataFrame): A DataFrame with a new 'bill_topic' column containing the assigned topic.
    """

    # Initialize the 'bill_topic' column with default value (e.g., "Uncategorized")
    df['bill_topic'] = 'Uncategorized'

    for keywords, label in keyword_dict.items():
        # Ensure the keywords are joined into a single string for regex
        pattern = '|'.join(re.escape(word) for word in keywords)
        # Apply the label where the pattern matches in the bill_name column
        df.loc[df['bill_name'].str.contains(pattern, na=False, case=False), 'bill_topic'] = label

    return df


# Keyword/topic mapping
keywords = {
    ('artificial intelligence', 'algorithm', 'automated'): 'AI',
    ('housing', 'eviction', 'tenant', 'renter'): 'Housing',
    ('worker', 'labor', 'gig economy', 'contract workers', 'content moderator', 'data labeler', 'data labeller', 'ghost work'): 'Labor'
}


###############################################################################

def process_bills_data(bills, history):
    bills = clean_bill_data(bills)  # Step 1: Clean the bills data
    bills = get_bill_status(bills, history)  # Step 2: Get bill status
    bills = get_date_introduced(bills, history)  # Step 3: Get date introduced
    bills = create_bill_history(bills, history)  # Step 4: Create bill history
    bills['bill_history'] = bills['bill_history'].apply(ensure_set).apply(format_bill_history) #Step 5: Format bill history
    bills = get_bill_topics(bills, keywords) # Step 6: Get bill topics
    return bills

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

def display_bill_info_text(selected_rows):
    '''
    Displays bill information as markdown text when a row is selected in
    an Ag Grid data frame.
    '''
    # Extract the values from the selected row
    bill_id = selected_rows['bill_id'].iloc[0]
    bill_number = selected_rows['bill_number'].iloc[0]
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
    topic = selected_rows['bill_topic'].iloc[0]
    
    # Display Bill Info Below the Table
    st.markdown('### Bill Details')
    st.divider()
    
    # Containter with add to dashboard button in the top-right corner
    with st.container(key='title_button_container'):
        col1, col2 = st.columns([7, 3])  # Adjust column widths as needed
        with col1:
            st.markdown(f'### {bill_number}')
        with col2:
            if st.button('Add to Dashboard', use_container_width=True,):
                # Call the function to add the bill to the dashboard
                add_bill_to_dashboard(bill_number, name, author, coauthors, status, date, chamber, link, text, history)
    
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
            st.markdown(name)

            st.markdown('')

            st.markdown('##### Author')
            st.markdown(author)
            
            st.markdown('')

            st.markdown('##### Status')
            st.markdown(status)

        with col2:
            st.markdown('')
        
        with col3:
            st.markdown('##### Chamber')
            st.markdown(chamber)

            st.markdown('')

            st.markdown('##### Co-author(s)')
            st.markdown(coauthors)

            st.markdown('')

            st.markdown('##### Date Introduced')
            st.markdown(date)
        
        with col4:
            st.markdown('')
        
        with col5:
            if topic != 'Uncategorized':
                st.markdown('##### Bill Topic')
                st.markdown(topic)
            else:
                st.markdown('#### ')
                st.markdown('')
            
            st.markdown('')

            st.markdown('##### Legislative Session')
            st.markdown(session)

            st.markdown('')

            st.markdown('##### Link to Bill')
            st.link_button('leginfo.ca.gov', str(link))

    # Add empty rows of space    
    st.write("")
    st.write("")

    # Retrieve saved custom details
    custom_details = get_custom_bill_details(bill_id)

    # Form for custom user-entered fields
    st.markdown('#### Custom Bill Details')
    st.write('Use this section to enter custom details for this bill.')
    with st.form(key='custom_fields', clear_on_submit=False, enter_to_submit=True, border=True):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])

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

        with col4:
            st.markdown('##### Coalition')
            coalition = st.text_input('Enter Coalition', 
                                    value=custom_details['coalition'] if custom_details else '')

        with col5:
            st.markdown('##### Letter of Support')
            letter_of_support = st.text_input('Link to Letter of Support', 
                                            value=custom_details['letter_of_support'] if custom_details else '')

        # Submit button
        submitted = st.form_submit_button("Save Custom Bill Details", 
                                        help='Click to save/update custom details for this bill', 
                                        type='secondary')

        if submitted:
            save_custom_bill_details(bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support)
            st.success("Custom details saved successfully!")

    # Add empty rows of space    
    st.write("")
    st.write("")

    # Expander for bill text
    with st.container(key='bill_text_text'):
        st.markdown('##### Bill Excerpt')
        expander = st.expander('Click to view bill excerpt')
        expander.write(text)

    # Add empty rows of space    
    st.write("")

    # Expander for bill history
    with st.container(key='bill_history_text'):
        st.markdown('##### Bill History')
        expander = st.expander('Click to view bill history')
        expander.markdown(history)


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
