import hashlib
import logging
from typing import Optional

from db.connect import get_conn

logger = logging.getLogger(__name__)


def _hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def resolve_org_token(raw_token: str) -> Optional[int]:
    """Return org_id if the token is valid, else None."""
    hashed = _hash(raw_token)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM auth.approved_organizations WHERE feed_token_hash = %s",
                (hashed,),
            )
            row = cur.fetchone()
    return row[0] if row else None


def resolve_user_token(raw_token: str) -> Optional[dict]:
    """
    Return {email, is_wg_member} if the token is valid, else None.
    is_wg_member is True when the wg column equals 'yes' (case-insensitive).
    """
    hashed = _hash(raw_token)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT email, ai_working_group FROM auth.approved_users WHERE feed_token_hash = %s",
                (hashed,),
            )
            row = cur.fetchone()
    if not row:
        return None
    return {
        "email": row[0],
        "is_wg_member": (row[1] or "").strip().lower() == "yes",
    }
