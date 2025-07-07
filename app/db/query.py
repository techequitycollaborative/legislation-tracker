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
import psycopg2.extras
from db.config import config
import numpy as np
import datetime
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
    #'bill_topic', # This is not in the processed bills table in the db, so we don't include it here
    'bill_event', 
    'event_text',
    'last_updated_on'
]

# All columns in the committee table
COMMITTEE_COLUMNS = [
    "committee_id",
    "committee_name",
    "chamber",
    "next_hearing",
    "committee_chair",
    "committee_vice_chair",
    "total_members",
    "webpage_link", 
    "chamber_id", 
    "committee_members",
    "member_count"
]

# All columns in the legislator view
LEGISLATOR_COLUMNS = [
    "openstates_people_id",
    "name",
    "party",
    "chamber",
    "district",
    "other_names",
    "ext_sources",
    "office_details",
    "issue_contacts",
    "last_updated_on"
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
                b.event_text,
                b.last_updated_on
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
        #if 'selected_bills' not in st.session_state:
        #    st.session_state.selected_bills = []  # Initialize as an empty list if it doesn't exist

        # Create a new row as a dictionary
        #new_row = {'openstates_bill_id': openstates_bill_id, 'bill_number': bill_number}

        # Append the new row to the selected_bills list
        #st.session_state.selected_bills.append(new_row)

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
                b.event_text,
                b.last_updated_on
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
        #raise -- only for local debugging, not for production use as it could break the app if the database is down or the query fails
    

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
        #if 'selected_bills' not in st.session_state:
        #    st.session_state.selected_bills = []  # Initialize as an empty list if it doesn't exist

        # Create a new row as a dictionary
        #new_row = {'openstates_bill_id': openstates_bill_id, 'bill_number': bill_number}

        # Append the new row to the selected_bills list
        #st.session_state.selected_bills.append(new_row)

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
    Fetches custom bill details for a specific openstates_bill_id from the bill_custom_details table in postgres and renders in the bill details page.
    '''
    # Load the database configuration
    db_config = config('postgres')
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")
    
    # Create a cursor that returns rows as dictionaries
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT * FROM public.bill_custom_details WHERE openstates_bill_id = %s", (openstates_bill_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "org_position": result["org_position"],
            "priority_tier": result["priority_tier"],
            "community_sponsor": result["community_sponsor"],
            "coalition": result["coalition"],
            "letter_of_support": result["letter_of_support"],
            "assigned_to": result["assigned_to"],
            "action_taken": result["action_taken"],
        }
    else:
        return None
    

def get_custom_bill_details_with_timestamp(openstates_bill_id):
    '''
    Fetches custom bill details for a specific openstates_bill_id from the bill_custom_details table in postgres and renders in the bill details page, 
    along with the timestamp of the last update and the user who made the changes.
    '''
    # Load the database configuration
    db_config = config('postgres')
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")
    
    # Create a cursor that returns rows as dictionaries
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT * FROM public.bill_custom_details WHERE openstates_bill_id = %s", (openstates_bill_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "org_position": result["org_position"],
            "priority_tier": result["priority_tier"],
            "community_sponsor": result["community_sponsor"],
            "coalition": result["coalition"],
            "letter_of_support": result["letter_of_support"],
            "assigned_to": result["assigned_to"],
            "action_taken": result["action_taken"],
            "last_updated_by": result["last_updated_by"],
            "last_updated_org_id": result["last_updated_org_id"],
            "last_updated_org_name": result["last_updated_org_name"],
            "last_updated_on": result["last_updated_on"],
            "last_updated_at": result["last_updated_on"],
        }
    else:
        return None

def get_custom_contact_details_with_timestamp(openstates_people_id):
    '''
    Fetches custom contact details for a specific openstates_people_id from the contact_custom_details table in postgres
    '''
    # Load the database configuration
    db_config = config('postgres')
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")
    
    # Create a cursor that returns rows as dictionaries
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT * FROM public.contact_custom_details WHERE openstates_people_id = '{}'".format(openstates_people_id))
    result = cursor.fetchall() # There can be more than one custom contact detail
    conn.close()
    
    if result:
        return result
    else:
        return None
###############################################################################

def save_custom_bill_details(openstates_bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support, assigned_to, action_taken):
    '''
    Saves or updates custom bill details for a specific openstates_bill_id in the bill_custom_details table
    '''
    # Load the database configuration
    db_config = config('postgres')
    
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    
    # Create a cursor
    cursor = conn.cursor()
    
    # Check if a record already exists for this bill
    cursor.execute("SELECT 1 FROM public.bill_custom_details WHERE openstates_bill_id = %s", (openstates_bill_id,))
    exists = cursor.fetchone()
    
    if exists:
        # Update existing record
        cursor.execute("""
            UPDATE public.bill_custom_details 
            SET bill_number = %s,
                org_position = %s,
                priority_tier = %s,
                community_sponsor = %s,
                coalition = %s,      
                letter_of_support = %s,
                assigned_to = %s,
                action_taken = %s
            WHERE openstates_bill_id = %s
            """, 
            (bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support, assigned_to, action_taken, openstates_bill_id)
        )
    else:
        # Insert new record
        cursor.execute("""
            INSERT INTO public.bill_custom_details 
            (openstates_bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support, assigned_to, action_taken)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (openstates_bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support, assigned_to, action_taken)
        )
    
    # Commit the transaction
    conn.commit()
    conn.close()
    
    print(f"Custom details for bill {bill_number} saved successfully.")


##################################################################################

def save_custom_bill_details_with_timestamp(openstates_bill_id, bill_number, org_position, priority_tier, community_sponsor, 
                      coalition, letter_of_support, assigned_to, action_taken, user_email=None, org_id=None, org_name=None):
    '''
    Saves or updates custom bill details for a specific openstates_bill_id in the bill_custom_details table and records who made the changes (user_email, org_id, org_name) and when (timestamp).
    '''
    # Load the database configuration
    db_config = config('postgres')
    
    # Get current timestamp
    today = datetime.date.today()
    current_timestamp = datetime.datetime.now()
    
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    
    # Create a cursor
    cursor = conn.cursor()
    
    # Check if a record already exists for this bill
    cursor.execute("SELECT 1 FROM public.bill_custom_details WHERE openstates_bill_id = %s", (openstates_bill_id,))
    exists = cursor.fetchone()
    
    try:
        if exists:
            # Update existing record
            cursor.execute("""
                UPDATE public.bill_custom_details
                SET bill_number = %s,
                    org_position = %s,
                    priority_tier = %s,
                    community_sponsor = %s,
                    coalition = %s,
                    letter_of_support = %s,
                    assigned_to = %s,
                    action_taken = %s,
                    last_updated_by = %s,
                    last_updated_org_id = %s,
                    last_updated_org_name = %s,
                    last_updated_on = %s,
                    last_updated_at = %s
                WHERE openstates_bill_id = %s
            """,
            (bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support, 
             assigned_to, action_taken, user_email, org_id, org_name, today, current_timestamp, openstates_bill_id)
            )
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO public.bill_custom_details
                (openstates_bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, 
                 letter_of_support, assigned_to, action_taken, last_updated_by, last_updated_org_id, 
                 last_updated_org_name, last_updated_on, last_updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (openstates_bill_id, bill_number, org_position, priority_tier, community_sponsor, coalition, 
             letter_of_support, assigned_to, action_taken, user_email, org_id, org_name, today, current_timestamp)
            )
        
        # Commit the transaction
        conn.commit()
        print(f"Custom details for bill {bill_number} saved successfully by {user_email} from {org_name}.")
        return True
        
    except Exception as e:
        # Roll back the transaction in case of error
        conn.rollback()
        print(f"Error saving custom details for bill {bill_number}: {str(e)}")
        raise e
        
    finally:
        # Always close the connection
        conn.close()


def save_custom_contact_details_with_timestamp(
        contact_update_df,
        openstates_people_id,
        user_email=None, 
        org_id=None, 
        org_name=None
        ):
    '''
    Saves or updates custom contact details for a specific openstates_people_id in the contact_custom_details table and records who made the changes (user_email, org_id, org_name) and when (timestamp).
    '''
    # Load the database configuration
    db_config = config('postgres')
    
    today = datetime.date.today()
    
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    
    # Create a cursor
    cursor = conn.cursor()
    
    
    try:
        # Save updated data to a temporary table which drops after updates are committed
        cursor.execute("""
        CREATE TEMP TABLE temp_updates (
            people_contact_id INT PRIMARY KEY,
            openstates_people_id TEXT,
            custom_staffer_contact TEXT,
            custom_staffer_email TEXT,
            last_updated_by TEXT,
            last_updated_org_id INT,
            last_updated_org_name TEXT,
            last_updated_on DATE      
        ) ON COMMIT DROP
        """)
        
        # Insert updates to temp table
        for _, row in contact_update_df.iterrows():
            print(row)
            cursor.execute("""
                INSERT INTO temp_updates
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::date)
            """, (row['people_contact_id'], openstates_people_id, row['custom_contact'], row['custom_email'], user_email, org_id, org_name, today))
        
        # Apply updates to prod table
        cursor.execute("""
        INSERT INTO public.contact_custom_details 
        (people_contact_id, openstates_people_id, custom_staffer_contact, custom_staffer_email, last_updated_by, last_updated_org_id, last_updated_org_name, last_updated_on)
        SELECT *
        FROM temp_updates
        ON CONFLICT (people_contact_id) DO UPDATE SET
            custom_staffer_contact = EXCLUDED.custom_staffer_contact,
            custom_staffer_email = EXCLUDED.custom_staffer_email,
            last_updated_by = EXCLUDED.last_updated_by,
            last_updated_org_id = EXCLUDED.last_updated_org_id,
            last_updated_org_name = EXCLUDED.last_updated_org_name,
            last_updated_on = EXCLUDED.last_updated_on            
        """)
        conn.commit()
        return True
        
    except Exception as e:
        # Roll back the transaction in case of error
        conn.rollback()
        print(f"Error saving custom details for point of contact: {str(e)}")
        raise e
        
    finally:
        # Always close the connection
        conn.close()