import logging
from flask import Flask
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
    app = Flask(__name__)

    app.register_blueprint(chamber_bp)
    app.register_blueprint(committee_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(wg_bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200
 
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)