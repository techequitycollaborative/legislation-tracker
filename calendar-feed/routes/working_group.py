from flask import Blueprint, abort, current_app
from auth import resolve_user_token
from db.calendar_queries import get_hearings_for_wg
from routes._helpers import ical_response, json_response

bp = Blueprint("working_group", __name__)


@bp.route("/feed/working-group/<token>")
def working_group_feed(token: str):
    user = resolve_user_token(token)
    if not user:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(401)
    if not user["is_wg_member"]:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(403)

    rows = get_hearings_for_wg()
    current_app.logger.info(f"Feed served: user={user["email"]}, events={len(rows)}")
    return ical_response(
        rows,
        feed_title="AI Working Group - Legislation Tracker",
        filename="working_group_hearings.ics",
        feed_label="AI-WG",
    )

@bp.route("/feed/working-group/<token>/json")
def working_group_feed_json(token: str):
    user = resolve_user_token(token)
    if not user:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(401)
    if not user["is_wg_member"]:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(403)

    rows = get_hearings_for_wg()
    current_app.logger.info(f"Feed served: user={user["email"]}, events={len(rows)}")
    return json_response(rows)