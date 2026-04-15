# calendar-feed/ics_builder.py
"""
Assembles a complete iCalendar feed from query rows.

Orchestrates hearing_builder and deadline_builder — owns the Calendar
envelope and iteration logic, not the event construction details.
"""

from typing import Any
import logging

import pytz
from icalendar import Calendar

from hearing_builder import build_hearing_event, group_hearings
from deadline_builder import build_deadline_event

UTC = pytz.utc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_ical(
    rows: list[dict[str, Any]], feed_title: str, feed_label: str = ""
) -> bytes:
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
    # Input validation
    if not rows:
        logger.warning(f"Feed has no data: {feed_title}")

        # Return minimal valid calendar instead of empty bytes
        cal = Calendar()
        cal.add("prodid", "-//LegTracker//iCal Feed//EN")
        cal.add("version", "2.0")
        return cal.to_ical()

    cal = Calendar()
    cal.add("prodid", "-//LegTracker//iCal Feed//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", feed_title)
    cal.add("x-wr-caldesc", "Legislative hearing schedule from LegTracker")

    # Log errors
    hearing_count = 0
    deadline_count = 0
    error_count = 0

    try:
        for hearing_id, group in group_hearings(rows):
            try:
                hearing_event = build_hearing_event(hearing_id, group)
                cal.add_component(hearing_event)
                hearing_count += 1
                # Deadline events - dashboard feeds only, one per tracked bill
                if group:  # Only try to build deadlines if group has data
                    for row in group:
                        # Check for missing data; continue to next bill if invalid
                        if not row.get("on_dashboard") or not row.get("deadline_date"):
                            continue
                        
                        # Check if org position warrants building a deadline; continue to next bill if invalid
                        if feed_label == "ORG":
                            org_pos = row.get("org_position")
                            if not org_pos or org_pos == "Neutral/No Position":
                                continue
                                
                        try:
                            cal.add_component(build_deadline_event(row, feed_label))
                            deadline_count += 1
                        except (KeyError, AttributeError, ValueError) as e:
                            error_count += 1
                            logger.error(
                                f"Failed to build deadline event for bill {row.get("bill_number")}: {e}"
                            )
            except (KeyError, AttributeError, ValueError) as e:
                error_count += 1
                logger.error(f"Failed to build hearing event for ID {hearing_id}: {e}")
                continue  # Skip, but continue to build partial calendar
    except Exception as e:
        error_count += 1
        logger.error(f"Critical error building calendar: {e}")
        # Return minimal calendar instead of failing completely
        minimal_cal = Calendar()
        minimal_cal.add("prodid", "-//LegTracker//iCal Feed//EN")
        cal.add("version", "2.0")
        cal.add("x-wr-calname", feed_title)
        cal.add("x-wr-caldesc", f"Partial calendar - errors occurred: {str(e)}")

    if error_count > 0:
        logger.warning(
            f"Built calendar with errors: {hearing_count} hearings, {deadline_count} deadlines, {error_count} errors"
        )
    else:
        logger.info(
            f"Build calendar: {hearing_count} hearings, {deadline_count} deadlines"
        )
    return cal.to_ical()
