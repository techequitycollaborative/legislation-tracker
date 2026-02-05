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
from db.connect import get_connection
import numpy as np
import datetime
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)
import sys
sys.path.append("..")
from utils.profiling import profile, timer, logger

###############################################################################
class Query:
    def __init__(
            self, 
            page_name, 
            query,
            df_columns=None, 
            error_msg="",
            warning_msg="",
            success_msg="Query successful.", 
        ):
        self.name = page_name
        self.query = query
        self.df_columns = df_columns
        self.error_message = error_msg
        self.warning_message = warning_msg
        self.success_message = success_msg
    
    @profile("query.py - Query object fetch records")
    def fetch_records(self):
        with get_connection() as conn:
            logger.info(f"Connected to PostgreSQL database.")
            # Default empty set value in case there are no records to fetch
            records = []

            with conn.cursor() as cursor:
                cursor.execute(self.query)
                records = cursor.fetchall()

                if self.df_columns == None:
                    self.df_columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(records, columns=self.df_columns)

        logger.info(f"Database connection closed.")

        return df
    
    @profile("query.py - Query object check if record exists")
    def check_for_record(self):
        with get_connection() as conn:

            with conn.cursor() as cursor:
                cursor.execute(self.query)
                count = cursor.fetchone()[0]
            
            if not count:
                st.warning(self.warning_message)

        return bool(count)
    
    @profile("query.py - Query object update records and rerun Streamlit")
    def update_records(self):
        with get_connection() as conn:
            logger.info(f"Connected to PostgreSQL database.")

            with conn.cursor() as cursor:
                cursor.execute(self.query)
                conn.commit()

        # Clear the cache so data reloads
        st.cache_data.clear()
        st.rerun()

        st.success(self.success_message)
        return

###############################################################################

@profile("query.py - query_table func")
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
    with get_connection() as conn:
        print("Connected to the PostgreSQL database.")
        
        # Define SQL query
        query = f'SELECT * FROM {schema}.{table};'
        
        # Query the table and convert to a DataFrame
        with conn.cursor() as cursor:
            cursor.execute(query)
            records = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(records, columns=columns)
    
    return df
    
# ###############################################################################

# # Query bill tables -- processing of which has already been done in postgres database
# # Cache these functions so database query functions don't reload every time the app
# # reruns (i.e. if the user interacts with the table)

# def get_data():
#     """
#     Use query_table to load main bills table (or view) and cache it.
#     """
#     # Cache the function that retrieves the data
#     def get_bills():
#         # Query the database for bills
#         bills = query_table('app', 'bills_2025_2026') # this is pulling a view, not a table
#         return bills
    
#     # Call the cached function to get the data
#     bills = get_bills()
    
#     return bills

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
# All columns for org dashboard (bill details + custom org details)
BILL_COLUMNS_WITH_DETAILS = [
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
    'last_updated_on',
    #'org_id',
    'org_position',
    #'priority_tier',
    #'community_sponsor',
    #'coalition',
    'assigned_to',
    #'action_taken'
]

@profile("query.py - get_my_dashboard_bills")
@st.cache_data(ttl=120)  #  Cache for 2 mins 
def get_my_dashboard_bills(user_email):
    '''
    Fetches bills from the user's dashboard in the database and returns them as a DataFrame.
    
    Parameters: user_email (str)
    Returns: DataFrame of user's saved bills

    '''
    with get_connection() as conn:
        try:
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
                FROM app.bills_mv b
                LEFT JOIN app.user_bill_dashboard ubd
                    ON ubd.openstates_bill_id = b.openstates_bill_id
                WHERE ubd.user_email = %s;
            """

            cursor.execute(query, (user_email,))
            rows = cursor.fetchall()

            return pd.DataFrame(rows, columns=BILL_COLUMNS) if rows else pd.DataFrame(columns=BILL_COLUMNS)
        
        except Exception as e:
            print(f"Error fetching dashboard bills: {e}")
            return pd.DataFrame(columns=BILL_COLUMNS)

@profile("query.py - add_bill_to_dashboard")
def add_bill_to_dashboard(openstates_bill_id, bill_number):
    '''
    Adds a selected bill to the user's dashboard, persists it to the database, and updates session state.
    '''
    user_email = st.session_state['user_email']
    org_id = st.session_state.get('org_id')
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if bill already exists for this user
        cursor.execute("""
            SELECT COUNT(*) FROM app.user_bill_dashboard 
            WHERE openstates_bill_id = %s AND user_email = %s;
        """, (openstates_bill_id, user_email))
        
        count = cursor.fetchone()[0]

        if count == 0:
            # Insert new tracked bill
            cursor.execute("""
                INSERT INTO app.user_bill_dashboard (user_email, org_id, openstates_bill_id, bill_number)
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

