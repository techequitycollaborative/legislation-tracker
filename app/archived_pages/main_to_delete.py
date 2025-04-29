#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
Created on Oct 2, 2024

This is the main script of the Legislation Tracker. To run the app locally, run: 'streamlit run main.py'
"""

import streamlit as st
import datetime
import bcrypt
import psycopg2
import re
from db.config import config
from typing import Optional, Tuple

# Get the current year
current_year = datetime.datetime.now().year

# Page configuration
st.set_page_config(
    page_title='CA Legislation Tracker',
    page_icon=':scales:',
    layout='wide',
    initial_sidebar_state='collapsed',
    menu_items={
        'Get help': 'mailto:info@techequity.us',
        'Report a bug': 'https://github.com/techequitycollaborative/legislation-tracker/issues',
        'About': f"""
        The CA Legislation Tracker is a project by [TechEquity](https://techequity.us). 

        **Developer Credits**: Danya Sherbini, Jessica Wang
        
        Special thanks to Matt Brooks and the team of volunteers who contributed to the previous version of this tool.

        Copyright (c) {current_year} TechEquity. [Terms of Use](https://github.com/techequitycollaborative/legislation-tracker/blob/main/LICENSE)
        """
    }
)

# Add logo
logo = './assets/logo.png'
st.logo(
        logo,
        link="https://techequity.us")

# Extract query parameters
query_params = st.query_params
nav_page = query_params.get("nav", "home")  # Default to "home" if no query param is set

# Load the database configuration
db_config = config('postgres')

# Improved security and validation functions
def validate_email(email: str) -> bool:
    """
    Validate email format using a more comprehensive regex.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if email is valid, False otherwise
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_password(password: str) -> bool:
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
    
    Returns:
        bool: True if password meets complexity requirements
    """
    # Require:
    # - At least 8 characters
    # - At least one uppercase letter
    # - At least one lowercase letter
    # - At least one number
    # - At least one special character
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(password_regex, password) is not None

def hash_password(password: str) -> str:
    """
    Securely hash a password using bcrypt.
    
    Args:
        password (str): Plain text password
    
    Returns:
        str: Hashed password
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password (str): Plain text password
        hashed (str): Hashed password to check against
    
    Returns:
        bool: True if password is correct, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_db_connection():
    """
    Establish and return a database connection.
    
    Returns:
        tuple: Database connection and cursor
    """
    try:
        db_config = config('postgres')
        conn = psycopg2.connect(**db_config)
        return conn, conn.cursor()
    except (Exception, psycopg2.Error) as error:
        st.error(f"Error connecting to database: {error}")
        return None, None

def get_user(email: str) -> Optional[Tuple]:
    """
    Retrieve user information by email.
    
    Args:
        email (str): User's email address
    
    Returns:
        Optional[Tuple]: User information or None if not found
    """
    conn, c = get_db_connection()
    if not conn:
        return None
    
    try:
        c.execute("SELECT id, name, email, password_hash, org_id FROM users WHERE email=%s", (email,))
        user = c.fetchone()
        return user
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()


def create_user(name: str, email: str, password: str, org_id: int) -> Optional[int]:
    """
    Create a new user in the database.
    
    Args:
        name (str): User's full name
        email (str): User's email address
        password (str): User's password
        org_id (int): Organization ID
    
    Returns:
        Optional[int]: Created user ID or None if creation failed
    """
    conn, c = get_db_connection()
    if not conn:
        return None
    
    try:
        password_hash = hash_password(password)
        c.execute("INSERT INTO users (name, email, password_hash, org_id) VALUES (%s, %s, %s, %s) RETURNING id", 
                  (name, email, password_hash, org_id))
        conn.commit()
        return c.fetchone()[0]
    except psycopg2.IntegrityError:
        st.error("Email already exists. Please log in.")
        conn.rollback()
        return None
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def create_organization(name: str, domain: str) -> Optional[int]:
    """
    Create a new organization in the database.
    
    Args:
        name (str): Organization name
        domain (str): Organization domain
    
    Returns:
        Optional[int]: Created organization ID or None if creation failed
    """
    conn, c = get_db_connection()
    if not conn:
        return None
    
    try:
        c.execute("INSERT INTO organizations (name, domain) VALUES (%s, %s) RETURNING id", (name, domain))
        conn.commit()
        return c.fetchone()[0]
    except psycopg2.IntegrityError:
        st.error("Organization with this domain already exists.")
        conn.rollback()
        return None
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_organization_by_id(org_id: int) -> Optional[Tuple]:
    """
    Retrieve organization by ID.
    
    Args:
        org_id (int): Organization ID
    
    Returns:
        Optional[Tuple]: Organization information or None if not found
    """
    conn, c = get_db_connection()
    if not conn:
        return None
    
    try:
        c.execute("SELECT id, name, domain FROM organizations WHERE id=%s", (org_id,))
        org = c.fetchone()
        return org
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_organization_by_domain(domain: str) -> Optional[Tuple]:
    """
    Retrieve organization by domain.
    
    Args:
        domain (str): Organization domain
    
    Returns:
        Optional[Tuple]: Organization information or None if not found
    """
    conn, c = get_db_connection()
    if not conn:
        return None
    
    try:
        c.execute("SELECT id, name, domain FROM organizations WHERE domain=%s", (domain,))
        org = c.fetchone()
        return org
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def handle_successful_signup():
    """
    Callback function to handle successful signup.
    Sets a flag in session state to show success message on login page.
    """
    # Store success message and signup data in session state
    st.session_state['signup_success'] = True
    st.session_state['show_signup'] = False

def signup_page():
    """
    Render the signup page with validation and error handling.
    """
    st.markdown("<h3 style='text-align: center;'>Sign up for the CA Legislation Tracker</h3>", unsafe_allow_html=True)
    
    # Signup form inputs
    name = st.text_input("Full Name", help="Enter your full name")
    email = st.text_input("Email", help="Enter a valid email address")
    password = st.text_input("Password", type="password", 
                              help="Password must be at least 8 characters, include uppercase, lowercase, number, and special character")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    # Validate and submit
    if st.button("Sign Up"):
        # Comprehensive validation
        errors = []
        
        if not name:
            errors.append("Name is required")
        
        if not validate_email(email):
            errors.append("Invalid email address")
        
        if not validate_password(password):
            errors.append("Password does not meet complexity requirements")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        # Extract email domain
        email_domain = email.split('@')[-1] if '@' in email else ""
        
        # Display any validation errors
        if errors:
            for error in errors:
                st.error(error)
            return
        
        # Check organization access
        org = get_organization_by_domain(email_domain)
        
        if org:
            org_id = org[0]  # Get existing org_id
            org_name = org[1]  # Get org name for later use
            
            user_id = create_user(name, email, password, org_id)
            
            if user_id:
                # Store user email for login convenience
                st.session_state['signup_email'] = email
                # Store org name in session state for later use
                st.session_state['org_name'] = org_name
                # Set success flag and redirect to login
                st.session_state['signup_success'] = True
                st.session_state['show_signup'] = False
                st.rerun()
        else:
            st.error("Your organization does not have access. Please email info@techequity.us for more information.")

    # Add a button to return to login page
    if st.button("Already have an account? Log In"):
        st.session_state['show_signup'] = False
        st.rerun()

def login_page():
    """
    Render the login page with improved error handling.
    """
    # Show success message if coming from signup
    if st.session_state.get('signup_success'):
        st.success("Account created successfully! Please log in.")
        # Clear the success flag so it doesn't show again on refresh
        st.session_state.pop('signup_success', None)
    
    st.markdown("<h3 style='text-align: center;'>Login to the CA Legislation Tracker</h3>", unsafe_allow_html=True)
    
    # Pre-fill email if coming from signup
    email_value = st.session_state.get('signup_email', '')
    if email_value:
        # Clear the stored email after using it once
        st.session_state.pop('signup_email', None)
    
    email = st.text_input("Email", value=email_value)
    password = st.text_input("Password", type="password")
    
    # Login attempt
    if st.button("Login"):
        # Basic input validation
        if not email or not password:
            st.error("Please enter both email and password")
            return
        
        user = get_user(email)
        
        if user and check_password(password, user[3]):
            # Successful login
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = user[0]
            st.session_state['user_name'] = user[1]
            st.session_state['user_email'] = user[2]
            st.session_state['org_id'] = user[4]
            
            # Get organization info and store in session state
            org = get_organization_by_id(user[4])
            if org:
                st.session_state['org_name'] = org[1]
            
            st.rerun()
        else:
            st.error("Invalid email or password. Please try again.")
    
    # Signup navigation
    if st.button("Create an Account"):
        st.session_state['show_signup'] = True
        st.rerun()

def logout():
    """
    Clear session state and log out the user.
    """
    st.session_state.logged_out = True  # Set a flag instead of calling st.rerun()

# Check if the user has triggered a logout and rerun if necessary
if "logged_out" in st.session_state and st.session_state.logged_out:
    st.session_state.clear()
    st.rerun()  # Use experimental_rerun() to restart execution

# Main authentication flow remains largely the same
if 'authenticated' not in st.session_state:
    if st.session_state.get('show_signup', False):
        signup_page()
    else:
        login_page()
else:
    # Get org_id from session state
    org_id = st.session_state.get('org_id')
    user_org = st.session_state.get('user_org')
    
    # Get organization info using the correct function
    org_info = get_organization_by_id(org_id) if org_id else None

    # Add page navigation for the authenticated user
    home = st.Page('home.py', title='Home', icon='🏠', url_path='home', default=(nav_page == "home")) 
    bills = st.Page('bills.py', title='Bills', icon='📝', url_path='bills')
    legislators = st.Page('legislators.py', title='Legislators', icon='💼', url_path='legislators')
    calendar = st.Page('calendar_page.py', title='Calendar', icon='📅', url_path='calendar')
    dashboard = st.Page('dashboard.py', title='My Dashboard', icon='📌', url_path='my_dashboard')

    if org_info:
        org_dashboard = st.Page("org_dashboard.py", title=f"{org_info[1]} Dashboard", icon="🏢", url_path="org_dashboard")
    else:
        org_dashboard = st.Page("org_dashboard.py", title="Organization Dashboard", icon="🏢", url_path="org_dashboard", default=False)

    # Build navigation bar
    pg = st.navigation([home, bills, legislators, calendar, dashboard, org_dashboard])

    # Clear query parameters after successful login to prevent infinite loops
    if st.session_state.get('connected'):
        st.query_params.clear()

    # Run the correct page based on query parameter navigation
    pg.run()

    # Add the logout button to the bottom of the navigation bar
    st.sidebar.markdown("<br>" * 16, unsafe_allow_html=True)  # Push logout button down
    if st.sidebar.button('Log out', key='logout'):
        logout()
