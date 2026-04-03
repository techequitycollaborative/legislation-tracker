# calendar-feed/deadline_builder.py
"""
Builds iCalendar all-day deadline events for dashboard bills.

Called once per row where on_dashboard=TRUE and deadline_date is not null.
One deadline event is emitted per bill-hearing association so each tracked
bill gets its own reminder.
"""

from datetime import datetime, timedelta
from typing import Any

import pytz
from icalendar import Event, vText

from hearing_builder import CHAMBER_ABBREV, _chamber_prefix

UTC = pytz.utc


def build_deadline_event(row: dict[str, Any], feed_label: str=None) -> Event:
    """
    Build one all-day deadline event for a single dashboard bill-hearing row.

    Args:
        row:        A single row from any get_hearings_for_* dashboard query
                    where on_dashboard=TRUE and deadline_date is not null.
        feed_label: Dashboard tag surfaced in the summary, e.g. 'ORG', 'AI-WG'.

    Returns:
        An icalendar Event object.

    Summary format: "ORG LETTER DUE! [ASM] - AB 123 - Budget"
    """
    if not row.get("hearing_id") or not row.get("openstates_bill_id"):
        raise ValueError("Missing required fields: hearing_id or openstates_bill_id")
    
    if not row.get("deadline_date"):
        raise ValueError("deadline_date is required but missing")
    
    ev = Event()

    # Stable UID per bill-hearing-deadline_type combination
    deadline_type = (row.get("deadline_type") or "letter").lower().replace(" ", "-")
    ev.add(
        "uid",
        f"deadline-{row['hearing_id']}-{row['openstates_bill_id']}-{deadline_type}@legtracker",
    )

    # Build summary: "ORG LETTER DUE! [ASM] Budget - AB 123"
    label        = (row.get("deadline_type") or "LETTER").upper()
    chamber_tag  = _chamber_prefix(row.get("chamber_id"))
    bill         = row.get("bill_number") or row.get("openstates_bill_id", "")
    hearing_name = row.get("hearing_name") or f"Hearing {row['hearing_id']}"
    hearing_time = row.get("hearing_time_verbatim").replace("m.", "m. PT")
    summary      = ""

    if feed_label:
        summary += f"{feed_label} "
    summary += f"{label} DUE!"
    summary += f" {chamber_tag}"
    summary += f" - {hearing_name} - {bill}"
    ev.add("summary", summary)

    # All-day event; dtend is exclusive next day per RFC 5545
    ev.add("dtstart", row["deadline_date"])
    ev.add("dtend",   row["deadline_date"] + timedelta(days=1))

    ev.add("dtstamp", datetime.now(UTC))

    # Plain + HTML description
    plain = (
        f"{bill}\n"
        f"Hearing: {chamber_tag} {hearing_name}\n"
        f"Time: {hearing_time}\n"
        # f"Deadline type: {row.get('deadline_type', 'letter')}"
    )
    html = (
        f"<html><body>"
        f"<b>{bill}</b><br>"
        f"<b>Hearing:</b> {hearing_name}<br>"
        f"<b>Time:</b> {hearing_time}<br>"
        # f"<b>Deadline type:</b> {row.get('deadline_type', 'letter')}"
        f"</body></html>"
    )
    ev.add("description", plain)
    alt = vText(html)
    alt.params["fmttype"] = "text/html"
    ev.add("x-alt-desc", alt)

    return ev