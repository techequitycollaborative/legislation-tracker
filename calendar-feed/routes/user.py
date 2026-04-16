from flask import Blueprint, abort, current_app, request
from extensions import cache
from auth import resolve_user_token
from db.calendar_queries import get_hearings_for_user
from routes._helpers import ical_response, json_response
import time

bp = Blueprint("user", __name__)


@bp.route("/feed/user/<token>")
@cache.cached(query_string=True)
def user_feed(token: str):
    current_app.logger.info(f"🔑 Request URL: {request.url}")

    timings = {}
    
    start = time.time()
    user = resolve_user_token(token)
    timings['token'] = (time.time() - start) * 1000
    if not user:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(401)

    start = time.time()
    rows = get_hearings_for_user(user["email"])
    timings['query'] = (time.time() - start) * 1000
    # current_app.logger.info(f"Feed served: user={user["email"]}, events={len(rows)}")
    
    start = time.time()
    result = ical_response(
        rows,
        feed_title="My Dashboard - Legislation Tracker",
        filename="my_hearings.ics",
    )
    timings['build'] = (time.time() - start) * 1000
    current_app.logger.info(
        (
            f"User: {user["email"][:20]} timings:"
            f"token={timings['token']:.0f}ms, "
            f"query={timings['query']:.0f}ms, "
            f"rows={len(rows), }"
            f"build={timings['build']:.0f}ms, "
        )
    )
    return result

@bp.route("/feed/user/<token>/json")
def user_feed_json(token: str):
    """JSON endpoint for web app consumption."""
    user = resolve_user_token(token)
    if not user:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(401)

    rows = get_hearings_for_user(user["email"])
    current_app.logger.info(f"Feed served: user={user["email"]}, events={len(rows)}")
    return json_response(rows)
