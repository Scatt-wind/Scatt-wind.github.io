import os

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        from app.content_watcher import start_content_watcher

        observer = start_content_watcher()
        if observer is not None:
            import atexit

            atexit.register(observer.stop)

    return app
