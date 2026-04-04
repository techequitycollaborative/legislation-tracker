from flask import Response, jsonify
from ics_builder import build_ical
from json_builder import build_json


def ical_response(
    rows: list,
    feed_title: str,
    filename: str,
    feed_label: str = "",
) -> Response:
    """Wrap build_ical output in the correct Flask Response."""
    payload = build_ical(rows, feed_title, feed_label)
    return Response(
        payload,
        mimetype="text/calendar",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "public, max-age=3600",
        },
    )


def json_response(hearings: list, status: int = 200) -> Response:
    """Wrap build_json output in a JSON Flask Response."""
    payload = build_json(hearings)
    return jsonify(payload), status