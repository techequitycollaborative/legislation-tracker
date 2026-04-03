# calendar-feed/ics_builder.py
"""
Assembles a complete iCalendar feed from query rows.

Orchestrates hearing_builder and deadline_builder — owns the Calendar
envelope and iteration logic, not the event construction details.
"""

from typing import Any

import pytz
from icalendar import Calendar

from hearing_builder import build_hearing_event, group_hearings
from deadline_builder import build_deadline_event

UTC = pytz.utc


def build_ical(rows: list[dict[str, Any]], feed_title: str, feed_label: str = "") -> bytes:
    """
    Build an iCal calendar from calendar_queries feed result rows.

    Each hearing produces one hearing event. Dashboard feeds additionally
    produce one all-day deadline event per bill row where on_dashboard=TRUE
    and deadline_date is not null.

    Chamber and committee feeds omit deadline events entirely since rows
    from those queries carry no on_dashboard field.

    Args:
        rows:        List of dicts from any get_hearings_for_* query.
        feed_title:  Human-readable calendar name surfaced in calendar apps.
        feed_label:  Short dashboard tag included in deadline summaries,
                     e.g. '[ORG]', '[PERSONAL]', '[WG]'. Empty string for
                     chamber/committee feeds which emit no deadline events.

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

    for hearing_id, group in group_hearings(rows):
        cal.add_component(build_hearing_event(hearing_id, group))

        # Deadline events — dashboard feeds only, one per tracked bill
        for row in group:
            if row.get("on_dashboard") and row.get("deadline_date"):
                cal.add_component(build_deadline_event(row, feed_label))

    return cal.to_ical()