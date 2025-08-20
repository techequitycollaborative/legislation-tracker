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
    @st.cache_data()
    def get_bills():
        # Query the database for bills
        bills = query_table('public', 'bills_2025_2026') # this is pulling a view, not a table
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
    'bill_event', 
    'event_text',
    'assigned_topics',
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
                b.assigned_topics,
                b.last_updated_on
            FROM public.bills_2025_2026 b
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
                b.assigned_topics,
                b.last_updated_on
            FROM public.bills_2025_2026 b
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

def get_custom_bill_details_with_timestamp(openstates_bill_id, org_id):
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
    
    cursor.execute("""
                    SELECT * FROM public.bill_custom_details 
                    WHERE openstates_bill_id = %s AND last_updated_org_id = %s
                    """, (openstates_bill_id, org_id))
    result = cursor.fetchone()

    cursor.close()
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
            # Note: last_updated_on is set to today's date, and last_updated_at is set to the current timestamp
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

##################################################################################

def save_custom_bill_details_with_timestamp(bill_number, org_position, priority_tier, community_sponsor, 
                      coalition, letter_of_support, openstates_bill_id, assigned_to, action_taken, user_email, org_id, org_name):
    '''
    Saves or updates custom bill details for a specific openstates_bill_id and a specific org_id in the bill_custom_details table.
    Records who made the changes (user_email, org_id, org_name) and when (timestamp).
    '''
    # Load the database configuration
    db_config = config('postgres')
    
    # Get current timestamp
    import datetime
    today = datetime.date.today()
    current_timestamp = datetime.datetime.now()
    
    # Establish connection to the PostgreSQL server
    conn = psycopg2.connect(**db_config)
    
    # Create a cursor
    cursor = conn.cursor()
    
    # Check if a record already exists for this bill
    cursor.execute("""
                    SELECT * FROM public.bill_custom_details 
                    WHERE openstates_bill_id = %s AND last_updated_org_id = %s
                """, (openstates_bill_id, org_id))
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
                WHERE openstates_bill_id = %s AND last_updated_org_id = %s
            """,
            (bill_number, org_position, priority_tier, community_sponsor, coalition, letter_of_support, 
             assigned_to, action_taken, user_email, org_id, org_name, today, current_timestamp, openstates_bill_id, org_id)
            )
        else:
            # Insert new record
                cursor.execute("""
                    INSERT INTO public.bill_custom_details
                        (bill_number, org_position, priority_tier, community_sponsor, coalition, 
                        letter_of_support, openstates_bill_id, assigned_to, action_taken, 
                        last_updated_by, last_updated_org_id, last_updated_org_name, 
                        last_updated_on, last_updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (bill_number, org_position, priority_tier, community_sponsor, coalition, 
                letter_of_support, openstates_bill_id, assigned_to, action_taken, 
                user_email, org_id, org_name, today, current_timestamp))
        
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
        cursor.close()
        conn.close()

##################################################################################

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

        
##################################################################################
# Advocacy details functions

def get_all_custom_bill_details():
    """
    Fetches all custom bill details for a specific bill from all organizations.
    For use on the advocacy hub page.
    """
    db_config = config('postgres')
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
        SELECT * FROM public.bill_custom_details
        ORDER BY bill_number ASC
    """, )
    
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in results]


def get_all_custom_bill_details_for_bill(openstates_bill_id):
    """
    Fetch all custom advocacy details for a single bill across all organizations.
    For use on the AI Working Group dashboard.
    """
    db_config = config('postgres')
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
        SELECT * FROM public.bill_custom_details
        WHERE openstates_bill_id = %s
        ORDER BY last_updated_org_name ASC
    """
    cursor.execute(query, (openstates_bill_id,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in results]

###############################################################################

# AI Working Group Dashboard Functions

def add_bill_to_working_group_dashboard(openstates_bill_id, bill_number):
    user_email = st.session_state.get('user_email')
    org_name = st.session_state.get('org_name')
    
    if not openstates_bill_id or not bill_number or not user_email or not org_name:
        st.error("Missing required information to save this bill.")
        return

    try:
        db_config = config('postgres')
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Check if bill already exists for this org/user
        cursor.execute("""
            SELECT COUNT(*) FROM public.working_group_dashboard
            WHERE openstates_bill_id = %s AND added_by_org = %s AND added_by_user = %s;
        """, (openstates_bill_id, org_name, user_email))

        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("""
                INSERT INTO public.working_group_dashboard 
                (openstates_bill_id, bill_number, added_by_org, added_by_user)
                VALUES (%s, %s, %s, %s);
            """, (openstates_bill_id, bill_number, org_name, user_email))

            conn.commit()
            st.success(f'Bill {bill_number} added to Working Group Dashboard!')
        else:
            st.warning(f'Bill {bill_number} is already in the Working Group Dashboard.')

    except Exception as e:
        st.error(f"Error adding bill to Working Group Dashboard: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def remove_bill_from_wg_dashboard(openstates_bill_id, bill_number):
    '''
    Removes a selected bill from the AI working group dashboard, deletes it from the database, and updates session state.
    '''
    db_config = config('postgres')

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM public.working_group_dashboard 
        WHERE openstates_bill_id = %s;
    """, (openstates_bill_id,))
    
    conn.commit()
    st.success(f'Bill {bill_number} removed from AI Working Group dashboard!')
    
    cursor.close()
    conn.close()
    st.rerun()


def get_working_group_bills():
    '''
    Fetches bills from the working_group_dashboard table in the PostgreSQL database.
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
                b.assigned_topics,
                b.last_updated_on
            FROM public.bills_2025_2026 b
            INNER JOIN public.working_group_dashboard wgd
                ON wgd.openstates_bill_id = b.openstates_bill_id;

        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return pd.DataFrame(rows, columns=BILL_COLUMNS) if rows else pd.DataFrame(columns=BILL_COLUMNS)
    
    except Exception as e:
        print(f"Error fetching AI Working Group bills: {e}")
        return pd.DataFrame(columns=BILL_COLUMNS)


def get_discussion_comments(bill_number: str) -> pd.DataFrame:
    '''
    Fetches discussion comments for a specific bill from the working_group_discussions table in the PostgreSQL database.
    '''
    db_config = config('postgres')
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")

    query = """
        SELECT user_email, comment, timestamp
        FROM public.working_group_discussions
        WHERE bill_number = %s
        ORDER BY timestamp DESC;
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (bill_number,))
        records = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(records, columns=columns)

    conn.close()
    print("Database connection closed.")
    return df


def save_comment(bill_number: str, user_email: str, comment: str):
    '''
    Saves a comment to the working group discussion table in the PostgreSQL database.
    '''
    db_config = config('postgres')
    conn = psycopg2.connect(**db_config)
    print("Connected to the PostgreSQL database.")

    query = """
        INSERT INTO public.working_group_discussions (bill_number, user_email, comment, timestamp)
        VALUES (%s, %s, %s, %s);
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (bill_number, user_email, comment, datetime.utcnow()))
        conn.commit()

    conn.close()
    print("Comment inserted and database connection closed.")


def get_ai_members():
    '''
    Get list of names of AI Working Group members from the database.
    '''
    try:
        db_config = config('postgres')
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        query = f"""
            SELECT name, email, org_name
            FROM public.approved_users
            WHERE ai_working_group = 'yes';
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return pd.DataFrame(rows, columns=['name', 'email', 'org_name']) if rows else pd.DataFrame(columns=['name', 'email', 'org_name'])

    except Exception as e:
        print(f"Error fetching AI Working Group members: {e}")
        return []




