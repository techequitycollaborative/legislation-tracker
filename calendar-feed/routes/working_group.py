from flask import Blueprint, abort, current_app, request
from extensions import cache
from auth import resolve_user_token
from db.calendar_queries import get_hearings_for_wg
from routes._helpers import ical_response, json_response
import time

bp = Blueprint("working_group", __name__)


@bp.route("/feed/working-group/<token>")
@cache.cached(query_string=True)
def working_group_feed(token: str):
    current_app.logger.info(f"🔑 Request URL: {request.url}")

    timings = {}
    
    start = time.time()
    user = resolve_user_token(token)
    timings['token'] = (time.time() - start) * 1000
    if not user:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(401)
    if not user["is_wg_member"]:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(403)

    start = time.time()
    rows = get_hearings_for_wg()
    timings['query'] = (time.time() - start) * 1000
    # current_app.logger.info(f"Feed served: user={user["email"]}, events={len(rows)}")
    
    start = time.time()
    result = ical_response(
        rows,
        feed_title="AI Working Group - Legislation Tracker",
        filename="working_group_hearings.ics",
        feed_label="AI-WG",
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
