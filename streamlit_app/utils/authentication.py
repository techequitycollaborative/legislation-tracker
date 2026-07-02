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
from db.queries.authentication import * 
from typing import Optional
from dataclasses import dataclass, field
from utils.profiling import profile, show_performance_metrics, track_rerun
import logging
logger = logging.getLogger(__name__)

'''
# Cookies functions for keeping users logged in -- TURNED OFF BC THESE ARE STILL IN DEVELOPMENT!!
from streamlit_cookies_manager import EncryptedCookieManager


# Get secret key from environment variable or use a generated one
def get_secret_key():
    # Try to get from environment variable first (recommended)
    secret_key = os.environ.get("COOKIE_SECRET_KEY")
    
    # If not set, generate a pseudo-random key based on user's session
    if not secret_key:
        if "cookie_secret" not in st.session_state:
            import secrets
            # Generate a new/temporary secret key for this session. Ensures app does not crash if it cannot access cookie secret from server.
            st.session_state["cookie_secret"] = secrets.token_hex(16)
            #st.warning("⚠️ Using temporary secret key. Set COOKIE_SECRET_KEY environment variable for persistent logins.") #optional warning message
        secret_key = st.session_state["cookie_secret"]
    
    return secret_key

# Initialize cookies manager with secret key
cookies = EncryptedCookieManager(
    prefix="auth_", 
    password=get_secret_key()
)

# Safe cookie set function with proper error handling
def set_login_cookie(email: str):
    """Set login cookies with 30-day expiration."""
    try:
        if not cookies.ready():
            # Initialize cookies first if not ready
            cookies.init()
            
        # Set up expiration date
        expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        # Set cookies safely
        cookies["email"] = email
        cookies["auth_expiry"] = expires_at
        cookies.save()
        return True
    except Exception as e:
        st.warning(f"⚠️ Could not set persistent login cookie: {str(e)}")
        # Store in session state as fallback
        st.session_state["backup_user_email"] = email
        return False

# Safe cookie retrieval function
def get_logged_in_user() -> Optional[str]:
    """Get logged in user email from cookies if valid."""
    # Check session state first (fallback if cookies failed)
    if "backup_user_email" in st.session_state:
        return st.session_state["backup_user_email"]
        
    try:
        # Cookies aren't ready, can't get user
        if not cookies.ready():
            return None
            
        expiry = cookies.get("auth_expiry")
        email = cookies.get("email")
        
        if not email or not expiry:
            return None
            
        # Check if cookie is expired
        if datetime.utcnow() > datetime.fromisoformat(expiry):
            clear_login_cookies()
            return None
        return email
    except Exception:
        # Any error with cookies, return None
        return None

def clear_login_cookies():
    """Clear all authentication cookies."""
    try:
        if cookies.ready():
            cookies.clear()
            cookies.save()
    except Exception:
        pass
    
    # Clear backup in session state too
    if "backup_user_email" in st.session_state:
        del st.session_state["backup_user_email"]

'''
############################# AUTH FUNCTIONS #############################
        
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
    Validate password strength. Must include: 
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one digit
    - Minimum length of 8 characters
    - Can include any special characters

    Args:
        password (str): Password to validate

    Returns:
        bool: True if password meets complexity requirements
    """
    # Expanded set of special characters allowed in the password
    #special_chars = r"""@$!%*?&#^()_+=[]{}:;'"<>,./\|~""" -- turned off special character requirement because it was causing log in issues

    # Escape special characters to safely use them in regex
    #escaped_special_chars = re.escape(special_chars) -- turned off special character requirement because it was causing log in issues

    # Build the password validation regex:
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$' 

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
    
@dataclass
class SignupResult:
    success: bool
    user_id: Optional[int] = None
    errors: list[str] = field(default_factory=list)


def signup_user(name: str, email: str, password: str, confirm_password: str,
                 selected_org: str, org_mapping: dict) -> SignupResult:
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

    if not is_approved_user(email):
        errors.append("Your email is not in the approved users list. Please contact admin for access.")

    if errors:
        return SignupResult(success=False, errors=errors)

    org_id = org_mapping.get(selected_org)
    if org_id is None:
        # selected_org wasn't the placeholder, but also isn't a valid key --
        # e.g. org list changed between render and submit
        return SignupResult(success=False, errors=["Invalid organization selection. Please try again."])

    try:
        user_id = create_user(name, email, hash_password(password), org_id)
        return SignupResult(success=True, user_id=user_id)
    except psycopg2.IntegrityError:
        return SignupResult(success=False, errors=["Email already exists. Please log in."])
    except psycopg2.Error as e:
        return SignupResult(success=False, errors=[f"Database error: {e}"])

