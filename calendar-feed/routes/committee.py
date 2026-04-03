# calendar-feed/routes/committee.py

from flask import Blueprint, current_app
from db.calendar_queries import get_hearings_for_committee
from routes._helpers import ical_response, json_response

bp = Blueprint("committee", __name__)


@bp.route("/feed/committee/<int:committee_id>")
def committee_feed(committee_id: int):
    rows = get_hearings_for_committee(committee_id)
    current_app.logger.info(f"Feed served: chamber={committee_id}, events={len(rows)}")
    return ical_response(
        rows,
        feed_title=f"Committee {committee_id} - Legislative Hearings",
        filename=f"committee_{committee_id}.ics",
    )

@bp.route("/feed/committee/<int:committee_id>/json")
def committee_feed_json(committee_id: int):
    rows = get_hearings_for_committee(committee_id)
    current_app.logger.info(f"Feed served: chamber={committee_id}, events={len(rows)}")
    return json_response(rows)