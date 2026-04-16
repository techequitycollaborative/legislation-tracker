from flask import Blueprint, abort, current_app, request
from extensions import cache
from auth import resolve_org_token
from db.calendar_queries import get_hearings_for_org, get_name_for_org
from routes._helpers import ical_response, json_response
import time

bp = Blueprint("org", __name__)


@bp.route("/feed/org/<token>")
@cache.cached(query_string=True)
def org_feed(token: str):
    current_app.logger.info(f"🔑 Request URL: {request.url}")

    timings = {}
    
    start = time.time()
    org_id = resolve_org_token(token)
    timings['token'] = (time.time() - start) * 1000
    if not org_id:
        current_app.logger.warning(f"Auth failed: token={token[:8]}...")
        abort(401)

    start = time.time()
    rows = get_hearings_for_org(org_id)
    timings['query'] = (time.time() - start) * 1000
    
    start = time.time()
    org_name = get_name_for_org(org_id)
    timings['name'] = (time.time() - start) * 1000

    start = time.time()
    result = ical_response(
        rows,
        feed_title=f"{org_name} - Legislation Tracker",
        filename="org_hearings.ics",
        feed_label="ORG",
    )
    timings['build'] = (time.time() - start) * 1000

    current_app.logger.info(
        (
            f"Org: {org_name} timings:"
            f"token={timings['token']:.0f}ms, "
            f"query={timings['query']:.0f}ms, "
            f"rows={len(rows), }"
            f"name={timings['name']:.0f}ms, "
            f"build={timings['build']:.0f}ms, "
        )
    )
    return result


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
