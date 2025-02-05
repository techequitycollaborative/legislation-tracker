#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
query.py

Functions for querying tables from postgreSQL database and pulling into python

Date: Jan 15. 2025
@author: danyasherbini
"""

import streamlit as st
import pandas as pd
import psycopg2
from db.config import config

###############################################################################

def query_table(schema, table):
    """
    Parameters
    ----------
    schema : str
        The schema name in the PostgreSQL database.
    table : str
        The table name in the PostgreSQL database.

    Returns
    -------
    pd.DataFrame
        The queried table in DataFrame format.
    """
    
    # Load the database configuration
    db_config = config('postgres')
    
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")
    
    # Define SQL query
    query = f'SELECT * FROM {schema}.{table};'
    
    # Query the table and convert to a DataFrame
    with conn.cursor() as cursor:
        cursor.execute(query)
        records = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(records, columns=columns)
    
    # Close the connection
    conn.close()
    print("Database connection closed.")
    
    return df


###############################################################################

# Query bill tables -- processing of which has already been done in postgres database
# Cache these functions so database query functions don't reload every time the app
# reruns (i.e. if the user interacts with the table)

def get_data():
    """
    Use query_table to load main bills table (or view) and cache it.
    """
    # Cache the function that retrieves the data
    @st.cache_data
    def get_bills():
        # Query the database for bills
        bills = query_table('public', 'processed_bills_20252026') # this is pulling a view, not a table
        return bills
    
    # Call the cached function to get the data
    bills = get_bills()
    
    return bills

###############################################################################

def get_custom_bill_details(bill_id):
    '''
    Fetches custom bill details for a specific bill_id from the bill_custom_details table in postgres and adds to the bills details page
    '''
    # Load the database configuration
    db_config = config('postgres')
    
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")
    
    # Query
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM public.bill_custom_details WHERE bill_id = %s", (int(bill_id),))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "bill_number": result[2],
            "org_position": result[3],
            "priority_tier": result[4],
            "community_sponsor": result[5],
            "coalition": result[6],
            "letter_of_support": result[7]
        }
    return None

###############################################################################

def save_custom_bill_details(bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support):
    '''
    Saves custom fields that a user enters on the bills details page to the bill_custom_details table in postgres
    '''
    # Load the database configuration
    db_config = config('postgres')

    # Ensure bill_id is an integer
    bill_id = int(bill_id)
    
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO public.bill_custom_details (bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (bill_id) 
        DO UPDATE SET 
            org_position = EXCLUDED.org_position,
            priority_tier = EXCLUDED.priority_tier,
            community_sponsor = EXCLUDED.community_sponsor,
            coalition = EXCLUDED.coalition,
            letter_of_support = EXCLUDED.letter_of_support;
    """, (bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support))
    
    conn.commit()
    conn.close()

###############################################################################

def get_my_dashboard_bills(user_email):
    try:
        # Load the database configuration
        db_config = config('postgres')
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Fetch bills for the user
        cursor.execute("""
            SELECT bill_id, bill_number, bill_name, status, date_introduced, leg_session, 
                   author, coauthors, chamber, leginfo_link, full_text, bill_history, bill_topic
            FROM public.user_bill_dashboard
            WHERE user_email = %s;
        """, (user_email,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Ensure there's always a DataFrame
        if rows:
            df = pd.DataFrame(rows, columns=['bill_id', 'bill_number', 'bill_name', 'status', 'date_introduced', 
                                             'leg_session', 'author', 'coauthors', 'chamber', 'leginfo_link', 
                                             'full_text', 'bill_history', 'bill_topic'])
        else:
            df = pd.DataFrame(columns=['bill_id', 'bill_number', 'bill_name', 'status', 'date_introduced', 
                                       'leg_session', 'author', 'coauthors', 'chamber', 'leginfo_link', 
                                       'full_text', 'bill_history', 'bill_topic'])

        return df

    except Exception as e:
        print(f"Error fetching dashboard bills: {e}")
        return pd.DataFrame(columns=['bill_id', 'bill_number', 'bill_name', 'status', 'date_introduced', 
                                     'leg_session', 'author', 'coauthors', 'chamber', 'leginfo_link', 
                                     'full_text', 'bill_history', 'bill_topic'])  # Return an empty DataFrame


###############################################################################

def add_bill_to_dashboard_with_db(bill_id, bill_number, bill_name, status, date_introduced, leg_session, 
                              author, coauthors, chamber, leginfo_link, full_text, bill_history, bill_topic):
    """
    Adds a selected bill to the user's dashboard, persists it to the database, and updates session state.
    """
    # Get user email from session state
    user_email = st.session_state['user_info'].get('email')

    # Load the database configuration
    db_config = config('postgres')

    # Ensure bill_id is an integer
    bill_id = int(bill_id)

    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    # Check if the bill is already in the database for the logged-in user
    cursor.execute("""
        SELECT COUNT(*) FROM public.user_bill_dashboard 
        WHERE bill_id = %s AND user_email = %s;
    """, (bill_id, user_email))
    count = cursor.fetchone()[0]

    # If the bill is not already in the database, insert it
    if count == 0:
        cursor.execute("""
            INSERT INTO public.user_bill_dashboard (user_email, bill_id, bill_number, bill_name, status, date_introduced, 
                                             leg_session, author, coauthors, chamber, leginfo_link, full_text, 
                                             bill_history, bill_topic)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (user_email, bill_id, bill_number, bill_name, status, date_introduced, leg_session, 
              author, coauthors, chamber, leginfo_link, full_text, bill_history, bill_topic))

        conn.commit()  # Commit the transaction
        st.success(f'Bill {bill_number} added to dashboard!')

        # Add the bill to session state if not already present
        if 'selected_bills' not in st.session_state:
            st.session_state.selected_bills = []

        if not any(bill['bill_id'] == bill_id for bill in st.session_state.selected_bills):
            bill = {
                'bill_id': bill_id,
                'bill_number': bill_number,
                'bill_name': bill_name,
                'status': status,
                'date_introduced': date_introduced,
                'leg_session': leg_session,
                'author': author,
                'coauthors': coauthors,
                'chamber': chamber,
                'leginfo_link': leginfo_link,
                'full_text': full_text,
                'bill_history': bill_history,
                'bill_topic': bill_topic
            }
            st.session_state.selected_bills.append(bill)

    else:
        st.warning(f'Bill {bill_number} is already in your dashboard.')

    # Close connection
    cursor.close()
    conn.close()


###############################################################################

def remove_bill_from_dashboard(bill_id):
    """
    Removes a selected bill from the user's dashboard, deletes it from the database, and updates session state.
    """
    # Get user email from session state
    user_email = st.session_state['user_info'].get('email')

    # Load the database configuration
    db_config = config('postgres')

    # Ensure bill_id is an integer
    bill_id = int(bill_id)

    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Delete the bill from the database for the logged-in user
    cursor.execute("""
        DELETE FROM public.user_bill_dashboard 
        WHERE bill_id = %s AND user_email = %s;
    """, (bill_id, user_email))
    
    conn.commit()  # Commit the transaction
    st.success(f'Bill {bill_id} removed from dashboard!')

    # Remove the bill from session state if it exists
    if 'selected_bills' in st.session_state:
        st.session_state.selected_bills = [
            bill for bill in st.session_state.selected_bills if bill['bill_id'] != bill_id
        ]

    # Close connection
    cursor.close()
    conn.close()

