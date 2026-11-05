"""Flask application factory for the CampusGear student equipment site."""

from flask import Flask


def create_app(test_config=None):
    """Create the app and register shared, public page routes.

    Teammates can add a database, authentication, and equipment blueprints here.
    Public page placeholders must be replaced when the real features are ready.
    """
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    from .routes import site

    app.register_blueprint(site)
    return app
