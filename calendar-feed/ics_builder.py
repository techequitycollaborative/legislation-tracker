from datetime import datetime, timedelta
from itertools import groupby
from typing import Any

import pytz
from icalendar import Calendar, Event, vText

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

    sorted_rows = sorted(rows, key=lambda r: r["hearing_id"])

    for hearing_id, group in groupby(sorted_rows, key=lambda r: r["hearing_id"]):
        group = list(group)
        h = group[0]  # hearing-level fields are identical across all rows in group

        ev = Event()

        ev.add("uid", f"hearing-{hearing_id}@legtracker")
        ev.add("summary", h.get("hearing_name") or f"Hearing {hearing_id}")

        plain, html = _build_description(h, group)
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

        updated_at_values = [r["updated_at"] for r in group if r.get("updated_at")]
        if updated_at_values:
            ev.add("last-modified", max(updated_at_values))

        cal.add_component(ev)

    return cal.to_ical()