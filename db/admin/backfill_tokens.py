#!/usr/bin/env python3
"""
db/admin/backfill_tokens.py

Admin CLI for bulk token generation and single-record resets.
Thin wrapper around db.tokens — all generation logic lives there.

Usage:
    python -m db.admin.backfill_tokens                                          # backfill missing only
    python -m db.admin.backfill_tokens --regenerate                             # reset ALL and backfill
    python -m db.admin.backfill_tokens --regenerate user someone@example.com    # reset one user
    python -m db.admin.backfill_tokens --regenerate org 42                      # reset one org
"""

import argparse
import sys

import psycopg2
from psycopg2.extras import RealDictCursor

from db.connect import get_conn
from db.tokens import generate_user_token, generate_org_token


# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_token(label: str, raw: str):
    """Print a generated token to stdout. This is the only time it's visible."""
    print(f"[TOKEN] {label:<45}  token={raw}")


def _clear_all_tokens(conn):
    print("\n── Clearing all existing tokens ───────────────────────────────────")
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE auth.approved_users SET feed_token_hash = NULL, feed_token_created_at = NULL"
        )
        cur.execute(
            "UPDATE auth.approved_organizations SET feed_token_hash = NULL, feed_token_created_at = NULL"
        )
    conn.commit()
    print("  Done.")


def _backfill_users(conn):
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
        raw = generate_user_token(row["email"])
        _print_token(row["email"], raw)

    print(f"  Backfilled {len(rows)} user(s).")


def _backfill_orgs(conn):
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
        raw = generate_org_token(row["id"])
        label = f"id={row['id']} ({row.get('name', '')})"
        _print_token(label, raw)

    print(f"  Backfilled {len(rows)} org(s).")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Backfill or regenerate iCal feed tokens"
    )
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
            # No flag — backfill missing tokens only
            _backfill_users(conn)
            _backfill_orgs(conn)
            print("\nDone. Store the tokens above securely — they will not be shown again.")

        elif len(args.regenerate) == 0:
            # --regenerate with no args — reset everything and backfill
            _clear_all_tokens(conn)
            _backfill_users(conn)
            _backfill_orgs(conn)
            print("\nDone. Store the tokens above securely — they will not be shown again.")

        elif len(args.regenerate) == 2:
            # --regenerate user <email> or --regenerate org <id>
            kind, identity = args.regenerate
            if kind == "user":
                raw = generate_user_token(identity)
                _print_token(identity, raw)
            elif kind == "org":
                raw = generate_org_token(int(identity))
                _print_token(f"org id={identity}", raw)
            else:
                print(f"Unknown type '{kind}'. Use 'user' or 'org'.", file=sys.stderr)
                sys.exit(1)

        else:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()