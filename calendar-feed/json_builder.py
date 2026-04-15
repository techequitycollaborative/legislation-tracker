from typing import Any, List, Dict
from hearing_builder import group_hearings


def build_json(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build JSON structure from hearing rows.

    Returns a dictionary with hearings grouped by date, suitable for
    calendar views in a web app.
    """
    hearing_groups = group_hearings(rows)

    hearings = []
    for hearing_id, group_rows in hearing_groups:
        h = group_rows[0]  # hearing-level fields

        # Build bills list
        bills = []
        for row in group_rows:
            if row.get("bill_number"):
                bill = {
                    "number": row["bill_number"],
                    "name": row.get("bill_name"),
                    "deadline_date": row.get("deadline_date"),
                    "deadline_type": row.get("deadline_type"),
                }
                bills.append(bill)

        # Build hearing object
        hearing = {
            "id": hearing_id,
            "name": h.get("hearing_name"),
            "date": h["hearing_date"].isoformat() if h.get("hearing_date") else None,
            "time": (
                h.get("hearing_time").isoformat() if h.get("hearing_time") else None
            ),
            "time_verbatim": h.get("hearing_time_verbatim"),
            "is_allday": h.get("is_allday", False),
            "location": h.get("hearing_location"),
            "room": h.get("hearing_room"),
            "notes": h.get("notes"),
            "bills": sorted(bills, key=lambda b: b["number"]),
        }
        hearings.append(hearing)

    # Optional: group by date for calendar views
    from collections import defaultdict

    hearings_by_date = defaultdict(list)
    for hearing in hearings:
        if hearing["date"]:
            hearings_by_date[hearing["date"]].append(hearing)

    return {
        "total": len(hearings),
        "hearings": hearings,
        "hearings_by_date": dict(hearings_by_date),
    }
