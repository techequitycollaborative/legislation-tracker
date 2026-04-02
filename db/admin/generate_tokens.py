#!/usr/bin/env python3
"""
scripts/generate_tokens.py

Generates iCal feed tokens for users and organizations that don't have one yet.
- Raw tokens are printed to stdout ONCE and never stored.
- Only the sha256 hash is written to the database.
- Safe to re-run: skips rows that already have a token.
- Pass --regenerate <email_or_org_id> to forcibly reset a single record.

Usage:
    python -m db.scripts.generate_tokens                                        # backfill missing only
    python -m db.scripts.generate_tokens --regenerate                           # reset ALL and backfill
    python -m db.scripts.generate_tokens --regenerate user someone@example.com  # reset one user
    python -m db.scripts.generate_tokens --regenerate org 42                    # reset one org
"""

import argparse
import hashlib
import secrets
import sys

from db.connect import get_conn
from psycopg2.extras import RealDictCursor

def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_and_store(cur, table: str, id_col: str, id_val, label: str) -> str:
    """Generate a token for one row. Returns the raw token."""
    raw = secrets.token_urlsafe(32)  # 43 URL-safe chars
    hashed = hash_token(raw)
    cur.execute(
        f"""
        UPDATE {table}
           SET feed_token_hash       = %s,
               feed_token_created_at = NOW()
         WHERE {id_col} = %s
        """,
        (hashed, id_val),
    )
    print(f"[TOKEN] {label:<45}  token={raw}")
    return raw
 
 
def clear_all_tokens(conn):
    print("\n── Clearing all existing tokens ───────────────────────────────────")
    with conn.cursor() as cur:
        cur.execute("UPDATE auth.approved_users SET feed_token_hash = NULL, feed_token_created_at = NULL")
        cur.execute("UPDATE auth.approved_organizations SET feed_token_hash = NULL, feed_token_created_at = NULL")
    conn.commit()
    print("  Done.")
 
 
def backfill_users(conn):
    print("\n── Users ──────────────────────────────────────────────────────────")
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT email FROM auth.approved_users WHERE feed_token_hash IS NULL"
        )
        rows = cur.fetchall()
        if not rows:
            print("  All users already have tokens.")
            return
        for row in rows:
            generate_and_store(cur, "auth.approved_users", "email", row["email"], row["email"])
    conn.commit()
    print(f"  Backfilled {len(rows)} user(s).")
 
 
def backfill_orgs(conn):
    print("\n── Organizations ──────────────────────────────────────────────────")
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, name FROM auth.approved_organizations WHERE feed_token_hash IS NULL"
        )
        rows = cur.fetchall()
        if not rows:
            print("  All organizations already have tokens.")
            return
        for row in rows:
            label = f"id={row['id']} ({row.get('name', '')})"
            generate_and_store(cur, "auth.approved_organizations", "id", row["id"], label)
    conn.commit()
    print(f"  Backfilled {len(rows)} org(s).")
 
 
def regenerate_user(conn, email: str):
    print(f"\nRegenerating token for user: {email}")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT email FROM auth.approved_users WHERE email = %s", (email,)
        )
        if not cur.fetchone():
            print(f"  ERROR: No user found with email '{email}'", file=sys.stderr)
            sys.exit(1)
        generate_and_store(cur, "auth.approved_users", "email", email, email)
    conn.commit()
 
 
def regenerate_org(conn, org_id: int):
    print(f"\nRegenerating token for org id: {org_id}")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM auth.approved_organizations WHERE id = %s", (org_id,)
        )
        if not cur.fetchone():
            print(f"  ERROR: No org found with id={org_id}", file=sys.stderr)
            sys.exit(1)
        generate_and_store(cur, "auth.approved_organizations", "id", org_id, f"id={org_id}")
    conn.commit()
 
 
def main():
    parser = argparse.ArgumentParser(description="Generate/regenerate iCal feed tokens")
    parser.add_argument(
        "--regenerate",
        nargs="*",                          # 0, 1, or 2 args
        metavar=("TYPE", "ID"),
        help=(
            "With no args: reset ALL tokens and backfill. "
            "With 'user <email>' or 'org <id>': reset one record."
        ),
    )
    args = parser.parse_args()
 
    with get_conn() as conn:
        if args.regenerate is None:
            # No --regenerate flag: backfill only missing tokens
            backfill_users(conn)
            backfill_orgs(conn)
            print("\nDone. Store the tokens above securely — they will not be shown again.")
 
        elif len(args.regenerate) == 0:
            # --regenerate with no args: reset everything and backfill
            clear_all_tokens(conn)
            backfill_users(conn)
            backfill_orgs(conn)
            print("\nDone. Store the tokens above securely — they will not be shown again.")
 
        elif len(args.regenerate) == 2:
            # --regenerate user <email> or --regenerate org <id>
            kind, identity = args.regenerate
            if kind == "user":
                regenerate_user(conn, identity)
            elif kind == "org":
                regenerate_org(conn, int(identity))
            else:
                print(f"Unknown type '{kind}'. Use 'user' or 'org'.", file=sys.stderr)
                sys.exit(1)
 
        else:
            parser.print_help()
            sys.exit(1)
 
 
if __name__ == "__main__":
    main()