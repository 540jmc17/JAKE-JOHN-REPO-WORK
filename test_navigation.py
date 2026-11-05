"""Sprint 1 Requirement #4: visible navigation and functioning links."""

import pytest

from campusgear import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    return app.test_client()


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


@pytest.mark.parametrize("path", ["/", "/catalog", "/about", "/login"])
def test_navigation_links_are_available_on_every_page(client, path):
    html = client.get(path).get_data(as_text=True)
    for link in ('href="/"', 'href="/catalog"', 'href="/about"', 'href="/login"'):
        assert link in html
    assert 'href="#main-content"' in html


@pytest.mark.parametrize("path,label", [
    ("/", "Home"),
    ("/catalog", "Equipment Catalog"),
    ("/about", "About"),
    ("/login", "Sign in"),
])
def test_selected_page_is_marked_active(client, path, label):
    html = client.get(path).get_data(as_text=True)
    assert f'aria-current="page">{label}</a>' in html
    assert html.count('aria-current="page"') == 1


def test_catalog_is_a_clearly_labeled_placeholder(client):
    html = client.get("/catalog").get_data(as_text=True)
    assert "Catalog integration in progress" in html
    assert "Requirement #3" in html


def test_login_does_not_collect_credentials_before_auth_integration(client):
    html = client.get("/login").get_data(as_text=True)
    assert "Secure login is coming soon" in html
    assert "does not accept credentials" in html
    assert "<form" not in html


def test_stylesheet_is_served(client):
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert b".primary-nav" in response.data
