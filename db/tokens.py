# db/tokens.py
"""
Importable token generation functions for iCal feed URLs.

Used by:
- db/admin/backfill_tokens.py  (CLI admin script)
- streamlit-app                (user-facing "Generate Feed URL" button)

Raw tokens are never stored — only sha256 hashes live in the DB.
The raw token is returned to the caller once and must be displayed
or stored by the caller immediately.
"""

import hashlib
import secrets

from db.connect import get_conn


def _generate_raw() -> str:
    """Generate a cryptographically secure URL-safe token."""
    return secrets.token_urlsafe(32)  # 43 URL-safe chars


def _hash(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_user_token(email: str) -> str:
    """
    Generate a new iCal feed token for a user, replacing any existing one.

    Args:
        email: The user's email address (primary key in auth.approved_users).

    Returns:
        The raw token string. Display this to the user immediately —
        it will not be recoverable from the DB after this call returns.

    Raises:
        ValueError: If no user with that email exists.
        psycopg2.DatabaseError: On DB failure (connection rolls back automatically).
    """
    raw = _generate_raw()
    hashed = _hash(raw)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT email FROM auth.approved_users WHERE email = %s",
                (email,),
            )
            if not cur.fetchone():
                raise ValueError(f"No user found with email '{email}'")

            cur.execute(
                """
                UPDATE auth.approved_users
                   SET feed_token_hash       = %s,
                       feed_token_created_at = NOW()
                 WHERE email = %s
                """,
                (hashed, email),
            )

    return raw


def generate_org_token(org_id: int) -> str:
    """
    Generate a new iCal feed token for an organization, replacing any existing one.

    Args:
        org_id: The organization's ID (primary key in auth.approved_organizations).

    Returns:
        The raw token string. Display this to the user immediately —
        it will not be recoverable from the DB after this call returns.

    Raises:
        ValueError: If no org with that ID exists.
        psycopg2.DatabaseError: On DB failure (connection rolls back automatically).
    """
    raw = _generate_raw()
    hashed = _hash(raw)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM auth.approved_organizations WHERE id = %s",
                (org_id,),
            )
            if not cur.fetchone():
                raise ValueError(f"No organization found with id={org_id}")

            cur.execute(
                """
                UPDATE auth.approved_organizations
                   SET feed_token_hash       = %s,
                       feed_token_created_at = NOW()
                 WHERE id = %s
                """,
                (hashed, org_id),
            )

    return raw


def user_has_token(email: str) -> bool:
    """Return True if the user already has a feed token generated."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT feed_token_hash FROM auth.approved_users WHERE email = %s",
                (email,),
            )
            row = cur.fetchone()
    return bool(row and row[0])


def org_has_token(org_id: int) -> bool:
    """Return True if the org already has a feed token generated."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT feed_token_hash FROM auth.approved_organizations WHERE id = %s",
                (org_id,),
            )
            row = cur.fetchone()
    return bool(row and row[0])