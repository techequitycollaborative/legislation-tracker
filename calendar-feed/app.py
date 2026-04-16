import logging
import os
import time
from flask import Flask, request, g, Response
from flask_caching import Cache
from extensions import cache
from routes.chamber import bp as chamber_bp
from routes.committee import bp as committee_bp
from routes.org import bp as org_bp
from routes.user import bp as user_bp
from routes.working_group import bp as wg_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


def create_app() -> Flask:
    global cache
    app = Flask(__name__)

    # Configure cache
    app.config["CACHE_TYPE"] = "filesystem"
    app.config["CACHE_DIR"] = "/tmp/flask_cache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 3600  # 1 hr fallback

    # Initialize cache with app
    cache.init_app(app)

    app.register_blueprint(chamber_bp)
    app.register_blueprint(committee_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(wg_bp)

    # Log total calendar feed request time
    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request_duration(response):
        # Skip logging for health/status endpoints to reduce noise
        if request.endpoint in ["status", "health"]:
            return response

        duration = time.time() - g.start_time
        size = len(response.get_data())

        # Log calendar feed requests specifically
        if "feed" in request.path:
            app.logger.info(
                f"CALENDAR FEED | Path: {request.path} | "
                f"Duration: {duration:.4f}s | Size: {size/1024:.1f}KB"
            )
        else:
            app.logger.info(
                f"REQUEST | {request.method} {request.path} | "
                f"Duration: {duration:.4f}s | Size: {size/1024:.1f}KB"
            )

        # Add custom response headers for debugging
        response.headers["X-Response-Time"] = f"{duration*1000:.2f}ms"
        return response

    @app.route("/")
    def root():
        return {"status": "ok"}, 200

    # NOTE: not currently in use
    # Cache clear endpoint for background worker
    @app.route("/admin/cache/clear", methods=["POST"])
    def clear_cache():
        """Clear all cached responses. Called by background worker after data updates."""
        api_key = request.headers.get("X-API-Key")
        expected_key = os.environ.get("CACHE_CLEAR_KEY")

        if not expected_key or api_key != expected_key:
            return {"error": "Unauthorized"}, 401

        cache.clear()
        app.logger.info("Cache cleared by background worker")
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
