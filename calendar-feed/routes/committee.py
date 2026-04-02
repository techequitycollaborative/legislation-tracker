# calendar-feed/routes/committee.py

from flask import Blueprint
from db.calendar_queries import get_hearings_for_committee
from routes._helpers import ical_response

bp = Blueprint("committee", __name__)


@bp.route("/feed/committee/<int:committee_id>")
def committee_feed(committee_id: int):
    rows = get_hearings_for_committee(committee_id)
    return ical_response(
        rows,
        feed_title=f"Committee {committee_id} - Legislative Hearings",
        filename=f"committee_{committee_id}.ics",
    )