@dataclass
class LoginResult:
    success: bool
    user: Optional[dict] = None
    org: Optional[dict] = None
    error: Optional[str] = None


def login_user(email: str, password: str) -> LoginResult:
    if not email or not password:
        return LoginResult(success=False, error="Please enter both email and password")

    if not is_approved_user(email):
        return LoginResult(success=False, error="Your email is not approved for access. Please contact admin.")

    user = get_user(email)

    if user is None or not check_password(password, user["password_hash"]):
        return LoginResult(success=False, error="Invalid email or password. Please try again.")

    update_last_login(user["id"])
    log_user_login(user["id"], user["name"], user["email"], user["org_id"])

    org = get_organization_by_id(user["org_id"])
    return LoginResult(success=True, user=user, org=org)

############################# SIGN UP AND LOGIN PAGE #############################
@profile("utils/authentication.py - signup_page")
def signup_page():
    """
    Render the signup page with validation and error handling.
    """
    st.markdown("<h3 style='text-align: center;'>Sign up for the CA Legislation Tracker</h3>", unsafe_allow_html=True)
    
    # Signup form inputs
    name = st.text_input("Full Name", help="Enter your full name")
    email = st.text_input("Email", help="Enter a valid email address")
    password = st.text_input("Password", type="password", 
                              help="Password must be at least 8 characters, including at least one uppercase, one lowercase, and one number")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    # Get all organizations for the dropdown
    organizations = get_all_organizations()
    org_names = ["Select an organization"] + [org["name"] for org in organizations]
    org_mapping = {org["name"]: org["id"] for org in organizations}
    
    # Organization dropdown
    selected_org = st.selectbox("Organization", options=org_names)
    
    # Validate and submit
    if st.button("Sign Up"):
        result = signup_user(
            name, email, password, confirm_password, selected_org, org_mapping
        )
        
        # Display any validation errors
        if not result.success:
            for error in result.errors:
                st.error(error)
            return
        
        st.session_state['signup_email'] = email
        st.session_state['org_name'] = selected_org
        st.session_state['signup_success'] = True
        st.session_state['show_signup'] = False
        st.rerun()

    # Add a button to return to login page
    if st.button("Already have an account? Log In"):
        st.session_state['show_signup'] = False
        st.rerun()


@profile("utils/authentication.py - login_page")
def login_page():
    """
    Render the login page with improved error handling.
    """
    track_rerun("Login")
    # Show success message if coming from signup
    if st.session_state.get('signup_success'):
        st.success("Account created successfully! Please log in.")
        # Clear the success flag so it doesn't show again on refresh
        st.session_state.pop('signup_success', None)
    
    # Add a temporary warning message to let user know the app is under maintenance / not working right now
    #st.warning("⚠️ The CA Legislation Tracker is currently undergoing maintenance, and some features may not work as intended. We will be sharing more information with users once maintenance is complete. We appreciate your patience!")

    # Page header
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
        result = login_user(email, password)

        if not result.success:
            st.error(result.error)
            return
            
        # Successful login
        st.session_state['authenticated'] = True
        st.session_state['user_id'] = result.user["id"]
        st.session_state['user_name'] = result.user["name"]
        st.session_state['user_email'] = result.user["email"]
        st.session_state['org_id'] = result.user["org_id"]
            
        if result.org:
            st.session_state['org_name'] = result.org["name"]
            st.session_state['nickname'] = result.org["nickname"]
            
            #set_login_cookie(user[2])  # <-- Persist login
            st.rerun()
    
    # Signup navigation
    if st.button("Create an Account"):
        st.session_state['show_signup'] = True
        st.rerun()

    # Add some text at the bottom of the page
    st.markdown("---")
    st.markdown("""The CA Legislation Tracker is continually being developed in order to roll out new features 
                and improve the experience for users. If you encounter any issues logging in or using the tool,
                please contact us for assistance at danya@techequity.us.""")
    
    show_performance_metrics()


def logout():
    """
    Clear session state and log out the user.
    """
    #clear_login_cookies() # clear cookies -- TURNED OFF FOR NOW UNTIL WE FIGURE OUT PERSISTENT LOGIN
    #st.session_state.logged_out = True  # Set a flag instead of calling st.rerun() -- TURNED OFF BC THIS WAS CAUSING THE NEED TO CLICK THE LOGOUT BUTTON TWICE
    st.session_state.clear()
    st.rerun()

    