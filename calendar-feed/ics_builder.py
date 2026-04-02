import pytz
from typing import Any
from icalendar import Calendar
from hearing_builder import group_hearings, build_hearing_event

LOCAL_TZ = pytz.timezone("America/Los_Angeles")
UTC = pytz.utc


def build_ical(rows: list[dict[str, Any]], feed_title: str) -> bytes:
    """
    Build an iCal calendar from calendar_queries feed result rows.

    Rows are grouped by hearing_id so each hearing produces exactly one
    calendar event, even if it has no associated bills.

    Datetimes are emitted in UTC for maximum client compatibility.
    All-day events use date-only values with dtend = hearing_date + 1 day
    per RFC 5545.

    Args:
        rows:       List of dicts from any get_hearings_for_* query.
        feed_title: Human-readable name surfaced in calendar apps.

    Returns:
        Raw iCal bytes (text/calendar).
    """
    cal = Calendar()
    cal.add("prodid", "-//LegTracker//iCal Feed//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", feed_title)
    cal.add("x-wr-caldesc", "Legislative hearing schedule from LegTracker")

    # Use the separated grouping logic
    hearing_groups = group_hearings(rows)
    
    for hearing_id, group_rows in hearing_groups:
        ev = build_hearing_event(hearing_id, group_rows)
        cal.add_component(ev)

    return cal.to_ical()