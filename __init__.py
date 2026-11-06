"""Flask application factory for the CampusGear student equipment site."""
"""
CampusGear - Flask Application Setup
This file creates and configures the CampusGear website.
It connnects the website's routes to the Flask application
and provides a starting point for future team features.
"""

#Import Flask, the framework used to build our website.
from flask import Flask


def create_app(test_config=None):
    """Create the app and register shared, public page routes.

    Teammates can add a database, authentication, and equipment blueprints here.
    Public page placeholders must be replaced when the real features are ready.
    """

    # Apply optional settings when running automated tests.
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

# Import the website routes from routes.py
# These controls which pages open when users click links.
    from .routes import site

# Register the routes so Flask recongizes the website's URLs.
    app.register_blueprint(site)
    # Return the completed application so app.py can run it. 
    return app
