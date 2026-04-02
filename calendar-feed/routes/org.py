from flask import Blueprint, abort
from auth import resolve_org_token
from db.calendar_queries import get_hearings_for_org
from routes._helpers import ical_response, json_response

bp = Blueprint("org", __name__)


@bp.route("/feed/org/<token>")
def org_feed(token: str):
    org_id = resolve_org_token(token)
    if not org_id:
        abort(401)

    rows = get_hearings_for_org(org_id)
    return ical_response(
        rows,
        feed_title="My Organization - Legislative Hearings",
        filename="org_hearings.ics",
    )

@bp.route("/feed/org/<token>/json")
def user_feed_json(token: str):
    """JSON endpoint for web app consumption."""
    org_id = resolve_org_token(token)
    if not org_id:
        abort(401)

    rows = get_hearings_for_org(org_id)
    return json_response(rows)