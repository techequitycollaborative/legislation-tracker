from flask import Blueprint, abort, current_app
from auth import resolve_org_token
from db.calendar_queries import get_hearings_for_org, get_name_for_org
from routes._helpers import ical_response, json_response

bp = Blueprint("org", __name__)


@bp.route("/feed/org/<token>")
def org_feed(token: str):
    org_id = resolve_org_token(token)
    if not org_id:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(401)
 
    rows = get_hearings_for_org(org_id)
    org_name = get_name_for_org(org_id)
    current_app.logger.info(org_name)
    current_app.logger.info(f"Feed served: org={org_id}, events={len(rows)}")
    return ical_response(
        rows,
        feed_title=f"{org_name} - Legislation Tracker",
        filename="org_hearings.ics",
        feed_label="ORG",
    )


@bp.route("/feed/org/<token>/json")
def user_feed_json(token: str):
    """JSON endpoint for web app consumption."""
    org_id = resolve_org_token(token)
    if not org_id:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(401)

    rows = get_hearings_for_org(org_id)
    current_app.logger.info(f"Feed served: org={org_id}, events={len(rows)}")
    return json_response(rows)