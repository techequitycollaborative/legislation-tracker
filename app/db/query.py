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
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)

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
        bills = query_table('public', 'processed_bills_from_snapshot_2025_2026') # this is pulling a view, not a table
        return bills
    
    # Call the cached function to get the data
    bills = get_bills()
    
    return bills

###############################################################################

# MY DASHBOARD FUNCTIONS

# All columns in the bill table
BILL_COLUMNS = [
    'openstates_bill_id', 
    'bill_number', 
    'bill_name', 
    'status', 
    'date_introduced', 
    'leg_session',
    'author', 
    'coauthors', 
    'chamber', 
    'leginfo_link', 
    'bill_text', 
    'bill_history',
    #'bill_topic', 
    'bill_event', 
    'event_text'
]

#@st.cache_data(ttl=120)  #  Cache for 2 mins -- Needs to be turned off for rerun to work for remove bill from dashboard button
def get_my_dashboard_bills(user_email):
    '''
    Fetches bills from the user's dashboard in the database and returns them as a DataFrame.
    
    Parameters: user_email (str)
    Returns: DataFrame of user's saved bills

    '''
    try:
        db_config = config('postgres')
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        query = f"""
            SELECT 
                b.openstates_bill_id,
                b.bill_number,
                b.bill_name,
                b.status,
                b.date_introduced,
                b.leg_session,
                b.author,
                b.coauthors, 
                b.chamber,
                b.leginfo_link,
                b.bill_text,
                b.bill_history,
                b.bill_event,
                b.event_text
            FROM public.processed_bills_from_snapshot_2025_2026 b
            LEFT JOIN public.user_bill_dashboard ubd
                ON ubd.openstates_bill_id = b.openstates_bill_id
            WHERE ubd.user_email = %s;
        """

        cursor.execute(query, (user_email,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return pd.DataFrame(rows, columns=BILL_COLUMNS) if rows else pd.DataFrame(columns=BILL_COLUMNS)
    
    except Exception as e:
        print(f"Error fetching dashboard bills: {e}")
        return pd.DataFrame(columns=BILL_COLUMNS)


def add_bill_to_dashboard(openstates_bill_id, bill_number):
    '''
    Adds a selected bill to the user's dashboard, persists it to the database, and updates session state.
    '''
    user_email = st.session_state['user_email']
    org_id = st.session_state.get('org_id')
    db_config = config('postgres')

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    # Check if bill already exists for this user
    cursor.execute("""
        SELECT COUNT(*) FROM public.user_bill_dashboard 
        WHERE openstates_bill_id = %s AND user_email = %s;
    """, (openstates_bill_id, user_email))
    
    count = cursor.fetchone()[0]

    if count == 0:
        # Insert new tracked bill
        cursor.execute("""
            INSERT INTO public.user_bill_dashboard (user_email, org_id, openstates_bill_id, bill_number)
            VALUES (%s, %s, %s, %s);
        """, (user_email, org_id, openstates_bill_id, bill_number))

        conn.commit()
        st.success(f'Bill {bill_number} added to dashboard!')

        # Optionally refresh dashboard state
        if 'selected_bills' not in st.session_state:
            st.session_state.selected_bills = []  # Initialize as an empty list if it doesn't exist

        # Create a new row as a dictionary
        new_row = {'openstates_bill_id': openstates_bill_id, 'bill_number': bill_number}

        # Append the new row to the selected_bills list
        st.session_state.selected_bills.append(new_row)

    else:
        st.warning(f'Bill {bill_number} is already in your dashboard.')

    cursor.close()
    conn.close()


def remove_bill_from_dashboard(openstates_bill_id, bill_number):
    '''
    Removes a selected bill from the user's dashboard, deletes it from the database, and updates session state.
    '''
    user_email = st.session_state['user_email']
    db_config = config('postgres')

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM public.user_bill_dashboard 
        WHERE openstates_bill_id = %s AND user_email = %s;
    """, (openstates_bill_id, user_email))
    
    conn.commit()
    st.success(f'Bill {bill_number} removed from dashboard!')
    
    cursor.close()
    conn.close()
    st.rerun()

def clear_all_my_dashboard_bills(user_email):
    '''
    Clears ALL bills from the user's personal dashboard, deletes them from the database, and updates session state.
    '''
    user_email = st.session_state['user_email']
    
    db_config = config('postgres')
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM public.user_bill_dashboard WHERE user_email = %s", (user_email,))
    
    conn.commit()
    cursor.close()
    conn.close()
    st.rerun()

###############################################################################

# ORG DASHBOARD FUNCTIONS
def get_org_dashboard_bills(org_id):
    '''
    Fetches bills from the org dashboard in the database and returns them as a DataFrame.
    
    Parameters: org_id (int)
    Returns: DataFrame of organization's saved bills

    '''
    try:
        db_config = config('postgres')
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        query = f"""
            SELECT 
                b.openstates_bill_id,
                b.bill_number,
                b.bill_name,
                b.status,
                b.date_introduced,
                b.leg_session,
                b.author,
                b.coauthors, 
                b.chamber,
                b.leginfo_link,
                b.bill_text,
                b.bill_history,
                b.bill_event,
                b.event_text
            FROM public.processed_bills_from_snapshot_2025_2026 b
            LEFT JOIN public.org_bill_dashboard ubd
                ON ubd.openstates_bill_id = b.openstates_bill_id
            WHERE ubd.org_id = %s;
        """

        cursor.execute(query, (org_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return pd.DataFrame(rows, columns=BILL_COLUMNS) if rows else pd.DataFrame(columns=BILL_COLUMNS)
    
    except Exception as e:
        print(f"Error fetching dashboard bills: {e}")
        return pd.DataFrame(columns=BILL_COLUMNS)


def add_bill_to_org_dashboard(openstates_bill_id, bill_number):
    '''
    Adds a selected bill to the user's ORG dashboard, persists it to the database, and updates session state.
    '''
    user_email = st.session_state['user_email']
    org_id = st.session_state.get('org_id')
    db_config = config('postgres')

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    # Check if bill already exists for this org
    cursor.execute("""
        SELECT COUNT(*) FROM public.org_bill_dashboard 
        WHERE openstates_bill_id = %s AND org_id = %s;
    """, (openstates_bill_id, org_id))
    
    count = cursor.fetchone()[0]

    if count == 0:
        # Insert new tracked bill
        cursor.execute("""
            INSERT INTO public.org_bill_dashboard (user_email, org_id, openstates_bill_id, bill_number)
            VALUES (%s, %s, %s, %s);
        """, (user_email, org_id, openstates_bill_id, bill_number))

        conn.commit()
        st.success(f'Bill {bill_number} added to dashboard!')

        # Optionally refresh dashboard state
        if 'selected_bills' not in st.session_state:
            st.session_state.selected_bills = []  # Initialize as an empty list if it doesn't exist

        # Create a new row as a dictionary
        new_row = {'openstates_bill_id': openstates_bill_id, 'bill_number': bill_number}

        # Append the new row to the selected_bills list
        st.session_state.selected_bills.append(new_row)

    else:
        st.warning(f'Bill {bill_number} is already in your dashboard.')

    cursor.close()
    conn.close()


def remove_bill_from_org_dashboard(openstates_bill_id, bill_number):
    '''
    Removes a selected bill from the user's ORG dashboard, deletes it from the database, and updates session state.
    '''
    user_email = st.session_state['user_email']
    org_id = st.session_state.get('org_id')
    db_config = config('postgres')

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM public.org_bill_dashboard 
        WHERE openstates_bill_id = %s AND org_id = %s;
    """, (openstates_bill_id, org_id))
    
    conn.commit()
    st.success(f'Bill {bill_number} removed from dashboard!')
    
    cursor.close()
    conn.close()
    st.rerun()

###############################################################################

def get_custom_bill_details(openstates_bill_id):
    '''
    Fetches custom bill details for a specific openstates_bill_id from the bill_custom_details table in postgres and adds to the bills details page
    '''
    # Load the database configuration
    db_config = config('postgres')
    
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")
    
    # Query
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM public.bill_custom_details WHERE openstates_bill_id = %s", (openstates_bill_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "org_position": result[3],
            "priority_tier": result[4],
            "community_sponsor": result[5],
            #"coalition": result[6],
            "letter_of_support": result[7]
        }
    
    else:
        return None

