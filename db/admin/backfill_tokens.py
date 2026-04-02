#!/usr/bin/env python3
"""
db/admin/backfill_tokens.py

Admin CLI for bulk token generation and single-record resets.
Thin wrapper around db.tokens — all generation logic lives there.

Raw tokens are stored in the DB (feed_token column) and are retrievable
at any time via the Streamlit UI. This script confirms generation but
does not print raw tokens — retrieve them from the UI or query the DB directly.

Usage:
    python -m db.admin.backfill_tokens                                          # backfill missing only
    python -m db.admin.backfill_tokens --regenerate                             # reset ALL and backfill
    python -m db.admin.backfill_tokens --regenerate user someone@example.com    # reset one user
    python -m db.admin.backfill_tokens --regenerate org 42                      # reset one org
"""

import argparse
import sys

from psycopg2.extras import RealDictCursor

from db.connect import get_conn
from db.tokens import generate_user_token, generate_org_token


def _clear_all_tokens(conn):
    print("\n-- Clearing all existing tokens ---")
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE auth.approved_users SET feed_token = NULL, feed_token_hash = NULL, feed_token_created_at = NULL"
        )
        cur.execute(
            "UPDATE auth.approved_organizations SET feed_token = NULL, feed_token_hash = NULL, feed_token_created_at = NULL"
        )
    conn.commit()
    print("  Done.")


def _backfill_users(conn):
    print("\n-- Users ---")
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT email FROM auth.approved_users WHERE feed_token IS NULL"
        )
        rows = cur.fetchall()

    if not rows:
        print("  All users already have tokens.")
        return

    for row in rows:
        generate_user_token(row["email"])
        print(f"  [OK] {row['email']}")

    print(f"  Backfilled {len(rows)} user(s).")


def _backfill_orgs(conn):
    print("\n-- Organizations ---")
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, name FROM auth.approved_organizations WHERE feed_token IS NULL"
        )
        rows = cur.fetchall()

    if not rows:
        print("  All organizations already have tokens.")
        return

    for row in rows:
        generate_org_token(row["id"])
        print(f"  [OK] id={row['id']} ({row.get('name', '')})")

    print(f"  Backfilled {len(rows)} org(s).")


def main():
    parser = argparse.ArgumentParser(description="Backfill or regenerate iCal feed tokens")
    parser.add_argument(
        "--regenerate",
        nargs="*",
        metavar=("TYPE", "ID"),
        help=(
            "With no args: reset ALL tokens and backfill. "
            "With 'user <email>' or 'org <id>': reset one record."
        ),
    )
    args = parser.parse_args()

    with get_conn() as conn:
        if args.regenerate is None:
            _backfill_users(conn)
            _backfill_orgs(conn)
            print("\nDone.")

        elif len(args.regenerate) == 0:
            _clear_all_tokens(conn)
            _backfill_users(conn)
            _backfill_orgs(conn)
            print("\nDone.")

        elif len(args.regenerate) == 2:
            kind, identity = args.regenerate
            if kind == "user":
                generate_user_token(identity)
                print(f"  [OK] Regenerated token for user: {identity}")
            elif kind == "org":
                generate_org_token(int(identity))
                print(f"  [OK] Regenerated token for org id={identity}")
            else:
                print(f"Unknown type '{kind}'. Use 'user' or 'org'.", file=sys.stderr)
                sys.exit(1)
        else:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()