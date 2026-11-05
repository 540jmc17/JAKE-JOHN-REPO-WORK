# CampusGear — Sprint 1 Website Skeleton & Navigation (Requirement #4)

This starter Flask site is the implementation for **John and Jake's Sprint 1 assignment: Requirement #4 — Website Skeleton and Navigation Menu (2 story points)**. The shared layout, mobile-friendly navigation, and implemented routes are working. The catalog and sign-in pages are intentionally labeled placeholders until the assigned teams integrate their features.

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app run --debug
```

Open http://127.0.0.1:5000 in a browser. The `--debug` flag is for local development only.

## Run navigation tests

```bash
python -m pytest -q
```

## Implemented pages

| Route | Purpose | Sprint 1 status |
| --- | --- | --- |
| `/` | Home page with links to the main site sections | Implemented for #4 |
| `/catalog` | Equipment Catalog entry point | Page works; **real inventory not implemented** (#3) |
| `/about` | Project information | Implemented for #4 |
| `/login` | Account/sign-in entry point | Page works; **authentication not implemented** (#5) |

The navigation appears on each page and highlights the current page with `aria-current="page"`. It supports keyboard navigation and responsive layouts.

## Integrating other team assignments

- **Database team (#1):** Register the database extension or data access layer inside `campusgear/create_app` after its implementation is ready. This starter deliberately has no database logic.
- **Catalog team (#3):** Replace the `/catalog` view in `campusgear/routes.py` and the placeholder content in `templates/catalog.html` with real equipment listings. Keep the endpoint `site.catalog` or update `url_for()` calls in the shared template. Do not show unavailable items as available.
- **Authentication team (#5, #6):** Replace the `/login` placeholder with a real login route, implement server-side sessions and authorization checks, and protect private/staff routes. Do not store credentials in this starter or treat hidden links as security.
- **Role-specific features team (#7):** Extend the `{% block account_actions %}` and navigation in `templates/base.html` after login is implemented. Only show navigation options appropriate for the user's role, and also enforce permissions in backend routes.
- **Equipment registration team (#2):** Add a staff-only equipment registration page after authentication and authorization exist.

If a teammate introduces a different Flask structure, preserve the shared `base.html` layout and make sure all `url_for()` references are adjusted to the final endpoint names.

## Verification for Requirement #4

1. Start the app and open the homepage.
2. Confirm the navigation menu is visible.
3. Click **Equipment Catalog** and verify that `/catalog` opens.
4. Click **Home**, **About**, and **Sign in** and verify that each implemented route opens.
5. Use the browser back button or the navigation menu to move between pages.
6. Run `python -m pytest -q` and confirm every test passes.
7. Resize to phone width and check that navigation remains accessible.

**Scope clarification:** passing these tests proves the navigation scaffold works. It does not complete Requirements #1–#3 or #5–#7, which require real database-backed behavior, authentication, and authorization.
