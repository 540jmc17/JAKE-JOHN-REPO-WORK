"""Public scaffold routes for Sprint 1 Requirement #4.

Do not add staff-only actions or student record access here without
backend authentication and authorization from Requirements #5 and #6.
"""

"""
CampusGear - Website Routes and Navigation

This file controls which pages are displayed when users
navigate through the CampusGear website.

These routes are part of Sprint 1, Requirement #4.
The equipement catalog and login pages are placeholders
until the other team members integrate their features. 

Protected features must have proper authentication
and authorization before they are implemented.
"""

# Import Blueprint to organize the website's routes.
# Import render_template to display the HTML pages.
from flask import Blueprint, render_template

# Create a Blueprint named "site" to group our website routes.
# This Blueprint is registered in __init__.py.
site = Blueprint("site", __name__)


# Homepage Route
# Opens the Homepage when users visit the main website URL.
# active_page highlights Home in the navigation menu.
@site.get("/")
def home():
    return render_template("home.html", active_page="home")


# Equipement Catalog Route
# Opens the equipement catalog when users select it from the menu.
# The actual equipement database will be connnected by the catalog team.
@site.get("/catalog")
def catalog():
    # Placeholder until Requirement #3's real database-backed catalog is merged.
    return render_template("catalog.html", active_page="catalog")


# About Page Route
# Displays information about CampusGear and its purpose.
# Highlights About in the navigation menu.
@site.get("/about")
def about():
    return render_template("about.html", active_page="about")


# Login Page Route
# Oepns the future student and staff login page.
# Authentication will be implemented by the login team. 
@site.get("/login")
def login():
    # Placeholder until Requirement #5's login routes are merged.
    # This page intentionally does not collect credentials.
    return render_template("login.html", active_page="login")