@profile("query.py - remove_bill_from_dashboard")
def remove_bill_from_dashboard(openstates_bill_id, bill_number):
    '''
    Removes a selected bill from the user's dashboard, deletes it from the database, and updates session state.
    '''
    user_email = st.session_state['user_email']
    

    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM app.user_bill_dashboard 
            WHERE openstates_bill_id = %s AND user_email = %s;
        """, (openstates_bill_id, user_email))
    
        conn.commit() #TODO: do we need this?
        
    # Clear the cache so data reloads
    st.cache_data.clear()
    
    st.success(f'Bill {bill_number} removed from dashboard!')
    st.rerun()

@profile("query.py - clear_all_my_dashboard_bills")
def clear_all_my_dashboard_bills():
    '''
    Clears ALL bills from the user's personal dashboard, deletes them from the database, and updates session state.
    '''    
    
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM app.user_bill_dashboard WHERE user_email = %s", (st.session_state['user_email'],))
        
        conn.commit()

    # Clear the cache so data reloads
    st.cache_data.clear()
    
    st.success('Your dashboard has been cleared!')

    st.rerun()

###############################################################################

# ORG DASHBOARD FUNCTIONS
@profile("query.py - get_org_dashboard_bills")
@st.cache_data(ttl=60)  #  Cache for 1 min
def get_org_dashboard_bills(org_id):
    '''
    Fetches bills from the org dashboard in the database and returns them as a DataFrame.
    
    Parameters: org_id (int)
    Returns: DataFrame of organization's saved bills

    '''
    with get_connection() as conn:
        try:
            cursor = conn.cursor()

            query = f"""
                SELECT 
                    openstates_bill_id,
                    bill_number,
                    bill_name,
                    status,
                    date_introduced,
                    leg_session,
                    author,
                    coauthors, 
                    chamber,
                    leginfo_link,
                    bill_text,
                    bill_history,
                    bill_event,
                    event_text,
                    assigned_topics,
                    last_updated_on,
                    org_position,
                    assigned_to
                FROM app.org_bill_dashboard_custom
                WHERE org_id = %s;
            """

            cursor.execute(query, (org_id,))
            rows = cursor.fetchall()

            return pd.DataFrame(rows, columns=BILL_COLUMNS_WITH_DETAILS) if rows else pd.DataFrame(columns=BILL_COLUMNS_WITH_DETAILS)
        
        except Exception as e:
            print(f"Error fetching dashboard bills: {e}")
            return pd.DataFrame(columns=BILL_COLUMNS_WITH_DETAILS)
            #raise -- only for local debugging, not for production use as it could break the app if the database is down or the query fails
    
@profile("query.py - add_bill_to_org_dashboard")
def add_bill_to_org_dashboard(openstates_bill_id, bill_number):
    '''
    Adds a selected bill to the user's ORG dashboard, persists it to the database, and updates session state.
    '''
    user_email = st.session_state['user_email']
    org_id = st.session_state.get('org_id')
    

    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if bill already exists for this org
        cursor.execute("""
            SELECT COUNT(*) FROM app.org_bill_dashboard 
            WHERE openstates_bill_id = %s AND org_id = %s;
        """, (openstates_bill_id, org_id))
        
        count = cursor.fetchone()[0]

        if count == 0:
            # Insert new tracked bill
            cursor.execute("""
                INSERT INTO app.org_bill_dashboard (user_email, org_id, openstates_bill_id, bill_number)
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

