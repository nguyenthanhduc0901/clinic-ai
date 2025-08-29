from flask import Flask, jsonify
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)

    # Load configuration
    from .config import Config
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Register blueprints
    from .routes.health import bp as health_bp
    from .routes.vision import bp as vision_bp
    from .routes.text import bp as text_bp
    from .routes.text import bp_alias as text_bp_alias
    app.register_blueprint(health_bp)
    app.register_blueprint(vision_bp, url_prefix="/v1/vision")
    app.register_blueprint(text_bp, url_prefix="/v1/text")
    app.register_blueprint(text_bp_alias, url_prefix="/ai/text")

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "name": "AI Server",
            "version": "1.0",
            "endpoints": {
                "GET /health": "health status of services",
                "POST /v1/vision/predict": {
                    "body": {
                        "image": "base64 string; supports data URI prefix"
                    }
                },
                "POST /v1/text/analyze": {
                    "body": {
                        "text": "string | optional",
                        "texts": ["string", "..."]
                    },
                    "note": "Provide either text or texts (batch)"
                }
            }
        })

    return app


