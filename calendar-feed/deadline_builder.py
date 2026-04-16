# calendar-feed/deadline_builder.py
"""
Builds iCalendar all-day deadline events for dashboard bills.

Called once per row where on_dashboard=TRUE and deadline_date is not null.
One deadline event is emitted per bill-hearing association so each tracked
bill gets its own reminder.
"""

from datetime import datetime, timedelta
from typing import Any

from icalendar import Event, vText

from hearing_builder import CHAMBER_ABBREV, _chamber_prefix


def build_deadline_event(
    now_utc: datetime, row: dict[str, Any], feed_label: str = None
) -> Event:
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

    label = (row.get("deadline_type") or "LETTER").upper()
    chamber_tag = _chamber_prefix(row.get("chamber_id"))
    bill_number = row.get("bill_number")
    bill_name = row.get("bill_name")
    bill_author = (
        row.get("bill_author") or "N/A"
    )  # empty string or None both treated as false
    hearing_name = row.get("hearing_name")
    hearing_note = row.get("notes") or "N/A"
    hearing_time = row.get("hearing_time_verbatim").replace("m.", "m. PT")
    hearing_date = row.get("hearing_date")
    summary = ""
    org_section_plain = ""
    org_section_html = ""

    # Build summary example: AB 1864 ORG LETTER DUE! [ASM] Judiciary
    summary += bill_number

    if feed_label:
        summary += f" {feed_label}"
    summary += f" {label} DUE!"
    summary += f" {chamber_tag}"
    summary += f" {hearing_name}"
    ev.add("summary", summary)

    if feed_label == "ORG":
        org_position = row.get("org_position") or "N/A"
        org_section_plain += f"Org Position: {org_position}\n"
        org_section_html += f"Org Position: {org_position}<br>"

    # All-day event; dtend is exclusive next day per RFC 5545
    ev.add("dtstart", row["deadline_date"])
    ev.add("dtend", row["deadline_date"] + timedelta(days=1))

    ev.add("dtstamp", now_utc)

    # # Plain + HTML description
    plain = (
        "**Bill Details**\n"
        f"Bill: {bill_number} | {bill_name}\n"
        f"Author: {bill_author}\n"
        f"{org_section_plain}\n"  # Double newline
        f"**Hearing Details**\n"
        f"Committee: {chamber_tag} {hearing_name}\n"
        f"Hearing date: {hearing_date}\n"
        f"Time: {hearing_time}\n"
        f"Notes: {hearing_note}\n"
        # f"Deadline type: {row.get('deadline_type', 'letter')}"
    )
    html = (
        f"<html><body>"
        f"<b>Bill Details:</b><br>"
        f"Bill: {bill_number} | {bill_name}<br><br>"
        f"Author: <br>"
        f"{org_section_html}<br>"  # Double newline
        f"<b>Hearing Details:</b><br>"
        f"Committee: {chamber_tag} {hearing_name}<br>"
        f"Hearing date: {hearing_date}<br>"
        f"<b>Time:</b> {hearing_time}<br>"
        f"<b>Notes:</b> {hearing_note}<br>"
        # f"<b>Deadline type:</b> {row.get('deadline_type', 'letter')}"
        f"</body></html>"
    )
    ev.add("description", plain)
    alt = vText(html)
    alt.params["fmttype"] = "text/html"
    ev.add("x-alt-desc", alt)

    return ev