@profile("query.py - remove_bill_from_org_dashboard")
def remove_bill_from_org_dashboard(openstates_bill_id, bill_number):
    '''
    Removes a selected bill from the user's ORG dashboard, deletes it from the database, and updates session state.
    '''
    user_email = st.session_state['user_email']
    org_id = st.session_state.get('org_id')
    

    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM app.org_bill_dashboard 
            WHERE openstates_bill_id = %s AND org_id = %s;
        """, (openstates_bill_id, org_id))
        
        conn.commit()
    

    # Clear the cache so data reloads
    st.cache_data.clear()

    st.success(f'Bill {bill_number} removed from dashboard!')
    st.rerun()

###############################################################################
@profile("query.py - get_custom_bill_details_with_timestamp")
@st.cache_data(ttl=120)  #  Cache for 2 mins 
def get_custom_bill_details_with_timestamp(openstates_bill_id, org_id):
    '''
    Fetches custom bill details for a specific openstates_bill_id from the bill_custom_details table in postgres and renders in the bill details page, 
    along with the timestamp of the last update and the user who made the changes.
    '''
    result = None
    # Establish connection to the PostgreSQL server
    with get_connection() as conn:
        print("Connected to the PostgreSQL database.")
        
        # Create a cursor that returns rows as dictionaries
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
                        SELECT * FROM app.bill_custom_details 
                        WHERE openstates_bill_id = %s AND last_updated_org_id = %s
                        """, (openstates_bill_id, org_id))
        result = cursor.fetchone()
    
    if result != None:
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
        return result

@profile("query.py - get_custom_contact_details_with_timestamp")
@st.cache_data(ttl=120)  #  Cache for 2 mins 
def get_custom_contact_details_with_timestamp(openstates_people_id):
    '''
    Fetches custom contact details for a specific openstates_people_id from the contact_custom_details table in postgres
    '''
    # Load the database configuration
    
    # Establish connection to the PostgreSQL server
    with get_connection() as conn:
        print("Connected to the PostgreSQL database.")
        
        # Create a cursor that returns rows as dictionaries
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("SELECT * FROM app.contact_custom_details WHERE openstates_people_id = '{}'".format(openstates_people_id))
        result = cursor.fetchall() # There can be more than one custom contact detail

    if result:
        return result
    else:
        return None

