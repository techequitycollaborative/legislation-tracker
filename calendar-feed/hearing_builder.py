# calendar-feed/hearing_builder.py
"""
Builds iCalendar hearing events from grouped query rows.
"""

from datetime import datetime, timedelta
from itertools import groupby
from typing import Any, List, Tuple, Dict

import pytz
from icalendar import Event, vText

LOCAL_TZ = pytz.timezone("America/Los_Angeles")
UTC = pytz.utc

# Chamber abbreviation lookup — keyed on chamber_id.
# IDs 1 (Assembly) and 3 (Joint Assembly) both abbreviate to ASM.
# IDs 2 (Senate) and 4 (Joint Senate) both abbreviate to SEN.
# ID 5 (Joint Chambers) abbreviates to JOINT.
# None/unknown falls back to no prefix.
CHAMBER_ABBREV: dict[int, str] = {
    1: "ASM",
    2: "SEN",
    3: "ASM",
    4: "SEN",
    5: "JOINT",
}


def _chamber_prefix(chamber_id: int | None) -> str:
    """Return a bracketed chamber prefix, e.g. '[ASM]', or '' if unknown."""
    if chamber_id is None:
        return ""
    abbrev = CHAMBER_ABBREV.get(chamber_id)
    return f"[{abbrev}]" if abbrev else ""


def _build_description(h: dict, rows: list[dict]) -> tuple[str, str]:
    """
    Compose the event description from hearing-level fields and bill rows.

    Returns a tuple of (plain_text, html) so callers can attach both:
    - DESCRIPTION (plain) — used by Apple Calendar and Google Calendar
    - X-ALT-DESC (html)   — used by Outlook
    """
    parts = []
    html_parts = []

    if h.get("hearing_time_verbatim"):
        hearing_time = h['hearing_time_verbatim'].replace("m.", "m. PT")
        parts.append(f"Time: {hearing_time}")
        html_parts.append(f"<b>Time:</b> {hearing_time}")

    # Committee webpage link when available (null for subcommittees/joint hearings)
    if h.get("committee_webpage"):
        parts.append(f"Committee info: {h['committee_webpage']}")
        html_parts.append(f"<br><b>Committee info:</b> <a href=\"{h['committee_webpage']}\">{h['committee_webpage']}</a>")

    # Collect unique deadlines across rows (future-proof for multiple types)
    seen_deadlines = set()
    for row in rows:
        if row.get("deadline_date") and row.get("deadline_type"):
            key = (row["deadline_date"], row["deadline_type"])
            if key not in seen_deadlines:
                parts.append(f"{row['deadline_type'].title()} deadline: {row['deadline_date']}")
                html_parts.append(f"<br><b>{row['deadline_type'].title()} deadline:</b> {row['deadline_date']}")
                seen_deadlines.add(key)

    if h.get("notes"):
        parts.append(f"\nNotes: {h['notes']}")
        html_parts.append(f"<br><b>Notes:</b> {h['notes']}")

    # Bills — skip rows where bill data is entirely null (hearing with no bills)
    bills = [r for r in rows if r.get("bill_number")]
    if bills:
        # Ensure bills are sorted in file order
        bills_sorted = sorted(bills, key=lambda r: r.get("file_order", float('inf')))

        parts.append("\nBills in file order:")
        html_parts.append("<br><b>Bills in file order:</b><ol>")

        for bill_detail in bills_sorted:
            line = f"{bill_detail["file_order"]}. "
            if bill_detail.get("bill_name"):
                line += f"{bill_detail['bill_number']} - {bill_detail['bill_name']}"

            parts.append(line)

            html_parts.append(f"<li>{bill_detail['bill_number']} - {bill_detail.get("bill_name", "Bill")}</li>")
        html_parts.append("</ol>")

    plain = "\n".join(parts)
    html  = f'<html><body>{"".join(html_parts)}</body></html>'
    return plain, html


def group_hearings(rows: List[Dict[str, Any]]) -> List[Tuple[int, List[Dict[str, Any]]]]:
    """
    Group rows by hearing_id.

    Returns a list of (hearing_id, group_rows) tuples.
    Each group contains all rows for a single hearing.
    """
    sorted_rows = sorted(rows, key=lambda r: r["hearing_id"])
    return [
        (hearing_id, list(group))
        for hearing_id, group in groupby(sorted_rows, key=lambda r: r["hearing_id"])
    ]


def build_hearing_event(hearing_id: int, group_rows: List[Dict[str, Any]]) -> Event:
    """
    Build a single iCalendar Event from a grouped hearing.

    Summary format: "[ASM] Budget Hearing"
    Chamber prefix is omitted when chamber_id is unknown.

    Args:
        hearing_id: The hearing ID.
        group_rows: All rows belonging to this hearing.

    Returns:
        An icalendar Event object.
    """
    h = group_rows[0]  # hearing-level fields are identical across all rows

    ev = Event()
    ev.add("uid", f"hearing-{hearing_id}@legtracker")

    prefix       = _chamber_prefix(h.get("chamber_id"))
    hearing_name = h.get("hearing_name") or f"Hearing {hearing_id}"
    summary      = f"{prefix} {hearing_name}".strip() if prefix else hearing_name
    ev.add("summary", summary)

    plain, html = _build_description(h, group_rows)
    ev.add("description", plain)
    alt = vText(html)
    alt.params["fmttype"] = "text/html"
    ev.add("x-alt-desc", alt)

    location_parts = [
        p for p in [h.get("hearing_location"), h.get("hearing_room")] if p
    ]
    ev.add("location", ", ".join(location_parts))

    if h.get("is_allday") or not h.get("hearing_time"):
        ev.add("dtstart", h["hearing_date"])
        ev.add("dtend", h["hearing_date"] + timedelta(days=1))
    else:
        dt_local = LOCAL_TZ.localize(
            datetime.combine(h["hearing_date"], h["hearing_time"])
        )
        dt_utc = dt_local.astimezone(UTC)
        ev.add("dtstart", dt_utc)
        ev.add("dtend", dt_utc + timedelta(hours=2))

    ev.add("dtstamp", datetime.now(UTC))

    updated_at_values = [r["updated_at"] for r in group_rows if r.get("updated_at")]
    if updated_at_values:
        ev.add("last-modified", max(updated_at_values))

    return ev