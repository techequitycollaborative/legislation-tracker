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
            "org_position": result[3],
            "priority_tier": result[4],
            "community_sponsor": result[5],
            "coalition": result[6],
            "letter_of_support": result[7]
        }
    
    else:
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
    
    # Check if the record exists in database
    cursor.execute("SELECT * FROM public.bill_custom_details WHERE bill_id = %s", (bill_id,))
    existing_record = cursor.fetchone()

    if existing_record:
            # If it exists, update the record
            cursor.execute("""
                UPDATE public.bill_custom_details
                SET org_position = %s, priority_tier = %s, community_sponsor = %s,
                    coalition = %s, letter_of_support = %s
                WHERE bill_id = %s
            """, (bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support, bill_id))
    else:
            # If it doesn't exist, insert a new record
            cursor.execute("""
                INSERT INTO public.bill_custom_details (bill_id, org_position, priority_tier, community_sponsor, coalition, letter_of_support)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support))

    conn.commit()
    conn.close()
