"""Public scaffold routes for Sprint 1 Requirement #4.

Do not add staff-only actions or student record access here without
backend authentication and authorization from Requirements #5 and #6.
"""

from flask import Blueprint, render_template

site = Blueprint("site", __name__)


@site.get("/")
def home():
    return render_template("home.html", active_page="home")


@site.get("/catalog")
def catalog():
    # Placeholder until Requirement #3's real database-backed catalog is merged.
    return render_template("catalog.html", active_page="catalog")


@site.get("/about")
def about():
    return render_template("about.html", active_page="about")


@site.get("/login")
def login():
    # Placeholder until Requirement #5's login routes are merged.
    # This page intentionally does not collect credentials.
    return render_template("login.html", active_page="login")