##################################################################################
@profile("query.py - save_custom_bill_details_with_timestamp")
def save_custom_bill_details_with_timestamp(bill_number, org_position, priority_tier, 
                    community_sponsor, coalition, openstates_bill_id, 
                    assigned_to, action_taken, user_email, org_id, org_name):
    '''
    Saves or updates custom bill details and logs all field changes to history.
    '''
    import datetime
    today = datetime.date.today()
    current_timestamp = datetime.datetime.now()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Fetch existing record to compare changes
        cursor.execute("""
            SELECT org_position, priority_tier, community_sponsor, coalition, 
                assigned_to, action_taken
            FROM app.bill_custom_details 
            WHERE openstates_bill_id = %s AND last_updated_org_id = %s
        """, (openstates_bill_id, org_id))
        existing = cursor.fetchone()
        
        # Define field mappings for comparison
        new_values = {
            'org_position': org_position,
            'priority_tier': priority_tier,
            'community_sponsor': community_sponsor,
            'coalition': coalition,
            'assigned_to': assigned_to,
            'action_taken': action_taken
        }
        
        try:
            # Log changes if record exists
            if existing:
                old_values = {
                    'org_position': existing[0],
                    'priority_tier': existing[1],
                    'community_sponsor': existing[2],
                    'coalition': existing[3],
                    'assigned_to': existing[4],      # Fixed: was existing[5]
                    'action_taken': existing[5]      # Fixed: was existing[6]
                }
                
                # Log each changed field
                for field_name, new_value in new_values.items():
                    old_value = old_values[field_name]
                    if old_value != new_value:
                        cursor.execute("""
                            INSERT INTO app.bill_custom_details_history
                            (openstates_bill_id, bill_number, org_id, org_name, 
                            field_name, old_value, new_value, changed_by, 
                            changed_on, changed_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (openstates_bill_id, bill_number, org_id, org_name,
                            field_name, old_value, new_value, user_email,
                            today, current_timestamp))
            else:
                # Log initial creation for all non-null fields
                for field_name, new_value in new_values.items():
                    if new_value:  # Only log fields that have values
                        cursor.execute("""
                            INSERT INTO app.bill_custom_details_history
                            (openstates_bill_id, bill_number, org_id, org_name, 
                            field_name, old_value, new_value, changed_by, 
                            changed_on, changed_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (openstates_bill_id, bill_number, org_id, org_name,
                            field_name, None, new_value, user_email,
                            today, current_timestamp))
            
            # Now update/insert the main record
            if existing:
                cursor.execute("""
                    UPDATE app.bill_custom_details
                    SET bill_number = %s, org_position = %s, priority_tier = %s,
                        community_sponsor = %s, coalition = %s,
                        assigned_to = %s, action_taken = %s, last_updated_by = %s,
                        last_updated_org_id = %s, last_updated_org_name = %s,
                        last_updated_on = %s, last_updated_at = %s
                    WHERE openstates_bill_id = %s AND last_updated_org_id = %s
                """, (bill_number, org_position, priority_tier, community_sponsor, 
                    coalition, assigned_to, action_taken, 
                    user_email, org_id, org_name, today, current_timestamp, 
                    openstates_bill_id, org_id))
            else:
                cursor.execute("""
                    INSERT INTO app.bill_custom_details
                    (bill_number, org_position, priority_tier, community_sponsor, 
                    coalition, openstates_bill_id, assigned_to, 
                    action_taken, last_updated_by, last_updated_org_id, 
                    last_updated_org_name, last_updated_on, last_updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (bill_number, org_position, priority_tier, community_sponsor, 
                    coalition, openstates_bill_id, assigned_to, 
                    action_taken, user_email, org_id, org_name, today, current_timestamp))
            
            conn.commit()
            print(f"Custom details for bill {bill_number} saved with change history.")
            
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving custom details: {str(e)}")
            raise e

##################################################################################
@profile("query.py - save_custom_contact_details_with_timestamp")
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
    
    
    today = datetime.date.today()
    
    # Establish connection to the PostgreSQL server
    with get_connection() as conn:
    
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
            INSERT INTO app.contact_custom_details 
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


#################################################################################
# Functions for letters of support and activity feed
@profile("query.py - add_letter_to_history")
def add_letter_to_history(openstates_bill_id, bill_number, org_id, org_name, 
                         letter_name, letter_url, user_name):
    '''
    Adds a new letter to the letter history table.
    '''
    import datetime
    today = datetime.date.today()
    current_timestamp = datetime.datetime.now()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO app.bill_letter_history
                    (openstates_bill_id, bill_number, org_id, org_name, letter_name, letter_url, 
                    created_by, created_on, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (openstates_bill_id, bill_number, org_id, org_name, letter_name, letter_url, 
            user_name, today, current_timestamp))
            
            conn.commit()
            print(f"Letter added to history for bill {bill_number}")

        except Exception as e:
            conn.rollback()
            print(f"Error adding letter to history: {str(e)}")
            raise e

    st.rerun()
    return True
        


@profile("query.py - get_letter_history")
def get_letter_history(openstates_bill_id, org_id):
    '''
    Retrieves all letters for a specific bill and organization, ordered by date.
    '''
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT letter_name, letter_url, created_by, created_on, created_at
            FROM app.bill_letter_history
            WHERE openstates_bill_id = %s AND org_id = %s
            ORDER BY created_at DESC
        """, (openstates_bill_id, org_id))
        
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        letter_history = []
        for row in results:
            letter_history.append({
                'letter_name': row[0],
                'letter_url': row[1],
                'created_by': row[2],
                'created_on': row[3],
                'created_at': row[4]
            })
        
        return letter_history


@profile("query.py - get_most_recent_letter")
def get_most_recent_letter(openstates_bill_id, org_id):
    '''
    Retrieves the most recent letter for a specific bill and organization.
    Returns None if no letter exists.
    '''
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT letter_name, letter_url, created_by, created_on, created_at
            FROM app.bill_letter_history
            WHERE openstates_bill_id = %s AND org_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (openstates_bill_id, org_id))
        
        row = cursor.fetchone()
        
        if row:
            return {
                'letter_name': row[0],
                'letter_url': row[1],
                'created_by': row[2],
                'created_on': row[3],
                'created_at': row[4]
            }
        
        return None


