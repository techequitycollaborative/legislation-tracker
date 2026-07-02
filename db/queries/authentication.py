from db.connect import get_cursor, fetch_one, fetch_all, execute

from typing import Optional, Dict, List

def get_user(email: str) -> Optional[Dict]:
    """
    Retrieve user information by email.
    
    Args:
        email (str): User's email address
    
    Returns:
        Optional[Dict]: User information or None if not found
    """
    sql = "SELECT id, name, email, password_hash, org_id FROM auth.logged_users WHERE email=%s"

    return fetch_one(sql, (email, ))

def is_approved_user(email: str) -> bool:
    """
    Check if the email is in the approved_users table.
    
    Args:
        email (str): User's email address
    
    Returns:
        bool: True if email is in approved_users table, False otherwise
    """
    sql = "SELECT 1 FROM auth.approved_users WHERE lower(email)=lower(%s)"
    result = fetch_one(sql, (email, ))
    return result is not None

def get_all_organizations() -> List[Dict]:
    """
    Retrieve all organizations from the database.
    
    Returns:
        List[Dict]: List of organizations (id, name)
    """
    sql = "SELECT id, name FROM auth.approved_organizations ORDER BY name"
    result = fetch_all(sql)
    return result if result else []

def create_user(name: str, email: str, password_hash: str, org_id: int) -> Optional[int]:
    """
    Create a new user in the database.

    Args:
        name: User's full name
        email: User's email address
        password_hash: Pre-hashed password (hashing is the caller's concern,
            not the db layer's -- keeps this function free of a specific
            hashing library dependency)
        org_id: Organization ID

    Returns:
        The created user's id.

    Raises:
        psycopg2.IntegrityError: if the email already exists (e.g. unique
            constraint violation) -- callers decide how to surface this.
        psycopg2.Error: for other database errors.
    """
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO auth.logged_users
                (name, email, password_hash, org_id, created_at, last_login)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id
            """,
            (name, email, password_hash, org_id),
        )
        return cur.fetchone()["id"]  # RealDictCursor -> dict, not a tuple

def get_organization_by_id(org_id: int) -> Optional[Dict]:
    """
    Retrieve organization by ID.
    
    Args:
        org_id (int): Organization ID
    
    Returns:
        Optional[Dict]: Organization information or None if not found
    """
    sql = "SELECT id, name, domain, nickname FROM auth.approved_organizations WHERE id=%s"
    return fetch_one(sql, (org_id, ))

def update_last_login(user_id: int) -> bool:
    """
    Update the last_login timestamp for a user.
    
    Args:
        user_id (int): User's ID
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    rowcount = execute(
        """
        UPDATE auth.logged_users
        SET last_login = NOW()
        WHERE id = %s
        """,
        (user_id, )
    )
    
    return rowcount > 0
    

def log_user_login(user_id: int, name: str, email: str, org_id: int) -> bool:
    """
    Log a user login event to the auth.logins table.
    
    Args:
        user_id (int): User's ID
        name (str): User's name
        email (str): User's email
        org_id (int): Organization ID
    
    Returns:
        bool: True if logging was successful, False otherwise
    """
    org_name = get_organization_by_id(org_id)["name"]

    with get_cursor() as cur:
        cur.execute(
            """
                INSERT INTO auth.logins 
                (login_date, login_time, user_id, name, email, org, org_id) 
                VALUES (CURRENT_DATE, CURRENT_TIME, %s, %s, %s, %s, %s)
            """, 
            (user_id, name, email, org_name, org_id)
        )
        return cur.rowcount > 0


############################# AI WORKING GROUP VALIDATION #############################

def is_user_in_working_group(user_email):
    """
    Check if the user is in the AI Working Group by querying the approved_users table.
    """
    sql = "SELECT ai_working_group FROM auth.approved_users WHERE lower(email) = lower(%s)"
    result = fetch_one(sql, (user_email, ))
    return result["ai_working_group"].strip().lower() == 'yes'
