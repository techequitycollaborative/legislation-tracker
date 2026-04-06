"""
Importable token generation functions for iCal feed URLs.

Used by:
- db/admin/backfill_tokens.py  (CLI admin script)
- streamlit-app                (user-facing "Get Feed URL" display)

Both the raw token and its sha256 hash are stored in the DB:
- feed_token      — plaintext, for display in the Streamlit UI
- feed_token_hash — sha256 hash, for fast lookup on every feed request

The feed service never compares raw tokens directly — it always hashes
the incoming token and compares against feed_token_hash.
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

    Stores both the raw token (for UI display) and its hash (for feed
    request validation) in auth.approved_users.

    Args:
        email: The user's email address (primary key in auth.approved_users).

    Returns:
        The raw token string.

    Raises:
        ValueError: If no user with that email exists.
        psycopg2.DatabaseError: On DB failure (rolls back automatically).
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
                   SET feed_token            = %s,
                       feed_token_hash       = %s,
                       feed_token_created_at = NOW()
                 WHERE email = %s
                """,
                (raw, hashed, email),
            )

    return raw


def generate_org_token(org_id: int) -> str:
    """
    Generate a new iCal feed token for an organization, replacing any existing one.

    Stores both the raw token (for UI display) and its hash (for feed
    request validation) in auth.approved_organizations.

    Args:
        org_id: The organization's ID (primary key in auth.approved_organizations).

    Returns:
        The raw token string.

    Raises:
        ValueError: If no org with that ID exists.
        psycopg2.DatabaseError: On DB failure (rolls back automatically).
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
                   SET feed_token            = %s,
                       feed_token_hash       = %s,
                       feed_token_created_at = NOW()
                 WHERE id = %s
                """,
                (raw, hashed, org_id),
            )

    return raw


def get_user_token(email: str) -> str | None:
    """
    Return the stored raw token for a user, or None if not yet generated.
    Used by the Streamlit UI to display the feed URL without regenerating.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT feed_token FROM auth.approved_users WHERE email = %s",
                (email,),
            )
            row = cur.fetchone()
    return row[0] if row else None


def get_org_token(org_id: int) -> str | None:
    """
    Return the stored raw token for an org, or None if not yet generated.
    Used by the Streamlit UI to display the feed URL without regenerating.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT feed_token FROM auth.approved_organizations WHERE id = %s",
                (org_id,),
            )
            row = cur.fetchone()
    return row[0] if row else None