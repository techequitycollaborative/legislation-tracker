# calendar-feed/hearing_builder.py
"""
Builds iCalendar hearing events from grouped query rows.
"""

from datetime import datetime, timedelta
from itertools import groupby
from typing import Any, List, Tuple, Dict
import logging

import pytz
from icalendar import Event, vText

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def _build_core_description(h: dict, rows: list[dict]) -> tuple[list, list]:
    parts = []
    html_parts = []

    # -- Step 1: get core details
    if h.get("hearing_time_verbatim"):
        hearing_time = h["hearing_time_verbatim"].replace("m.", "m. PT")
        parts.append(f"Time: {hearing_time}")
        html_parts.append(f"<b>Time:</b> {hearing_time}")

    # Committee webpage link when available (null for subcommittees/joint hearings)
    if h.get("committee_webpage"):
        parts.append(f"Committee info: {h['committee_webpage']}")
        html_parts.append(
            f"<br><b>Committee info:</b> <a href=\"{h['committee_webpage']}\">{h['committee_webpage']}</a>"
        )

    # -- Step 2: collect unique deadlines across rows (future-proof for multiple types)
    seen_deadlines = set()
    for row in rows:
        if row.get("deadline_date") and row.get("deadline_type"):
            key = (row["deadline_date"], row["deadline_type"])
            if key not in seen_deadlines:
                parts.append(
                    f"{row['deadline_type'].title()} deadline: {row['deadline_date']}"
                )
                html_parts.append(
                    f"<br><b>{row['deadline_type'].title()} deadline:</b> {row['deadline_date']}"
                )
                seen_deadlines.add(key)

    # -- Step 3: get optional hearing_notes
    NOTES_NA = "\nNotes: N/A"
    NOTES_NA_HTML = "<br><b>Notes:</b> N/A"

    if h.get("notes"):
        parts.append(f"\nNotes: {h['notes']}")
        html_parts.append(f"<br><b>Notes:</b> {h['notes']}")
    else:
        parts.append(NOTES_NA)
        html_parts.append(NOTES_NA_HTML)
    return parts, html_parts


def _build_footnote_description(
    bills: list[dict], parts: list[str], html_parts: list[str]
) -> tuple[list, list]:

    # Consolidate non-empty footnote content
    footnote_content = dict()
    for bill_detail in bills:
        symbol = bill_detail.get("footnote_symbol") or ""
        footnote = bill_detail.get("footnote") or ""

        # Skip if both are empty
        if not symbol and not footnote:
            continue

        if symbol not in footnote_content:
            footnote_content[symbol] = footnote

    # Join footnote description to the bottom if exists
    if footnote_content:
        logger.info("build footnotes")
        footnote_description = "\n\n----------\n"
        footnote_description_html = "<br><br>----------<br>"

        for symbol, footnote in footnote_content.items():
            line = f"{symbol}{footnote}"
            footnote_description += f"{line}\n"
            footnote_description_html += f"<p>{line}</p>"

        parts.append(footnote_description)
        html_parts.append(footnote_description_html)
    return parts, html_parts


def _build_bill_description(
    bills: list[dict], parts: list[str], html_parts: list[str], dashboard: bool
) -> tuple[list, list]:
    # Filter if this is for a dashboard feed
    if dashboard:
        display_bills = [b for b in bills if b.get("on_dashboard", False)]
        header = "Tracked bills on the agenda"
        list_tag = "ul"
    else:
        display_bills = bills
        header = "Bills on the agenda"
        list_tag = "ol"

    if not display_bills:
        return parts, html_parts

    full_agenda_length = len(bills)
    display_bills.sort(key=lambda b: b["file_order"])
    # Add headers
    parts.append(f"\n**{header}**")
    html_parts.append(f"<br><b>{header}</b><{list_tag}>")

    for bill in display_bills:
        symbol = bill.get("footnote_symbol") or ""
        file_order = bill["file_order"]

        # Ex: AB 123 | Lorem ipsum
        desc = f" {bill['bill_number']}{symbol} | {bill['bill_name']}"

        if dashboard:  # Ex: - AB 123 | Lorem ipsum | File order: 4/5
            # Add file order to description, prefix is always '-'
            desc += f" | File order: {file_order}/{full_agenda_length}"
            prefix = "-"
        else:  # Ex: 4. AB 123 | Lorem ipsum
            prefix = f"{file_order}."

        parts.append(f"{prefix}{desc}")
        html_parts.append(f"<li>{desc.strip()}</li>")

    # Close the HTML list
    html_parts.append(f"</{list_tag}>")
    return parts, html_parts


def _build_description(h: dict, rows: list[dict], dashboard: bool) -> tuple[str, str]:
    """
    Compose the event description from hearing-level fields and bill rows.

    Returns a tuple of (plain_text, html) so callers can attach both:
    - DESCRIPTION (plain) — used by Apple Calendar and Google Calendar
    - X-ALT-DESC (html)   — used by Outlook
    """
    # -- Step 1: Build universal description parts
    parts, html_parts = _build_core_description(h, rows)

    # -- Step 2: extract bills — skip rows if bill number was not found
    bills = [r for r in rows if r.get("bill_number")]

    # -- Step 3: Generate bill descriptions if there are bills associated
    if bills:
        parts, html_parts = _build_bill_description(
            bills=bills,
            parts=parts,
            html_parts=html_parts,
            dashboard=dashboard,
        )
    # -- Step 4: Add footer if there are footnotes
    parts, html_parts = _build_footnote_description(
        bills=bills, parts=parts, html_parts=html_parts
    )

    # -- Step 5: Join parts
    plain = "\n".join(parts)
    html = f'<html><body>{"".join(html_parts)}</body></html>'

    return plain, html


def group_hearings(
    rows: List[Dict[str, Any]],
) -> List[Tuple[int, List[Dict[str, Any]]]]:
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


def build_hearing_event(
    now_utc: datetime,
    hearing_id: int,
    group_rows: List[Dict[str, Any]],
    dashboard: bool,
) -> Event:
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
    if hearing_id is None:
        raise ValueError("hearing_id is required")

    # Handle empty group_rows
    if not group_rows:
        ev = Event()
        ev.add("uid", f"hearing-{hearing_id}@legtracker")
        ev.add("summary", f"Hearing {hearing_id} (no data)")
        ev.add("dtstamp", now_utc)
        return ev

    h = group_rows[0]  # hearing-level fields are identical across all rows

    ev = Event()
    ev.add("uid", f"hearing-{hearing_id}@legtracker")

    # Build event summary (title) from hearing-level fields
    prefix = _chamber_prefix(h.get("chamber_id"))
    hearing_name = h.get("hearing_name") or f"Hearing {hearing_id}"
    summary = f"{prefix} {hearing_name}"
    ev.add("summary", summary)
    logger.info(f"Building {summary}")
    # Build description from all rows in the group
    plain, html = _build_description(h, group_rows, dashboard)
    ev.add("description", plain)
    alt = vText(html)
    alt.params["fmttype"] = "text/html"
    ev.add("x-alt-desc", alt)

    # Build event location from hearing location + room
    location_parts = [
        p for p in [h.get("hearing_location"), h.get("hearing_room")] if p
    ]
    ev.add("location", ", ".join(location_parts))

    # Build event time from relevant columns
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

    ev.add("dtstamp", now_utc)

    # Add last modified value which may differ for each bill in the group
    updated_at_values = [r["updated_at"] for r in group_rows if r.get("updated_at")]
    if updated_at_values:
        ev.add("last-modified", max(updated_at_values))

    return ev
