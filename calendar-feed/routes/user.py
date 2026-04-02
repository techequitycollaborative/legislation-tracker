from flask import Blueprint, abort
from auth import resolve_user_token
from db.calendar_queries import get_hearings_for_user
from routes._helpers import ical_response

bp = Blueprint("user", __name__)


@bp.route("/feed/user/<token>")
def user_feed(token: str):
    user = resolve_user_token(token)
    if not user:
        abort(401)

    rows = get_hearings_for_user(user["email"])
    return ical_response(
        rows,
        feed_title="My Dashboard - Legislative Hearings",
        filename="my_hearings.ics",
    )