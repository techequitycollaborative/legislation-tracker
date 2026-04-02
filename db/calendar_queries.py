# db/calendar_queries.py

from psycopg2.extras import RealDictCursor
from db.connect import get_conn


# ── Shared SQL fragments ───────────────────────────────────────────────────────

# Core SELECT used by all feed queries — hearing-first with bills eagerly joined
_FEED_SELECT = """
    SELECT
        h.hearing_id,
        h.name              AS hearing_name,
        h.date              AS hearing_date,
        h.time_verbatim     AS hearing_time_verbatim,
        h.time_normalized   AS hearing_time,
        h.is_allday,
        h.location          AS hearing_location,
        h.room              AS hearing_room,
        h.notes,
        h.chamber_id,
        h.committee_id,
        h.updated_at,
        hd.deadline_date,
        hd.deadline_type,
        b.openstates_bill_id,
        b.bill_num          AS bill_number,
        b.title             AS bill_name
    FROM snapshot.hearings h
    LEFT JOIN snapshot.hearing_deadlines hd ON hd.hearing_id = h.hearing_id
    LEFT JOIN snapshot.hearing_bills     hb ON hb.hearing_id = h.hearing_id
    LEFT JOIN snapshot.bill               b  ON b.openstates_bill_id = hb.openstates_bill_id
"""

_FUTURE_ONLY = "h.date >= CURRENT_DATE"
_ORDER       = "ORDER BY h.date, h.time_normalized NULLS LAST"


# ── Page queries (Streamlit) ───────────────────────────────────────────────────

def get_hearings() -> list[dict]:
    """
    All future hearings with no bill data — for the calendar page list view.
    """
    sql = f"""
        SELECT
            h.hearing_id,
            h.name              AS hearing_name,
            h.date              AS hearing_date,
            h.time_verbatim     AS hearing_time_verbatim,
            h.time_normalized   AS hearing_time,
            h.is_allday,
            h.location          AS hearing_location,
            h.room              AS hearing_room,
            h.notes,
            h.chamber_id,
            h.committee_id,
            h.updated_at,
            hd.deadline_date,
            hd.deadline_type
        FROM snapshot.hearings h
        LEFT JOIN snapshot.hearing_deadlines hd ON hd.hearing_id = h.hearing_id
        WHERE {_FUTURE_ONLY}
        {_ORDER}
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()


def get_hearing_agenda(hearing_id: int) -> list[dict]:
    """
    Bills and notes for a single hearing — for the calendar page drill-down.
    """
    sql = """
        SELECT
            hb.file_order,
            b.openstates_bill_id,
            b.bill_number,
            b.bill_name,
            b.leginfo_link,
            b.author,
            h.notes
        FROM snapshot.hearing_bills hb
        JOIN app.bills_mv           b  ON b.openstates_bill_id = hb.openstates_bill_id
        JOIN snapshot.hearings      h  ON h.hearing_id = hb.hearing_id
        WHERE hb.hearing_id = %s
        ORDER BY hb.file_order
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (hearing_id,))
            return cur.fetchall()


# ── Feed queries (calendar-feed service) ──────────────────────────────────────

def get_hearings_for_chamber(chamber_id: int) -> list[dict]:
    sql = f"""
        {_FEED_SELECT}
        WHERE {_FUTURE_ONLY}
          AND h.chamber_id = %s
        {_ORDER}
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (chamber_id,))
            return cur.fetchall()


def get_hearings_for_committee(committee_id: int) -> list[dict]:
    sql = f"""
        {_FEED_SELECT}
        WHERE {_FUTURE_ONLY}
          AND h.committee_id = %s
        {_ORDER}
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (committee_id,))
            return cur.fetchall()


def get_hearings_for_org(org_id: int) -> list[dict]:
    """
    All future hearings where at least one bill on the org's dashboard is on
    the agenda. Returns the full hearing with all associated bills, not just
    the dashboard bills.
    """
    sql = f"""
        {_FEED_SELECT}
        WHERE {_FUTURE_ONLY}
          AND h.hearing_id IN (
                SELECT DISTINCT hb.hearing_id
                  FROM snapshot.hearing_bills  hb
                  JOIN app.org_bill_dashboard  d ON d.openstates_bill_id = hb.openstates_bill_id
                 WHERE d.org_id = %s
          )
        {_ORDER}
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (org_id,))
            return cur.fetchall()


def get_hearings_for_user(user_email: str) -> list[dict]:
    """
    All future hearings where at least one bill on the user's personal
    dashboard is on the agenda.
    """
    sql = f"""
        {_FEED_SELECT}
        WHERE {_FUTURE_ONLY}
          AND h.hearing_id IN (
                SELECT DISTINCT hb.hearing_id
                  FROM snapshot.hearing_bills    hb
                  JOIN app.user_bill_dashboard   d ON d.openstates_bill_id = hb.openstates_bill_id
                 WHERE d.user_email = %s
          )
        {_ORDER}
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (user_email,))
            return cur.fetchall()


def get_hearings_for_wg() -> list[dict]:
    """
    All future hearings where at least one bill on the working group
    dashboard is on the agenda.
    """
    sql = f"""
        {_FEED_SELECT}
        WHERE {_FUTURE_ONLY}
          AND h.hearing_id IN (
                SELECT DISTINCT hb.hearing_id
                  FROM snapshot.hearing_bills        hb
                  JOIN app.working_group_dashboard   d ON d.openstates_bill_id = hb.openstates_bill_id
          )
        {_ORDER}
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()