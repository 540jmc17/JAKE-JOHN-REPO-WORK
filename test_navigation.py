
"""
CampusGear - Navigation Testing

This file contains automated tests for Sprint 1 Requirement #4.

The tests verify that the CampusGear website's main pages
load successfully, navigation links work, and the correct
page is highlighted in the navigation menu.

The tests also verify that the catalog and login pages
are clearly identified as placeholders until their
features are implemented by the other team members.

These tests use pytest and Flask's built-in test client.
"""

# Import pytest to create and run automated tests.
import pytest

# Import the function that creates the CampusGear application.
from campusgear import create_app


# TEST CLIENT SETUP
# Creates a Flask test client so tests can simulate
# website requests without opening a browser.
@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    return app.test_client()


# TEST 1 - PAGE LOADING
# Checks that all four implemented pages load successfully.
# Verifies that each page returns HTTP status 200,
# displays the correct browser title, and includes
# the shared navigation menu.
#
# parametrize runs the same test with four different
# page URLs and their expected titles.
@pytest.mark.parametrize(
    "path,title",
    [
        ("/", "Home"),
        ("/catalog", "Equipment Catalog"),
        ("/about", "About"),
        ("/login", "Sign in"),
    ],
)
def test_implemented_pages_load(client, path, title):
    response = client.get(path)
    assert response.status_code == 200
    assert f"<title>{title} | CampusGear</title>".encode() in response.data
    assert b'<nav class="primary-nav" aria-label="Primary navigation">' in response.data


# TEST 2 - NAVIGATION LINKS
# Checks that the navigation links are available
# on every implemented website page.
#
# The test also verifies that the accessibility
# link for skipping directly to the main content exists.
@pytest.mark.parametrize("path", ["/", "/catalog", "/about", "/login"])
def test_navigation_links_are_available_on_every_page(client, path):
    html = client.get(path).get_data(as_text=True)

    # Verify that the main website links are present.
    for link in ('href="/"', 'href="/catalog"', 'href="/about"', 'href="/login"'):
        assert link in html

    # Verify the accessibility skip link is present.
    assert 'href="#main-content"' in html


# TEST 3 - ACTIVE PAGE INDICATOR
# Verifies that the currently selected page is marked
# as active in the website's navigation.
#
# aria-current="page" identifies the active page
# for accessibility tools such as screen readers.
#
# Only one page should be marked as active at a time.
@pytest.mark.parametrize("path,label", [
    ("/", "Home"),
    ("/catalog", "Equipment Catalog"),
    ("/about", "About"),
    ("/login", "Sign in"),
])
def test_selected_page_is_marked_active(client, path, label):
    html = client.get(path).get_data(as_text=True)

    # Verify that the correct page is marked as active.
    assert f'aria-current="page">{label}</a>' in html

    # Prevent multiple navigation links from being marked active.
    assert html.count('aria-current="page"') == 1


# TEST 4 - EQUIPMENT CATALOG PLACEHOLDER
# Verifies that the catalog page displays a message
# explaining that inventory integration is still in progress.
#
# The actual equipment listings are handled separately
# under Sprint 1 Requirement #3.
def test_catalog_is_a_clearly_labeled_placeholder(client):
    html = client.get("/catalog").get_data(as_text=True)

    assert "Catalog integration in progress" in html
    assert "Requirement #3" in html


# TEST 5 - LOGIN PLACEHOLDER
# Verifies that the login page clearly identifies itself
# as a placeholder until authentication is implemented.
#
# Also checks that no login form is present, preventing
# the unfinished page from requesting user credentials.
#
# This does not replace backend security testing.
def test_login_does_not_collect_credentials_before_auth_integration(client):
    html = client.get("/login").get_data(as_text=True)

    assert "Secure login is coming soon" in html
    assert "does not accept credentials" in html
    assert "<form" not in html


# TEST 6 - STYLESHEET LOADING
# Verifies that the CampusGear CSS file is accessible.
#
# Checks that the stylesheet loads successfully
# and includes the navigation menu styling.
def test_stylesheet_is_served(client):
    response = client.get("/static/styles.css")

    assert response.status_code == 200
    assert b".primary-nav" in response.data
