from flask import Blueprint, abort
from auth import resolve_user_token
from db.calendar_queries import get_hearings_for_wg
from routes._helpers import ical_response, json_response

bp = Blueprint("working_group", __name__)


@bp.route("/feed/working-group/<token>")
def working_group_feed(token: str):
    user = resolve_user_token(token)
    if not user:
        abort(401)
    if not user["is_wg_member"]:
        abort(403)

    rows = get_hearings_for_wg()
    return ical_response(
        rows,
        feed_title="Working Group - Legislative Hearings",
        filename="working_group_hearings.ics",
    )

@bp.route("/feed/working-group/<token>/json")
def working_group_feed(token: str):
    user = resolve_user_token(token)
    if not user:
        abort(401)
    if not user["is_wg_member"]:
        abort(403)

    rows = get_hearings_for_wg()
    return json_response(rows)