###############################################################################

def save_custom_bill_details(openstates_bill_id, bill_number, org_position, priority_tier, community_sponsor, letter_of_support):
    '''
    Saves custom fields that a user enters on the bills details page to the bill_custom_details table in postgres
    '''
    # Load the database configuration
    db_config = config('postgres')

    # Ensure bill_id is an integer
    #bill_id = int(bill_id)
    
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")
    cursor = conn.cursor()
    
    # Check if the record exists in database
    cursor.execute("SELECT * FROM public.bill_custom_details WHERE openstates_bill_id = %s", (openstates_bill_id,))
    existing_record = cursor.fetchone()

    if existing_record:
            # If it exists, update the record
            cursor.execute("""
                UPDATE public.bill_custom_details
                SET org_position = %s, priority_tier = %s, community_sponsor = %s, letter_of_support = %s
                WHERE openstates_bill_id = %s
            """, (bill_number, org_position, priority_tier, community_sponsor, letter_of_support, openstates_bill_id))
    else:
            # If it doesn't exist, insert a new record
            cursor.execute("""
                INSERT INTO public.bill_custom_details (openstates_bill_id, org_position, priority_tier, community_sponsor, letter_of_support)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (openstates_bill_id, bill_number, org_position, priority_tier, community_sponsor, letter_of_support))

    conn.commit()
    conn.close()


