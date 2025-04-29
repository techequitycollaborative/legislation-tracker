#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
authentication.py
Created on April 22, 2025
@author: danyasherbini

This file defines the user authentication mechanism for the CA Legislation Tracker.
"""

import streamlit as st
import bcrypt
import psycopg2
import re
from db.config import config
from typing import Optional, Tuple, List

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
        c.execute("SELECT id, name, email, password_hash, org_id FROM logged_users WHERE email=%s", (email,))
        user = c.fetchone()
        return user
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def is_approved_user(email: str) -> bool:
    """
    Check if the email is in the approved_users table.
    
    Args:
        email (str): User's email address
    
    Returns:
        bool: True if email is in approved_users table, False otherwise
    """
    conn, c = get_db_connection()
    if not conn:
        return False
    
    try:
        c.execute("SELECT 1 FROM approved_users WHERE email=%s", (email,))
        result = c.fetchone()
        return result is not None
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_organizations() -> List[Tuple]:
    """
    Retrieve all organizations from the database.
    
    Returns:
        List[Tuple]: List of organizations (id, name)
    """
    conn, c = get_db_connection()
    if not conn:
        return []
    
    try:
        c.execute("SELECT id, name FROM organizations ORDER BY name")
        orgs = c.fetchall()
        return orgs
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        return []
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
        c.execute("INSERT INTO logged_users (name, email, password_hash, org_id) VALUES (%s, %s, %s, %s) RETURNING id", 
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
    
    # Get all organizations for the dropdown
    organizations = get_all_organizations()
    org_names = ["Select an organization"] + [org[1] for org in organizations]
    org_mapping = {org[1]: org[0] for org in organizations}
    
    # Organization dropdown
    selected_org = st.selectbox("Organization", options=org_names)
    
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
        
        if selected_org == "Select an organization":
            errors.append("Please select an organization")
        
        # Check if user is approved
        if not is_approved_user(email):
            errors.append("Your email is not in the approved users list. Please contact admin for access.")
        
        # Display any validation errors
        if errors:
            for error in errors:
                st.error(error)
            return
        
        # Get the selected organization ID
        org_id = org_mapping.get(selected_org)
        
        if org_id:
            user_id = create_user(name, email, password, org_id)
            
            if user_id:
                # Store user email for login convenience
                st.session_state['signup_email'] = email
                # Store org name in session state for later use
                st.session_state['org_name'] = selected_org
                # Set success flag and redirect to login
                st.session_state['signup_success'] = True
                st.session_state['show_signup'] = False
                st.rerun()
        else:
            st.error("Invalid organization selection. Please try again.")

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
        
        # Check if the user is in the approved_users table
        if not is_approved_user(email):
            st.error("Your email is not approved for access. Please contact admin.")
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

    