@profile("query.py - get_bill_activity_history")
@st.cache_data(ttl=5) 
def get_bill_activity_history(openstates_bill_id, org_id):
    '''
    Retrieves complete activity history for a bill including field changes
    and letters.
    '''
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 'field_change' as activity_type, field_name, 
                old_value, new_value, changed_by as user, 
                changed_on as date, changed_at as timestamp
            FROM app.bill_custom_details_history
            WHERE openstates_bill_id = %s AND org_id = %s
            
            UNION ALL
            
            SELECT 'letter' as activity_type, letter_name as field_name,
                letter_url as old_value, NULL as new_value,
                created_by as user, created_on as date, created_at as timestamp
            FROM app.bill_letter_history
            WHERE openstates_bill_id = %s AND org_id = %s
            
            ORDER BY timestamp DESC
        """, (openstates_bill_id, org_id, openstates_bill_id, org_id))
        
        results = cursor.fetchall()
        
        activity_history = []
        for row in results:
            activity_history.append({
                'activity_type': row[0],
                'field_name': row[1],
                'old_value': row[2],
                'new_value': row[3],
                'user': row[4],
                'date': row[5],
                'timestamp': row[6]
            })
        
        return activity_history

        
##################################################################################
# Advocacy details functions
@profile("query.py - get_all_custom_bill_details")
@st.cache_data(ttl=120)  #  Cache for 2 mins 
def get_all_custom_bill_details():
    """
    Fetches all custom bill details for a specific bill from all organizations.
    For use on the advocacy hub page.
    """
    
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("""
            SELECT * FROM app.bill_custom_details
            ORDER BY bill_number ASC
        """, )
        
        results = cursor.fetchall()

    return [dict(row) for row in results]

@profile("query.py - get_all_custom_bill_details_for_bill")
@st.cache_data(ttl=120)  #  Cache for 2 mins 
def get_all_custom_bill_details_for_bill(openstates_bill_id):
    """
    Fetch all custom advocacy details for a single bill across all organizations.
    For use on the AI Working Group dashboard.
    """
    
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """
            SELECT * FROM app.bill_custom_details
            WHERE openstates_bill_id = %s
            ORDER BY last_updated_org_name ASC
        """
        cursor.execute(query, (openstates_bill_id,))
        results = cursor.fetchall()

    return [dict(row) for row in results]

###############################################################################

# AI Working Group Dashboard Functions
@profile("query.py - add_bill_to_working_group_dashboard")
def add_bill_to_working_group_dashboard(openstates_bill_id, bill_number):
    user_email = st.session_state.get('user_email')
    org_name = st.session_state.get('org_name')
    
    if not openstates_bill_id or not bill_number or not user_email or not org_name:
        st.error("Missing required information to save this bill.")
        return
    with get_connection() as conn:
        try:
            cursor = conn.cursor()

            # Check if bill already exists for this org/user
            cursor.execute("""
                SELECT COUNT(*) FROM app.working_group_dashboard
                WHERE openstates_bill_id = %s AND added_by_org = %s AND added_by_user = %s;
            """, (openstates_bill_id, org_name, user_email))

            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute("""
                    INSERT INTO app.working_group_dashboard 
                    (openstates_bill_id, bill_number, added_by_org, added_by_user)
                    VALUES (%s, %s, %s, %s);
                """, (openstates_bill_id, bill_number, org_name, user_email))

                conn.commit()
                st.success(f'Bill {bill_number} added to Working Group Dashboard!')
            else:
                st.warning(f'Bill {bill_number} is already in the Working Group Dashboard.')

        except Exception as e:
            st.error(f"Error adding bill to Working Group Dashboard: {e}")

@profile("query.py - remove_bill_from_wg_dashboard")
def remove_bill_from_wg_dashboard(openstates_bill_id, bill_number):
    '''
    Removes a selected bill from the AI working group dashboard, deletes it from the database, and updates session state.
    '''
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM app.working_group_dashboard 
            WHERE openstates_bill_id = %s;
        """, (openstates_bill_id,))
        
        conn.commit()

    # Clear the cache so data reloads
    st.cache_data.clear()

    st.success(f'Bill {bill_number} removed from AI Working Group dashboard!')
    st.rerun()

