from datetime import datetime, timedelta
from itertools import groupby
from typing import Any, List, Tuple, Dict, Optional

import pytz
from icalendar import Event, vText

LOCAL_TZ = pytz.timezone("America/Los_Angeles")
UTC = pytz.utc


def _build_description(h: dict, rows: list[dict]) -> tuple[str, str]:
    """
    Compose the event description from hearing-level fields and bill rows.

    Returns a tuple of (plain_text, html) so callers can attach both:
    - DESCRIPTION (plain) — used by Apple Calendar and Google Calendar
    - X-ALT-DESC (html)   — used by Outlook
    """
    parts = []       # plain text lines
    html_parts = []  # html fragments

    if h.get("hearing_time_verbatim"):
        parts.append(f"Time: {h['hearing_time_verbatim']}")
        html_parts.append(f"<b>Time:</b> {h['hearing_time_verbatim']}")

    # Collect unique deadlines across rows (future-proof for multiple types)
    seen_deadlines = set()
    for row in rows:
        if row.get("deadline_date") and row.get("deadline_type"):
            key = (row["deadline_date"], row["deadline_type"])
            if key not in seen_deadlines:
                parts.append(f"Deadline ({row['deadline_type']}): {row['deadline_date']}")
                html_parts.append(f"<b>Deadline ({row['deadline_type']}):</b> {row['deadline_date']}")
                seen_deadlines.add(key)

    if h.get("notes"):
        parts.append(f"\nNotes: {h['notes']}")
        html_parts.append(f"<br><b>Notes:</b> {h['notes']}")

    # Bills — skip rows where bill data is entirely null (hearing with no bills)
    bills = [r for r in rows if r.get("bill_number")]
    if bills:
        parts.append("\nBills:")
        html_parts.append("<br><b>Bills:</b><ul>")
        for bill in sorted(bills, key=lambda r: r.get("bill_number") or ""):
            line = bill["bill_number"]
            if bill.get("bill_name"):
                line += f" \u2013 {bill['bill_name']}"
            parts.append(line)
            html_parts.append(f"<li>{line}</li>")
        html_parts.append("</ul>")

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
    return [(hearing_id, list(group)) for hearing_id, group in groupby(sorted_rows, key=lambda r: r["hearing_id"])]


def build_hearing_event(hearing_id: int, group_rows: List[Dict[str, Any]]) -> Event:
    """
    Build a single iCalendar Event from a grouped hearing.
    
    Args:
        hearing_id: The hearing ID
        group_rows: All rows belonging to this hearing (bills, deadlines, etc.)
    
    Returns:
        An icalendar Event object
    """
    h = group_rows[0]  # hearing-level fields are identical across all rows
    
    ev = Event()
    ev.add("uid", f"hearing-{hearing_id}@legtracker")
    ev.add("summary", h.get("hearing_name") or f"Hearing {hearing_id}")
    
    plain, html = _build_description(h, group_rows)
    ev.add("description", plain)
    # X-ALT-DESC provides HTML formatting for Outlook, which ignores plain
    # DESCRIPTION. Apple Calendar and Google Calendar ignore this property.
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