from flask import Response, jsonify
from ics_builder import build_ical
from json_builder import build_json


def ical_response(hearings: list, feed_title: str, filename: str) -> Response:
    """Wrap build_ical output in the correct Flask Response."""
    payload = build_ical(hearings, feed_title)
    return Response(
        payload,
        mimetype="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "public, max-age=3600",
        },
    )


def json_response(hearings: list, status: int = 200) -> Response:
    """Wrap build_json output in a JSON Flask Response."""
    payload = build_json(hearings)
    return jsonify(payload), status