@profile("query.py - get_working_group_bills")
@st.cache_data(show_spinner="Loading bills data...",ttl=120)  #  Cache for 2 mins 
def get_working_group_bills():
    '''
    Fetches bills from the working_group_dashboard table in the PostgreSQL database.
    '''
    with get_connection() as conn:
        try:
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
                FROM app.bills_mv b
                INNER JOIN app.working_group_dashboard wgd
                    ON wgd.openstates_bill_id = b.openstates_bill_id;

            """

            cursor.execute(query)
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=BILL_COLUMNS) if rows else pd.DataFrame(columns=BILL_COLUMNS)
        
        except Exception as e:
            print(f"Error fetching AI Working Group bills: {e}")
            return pd.DataFrame(columns=BILL_COLUMNS)

@profile("query.py - get_wg_comments")
@st.cache_data(ttl=30)  # Cache comment data for 30 seconds
def get_wg_comments(bill_number: str):
    '''
    Fetches discussion comments for a specific bill from the working_group_discussions table.
    
    Args:
        bill_number: The bill number to fetch comments for
        
    Returns:
        list: List of dictionaries containing comment data
    '''
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT comment_id, user_name, user_email, org_id, org_name, comment, added_on, added_at
            FROM app.working_group_discussions
            WHERE bill_number = %s
            ORDER BY added_at DESC
        """, (bill_number,))
        
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        comments = []
        for row in results:
            comments.append({
                'comment_id': row[0],
                'user_name': row[1],
                'user_email': row[2],
                'org_id': row[3],
                'org_name': row[4],
                'comment': row[5],
                'added_on': row[6],
                'added_at': row[7]
            })
        
        return comments

@profile("query.py - save_wg_comment")
def save_wg_comment(bill_number: str, user_name: str, user_email: str, comment: str, org_id: int = None, org_name: str = None):
    '''
    Saves a comment to the working group discussion table in the PostgreSQL database.
    
    Args:
        bill_number: The bill number being discussed
        user_name: Name of the user making the comment
        user_email: Email of the user making the comment
        comment: The comment text
        org_id: Optional organization ID
        org_name: Optional organization name
        
    Returns:
        comment_id: The ID of the newly created comment
    '''
    import datetime
    today = datetime.date.today()
    current_timestamp = datetime.datetime.now()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO app.working_group_discussions 
            (bill_number, user_name, user_email, org_id, org_name, comment, added_on, added_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING comment_id;
        """, (bill_number, user_name, user_email, org_id, org_name, comment, today, current_timestamp))
        
        comment_id = cursor.fetchone()[0]
        
        conn.commit()

        # Clear the cache so that the comments re-load and new comment appears
        st.cache_data.clear()
        
        return comment_id

@profile("query.py - get_ai_members")
@st.cache_data(show_spinner="Loading bills data...",ttl=60 * 60 * 6) # Cache name data and refresh every 6 hours
def get_ai_members():
    '''
    Get list of names of AI Working Group members from the database.
    '''
    with get_connection() as conn:
        try:
            cursor = conn.cursor()

            query = f"""
                SELECT name, email, org_name
                FROM auth.approved_users
                WHERE ai_working_group = 'yes';
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            return pd.DataFrame(rows, columns=['name', 'email', 'org_name']) if rows else pd.DataFrame(columns=['name', 'email', 'org_name'])

        except Exception as e:
            print(f"Error fetching AI Working Group members: {e}")
            return []




