from flask import Blueprint, current_app
from db.calendar_queries import get_hearings_for_chamber
from routes._helpers import ical_response, json_response

bp = Blueprint("chamber", __name__)


@bp.route("/feed/chamber/<int:chamber_id>")
def chamber_feed(chamber_id: int):
    rows = get_hearings_for_chamber(chamber_id)
    current_app.logger.info(f"Feed served: chamber={chamber_id}, events={len(rows)}")
    return ical_response(
        rows,
        feed_title=f"Chamber {chamber_id} - Legislation Tracker",
        filename=f"chamber_{chamber_id}.ics",
    )

@bp.route("/feed/chamber/<int:chamber_id>/json")
def chamber_feed_json(chamber_id: int):
    rows = get_hearings_for_chamber(chamber_id)
    current_app.logger.info(f"Feed served: chamber={chamber_id}, events={len(rows)}")
    return json_response(rows)