# db/calendar_queries.py

from psycopg2.extras import RealDictCursor
from db.connect import get_conn

# ── Shared SQL fragments ───────────────────────────────────────────────────────

_FUTURE_ONLY = "h.date >= CURRENT_DATE"
_ORDER = "ORDER BY h.date, h.time_normalized NULLS LAST"

# Core SELECT for chamber/committee feeds — no dashboard context, no deadlines.
# committee_id may be null for subcommittees and joint hearings.
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
        c.webpage_link      AS committee_webpage,
        hd.deadline_date,
        hd.deadline_type,
        b.openstates_bill_id,
        b.bill_num          AS bill_number,
        b.title             AS bill_name
    FROM snapshot.hearings h
    LEFT JOIN snapshot.committee         c  ON c.committee_id = h.committee_id
    LEFT JOIN snapshot.hearing_deadlines hd ON hd.hearing_id = h.hearing_id
    LEFT JOIN snapshot.hearing_bills     hb ON hb.hearing_id = h.hearing_id
    LEFT JOIN snapshot.bill               b ON b.openstates_bill_id = hb.openstates_bill_id
"""

# Extended SELECT for dashboard feeds — adds on_dashboard flag per bill row.
# on_dashboard = TRUE means this bill is tracked on the relevant dashboard,
# which controls whether a deadline event is emitted for that bill in ics_builder.
# The dashboard table LEFT JOIN is appended per query below.
_DASHBOARD_SELECT_BASE = """
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
        c.webpage_link      AS committee_webpage,
        hd.deadline_date,
        hd.deadline_type,
        b.openstates_bill_id,
        b.bill_num          AS bill_number,
        b.title             AS bill_name,
        hb.file_order,
        CASE WHEN dash.openstates_bill_id IS NOT NULL
             THEN TRUE ELSE FALSE
        END                 AS on_dashboard,
        -- Author from bills materialized view
        bmv.author          AS bill_author
    FROM snapshot.hearings h
    LEFT JOIN snapshot.committee         c  ON c.committee_id = h.committee_id
    LEFT JOIN snapshot.hearing_deadlines hd ON hd.hearing_id = h.hearing_id
    LEFT JOIN snapshot.hearing_bills     hb ON hb.hearing_id = h.hearing_id
    LEFT JOIN snapshot.bill               b ON b.openstates_bill_id = hb.openstates_bill_id
    LEFT JOIN app.bills_mv              bmv ON bmv.openstates_bill_id = b.openstates_bill_id
"""

# Extended template with org_position (for org feeds only)
# NOTE: placeholder for org_id included at the end of the template, needs to be resolved
_DASHBOARD_SELECT_WITH_CUSTOM = """
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
        c.webpage_link      AS committee_webpage,
        hd.deadline_date,
        hd.deadline_type,
        b.openstates_bill_id,
        b.bill_num          AS bill_number,
        b.title             AS bill_name,
        hb.file_order,
        CASE WHEN dash.openstates_bill_id IS NOT NULL
             THEN TRUE ELSE FALSE
        END                 AS on_dashboard,
        bmv.author          AS bill_author,
        bcd.org_position
    FROM snapshot.hearings h
    LEFT JOIN snapshot.committee         c  ON c.committee_id = h.committee_id
    LEFT JOIN snapshot.hearing_deadlines hd ON hd.hearing_id = h.hearing_id
    LEFT JOIN snapshot.hearing_bills     hb ON hb.hearing_id = h.hearing_id
    LEFT JOIN snapshot.bill               b ON b.openstates_bill_id = hb.openstates_bill_id
    LEFT JOIN app.bills_mv              bmv ON bmv.openstates_bill_id = b.openstates_bill_id
    LEFT JOIN app.bill_custom_details    bcd ON bcd.openstates_bill_id = b.openstates_bill_id
                                            AND bcd.last_updated_org_id = %s
"""

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
            c.webpage_link      AS committee_webpage,
            hd.deadline_date,
            hd.deadline_type
        FROM snapshot.hearings h
        LEFT JOIN snapshot.committee         c  ON c.committee_id = h.committee_id
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
    """
    No dashboard context — on_dashboard absent, no deadline events emitted.
    """
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
    """
    No dashboard context — on_dashboard absent, no deadline events emitted.
    """
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


def get_name_for_org(org_id: int) -> str | None:
    """
    Return org nickname associated with org ID to use in feed title.
    """
    sql = f"""
        SELECT nickname FROM auth.approved_organizations
        WHERE id = %s
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (org_id,))
            result = cur.fetchone()
            return result["nickname"] if result else None


def get_hearings_for_org(org_id: int) -> list[dict]:
    """
    All future hearings where at least one bill on the org's dashboard is on
    the agenda. Returns all bills on each hearing; on_dashboard=TRUE only for
    bills tracked on this org's dashboard. Deadline events emitted for those only.
    """
    sql = f"""
        {_DASHBOARD_SELECT_WITH_CUSTOM}
        LEFT JOIN app.org_bill_dashboard dash
               ON dash.openstates_bill_id = b.openstates_bill_id
              AND dash.org_id = %s
        WHERE {_FUTURE_ONLY}
          AND h.hearing_id IN (
                SELECT DISTINCT hb2.hearing_id
                  FROM snapshot.hearing_bills hb2
                  JOIN app.org_bill_dashboard d
                    ON d.openstates_bill_id = hb2.openstates_bill_id
                 WHERE d.org_id = %s
          )
        {_ORDER}
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                sql, (org_id, org_id, org_id)
            )  # All three org_id placeholders need to be resolved
            return cur.fetchall()


def get_hearings_for_user(user_email: str) -> list[dict]:
    """
    All future hearings where at least one bill on the user's personal dashboard
    is on the agenda. on_dashboard=TRUE only for bills tracked by this user.
    Deadline events emitted for those only.
    """
    sql = f"""
        {_DASHBOARD_SELECT_BASE}
        LEFT JOIN app.user_bill_dashboard dash
               ON dash.openstates_bill_id = b.openstates_bill_id
              AND dash.user_email = %s
        WHERE {_FUTURE_ONLY}
          AND h.hearing_id IN (
                SELECT DISTINCT hb2.hearing_id
                  FROM snapshot.hearing_bills    hb2
                  JOIN app.user_bill_dashboard   d
                    ON d.openstates_bill_id = hb2.openstates_bill_id
                 WHERE d.user_email = %s
          )
        {_ORDER}
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (user_email, user_email))
            return cur.fetchall()


def get_hearings_for_wg() -> list[dict]:
    """
    All future hearings where at least one bill on the working group dashboard
    is on the agenda. on_dashboard=TRUE only for bills tracked by the WG.
    Deadline events emitted for those only.
    """
    sql = f"""
        {_DASHBOARD_SELECT_BASE}
        LEFT JOIN app.working_group_dashboard dash
               ON dash.openstates_bill_id = b.openstates_bill_id
        WHERE {_FUTURE_ONLY}
          AND h.hearing_id IN (
                SELECT DISTINCT hb2.hearing_id
                  FROM snapshot.hearing_bills      hb2
                  JOIN app.working_group_dashboard d
                    ON d.openstates_bill_id = hb2.openstates_bill_id
          )
        {_ORDER}
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
