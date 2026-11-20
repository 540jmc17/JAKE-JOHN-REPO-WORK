# Name: test_reservations.py
# Description: Automated tests for the student equipment reservation form
#              and date-selection workflow. Verifies that signed-in students
#              can access the reservation form from the equipment catalog
#              and submit valid reservation start and end dates.
#              Tests invalid date submissions, including past, equal,
#              reversed, malformed, and missing dates, and verifies that
#              invalid submissions do not create database records.
#              Also tests student-only access, CSRF protection, correct
#              assignment of reservations to the signed-in student, and
#              equipment availability when a reservation is submitted.
#              Requirement #8 (Select Reservation Dates).
# Programmer: Jake Crawford and John Pannell, with substantial code-drafting assistance from ChatGPT Pro-6.
# Dates: November 19, 2026
# Revisions: None
# Preconditions: The Flask test application and database must be initialized
#                with the required tables and test users. Test fixtures must
#                provide a test client, seeded application, authentication
#                helpers, and CSRF token helper. The reservation form,
#                presentation route, and business-logic functions must
#                be implemented.
# Postconditions: Confirms that valid reservation dates are saved with the
#                 correct student ID, equipment ID, and initial reservation
#                 status. Confirms that invalid dates, unavailable equipment,
#                 unauthorized access, and missing CSRF tokens prevent
#                 successful reservation creation.
# Errors: Test failures indicate incorrect date validation, database
#         persistence, student access control, CSRF validation, or
#         equipment availability handling.

from datetime import date

import pytest

from campusgear.db import insert_record, transaction
from conftest import STAFF, STUDENT_A, get_token, login


@pytest.fixture
def available_equipment(seeded_app, monkeypatch):
    # Fix the campus date so these tests stay reproducible.
    monkeypatch.setattr("campusgear.presentation.student.reservation_today",
                        lambda: date(2026, 11, 17))
    with transaction(seeded_app.config["DATABASE"]) as connection:
        return insert_record(connection, "equipment", asset_id="KU-003",
                             name="Tripod", category="Demo", description="Test item")


def test_student_reserves_available_equipment_from_catalog(client, seeded_app,
                                                           available_equipment):
    login(client, STUDENT_A)
    url = f"/catalog/{available_equipment}/reserve"
    catalog = client.get("/catalog").get_data(as_text=True)
    assert f'href="{url}"' in catalog
    assert "/catalog/1/reserve" not in catalog

    form = client.get(url)
    assert form.status_code == 200
    assert b'name="start_date"' in form.data
    assert b'name="end_date"' in form.data
    assert b'min="2026-11-17"' in form.data
    response = client.post(url, data={
        "csrf_token": get_token(client), "start_date": "2026-11-17",
        # Send another user ID to check that the session still determines ownership.
        "end_date": "2026-11-20", "user_id": 2,
    }, follow_redirects=True)
    assert response.history[0].status_code == 303
    assert response.request.path == "/students/1/records"
    assert b"2026-11-17" in response.data
    assert b"2026-11-20" in response.data
    with transaction(seeded_app.config["DATABASE"]) as connection:
        row = connection.execute(
            "SELECT user_id, pickup_date, return_date, status FROM reservations "
            "WHERE equipment_id = ?", (available_equipment,),
        ).fetchone()
        # Verify the saved borrower, dates, and initial reservation status.
        assert tuple(row) == (1, "2026-11-17", "2026-11-20", "reserved")


# Exercise past, equal, reversed, malformed, and missing dates.
@pytest.mark.parametrize(("start", "end", "error"), [
    ("2026-11-16", "2026-11-20", b"cannot be in the past"),
    ("2026-11-17", "2026-11-17", b"must be later"),
    ("2026-11-20", "2026-11-17", b"must be later"),
    ("2026-02-30", "2026-11-20", b"valid start date"),
    ("20261117", "2026-11-20", b"valid start date"),
    (None, "2026-11-20", b"valid start date"),
    ("2026-11-17", None, b"valid end date"),
])
def test_invalid_dates_show_error_without_saving(client, seeded_app, available_equipment,
                                                  start, end, error):
    login(client, STUDENT_A)
    form = {"csrf_token": get_token(client)}
    # A None in the test case means the field is omitted from the POST.
    form.update({key: value for key, value in (("start_date", start), ("end_date", end))
                 if value is not None})
    response = client.post(f"/catalog/{available_equipment}/reserve", data=form)
    assert response.status_code == 400
    assert error in response.data
    with transaction(seeded_app.config["DATABASE"]) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM reservations WHERE equipment_id = ?", (available_equipment,),
        ).fetchone()[0] == 0


def test_form_and_submission_require_student_role_and_post_requires_csrf(
        client, available_equipment):
    url = f"/catalog/{available_equipment}/reserve"
    assert client.get(url).status_code == 302
    assert client.post(url).status_code == 302

    # Staff can browse the catalog. Reservation form access is student-only.
    login(client, STAFF)
    assert client.get(url).status_code == 403
    assert client.post(url).status_code == 403
    assert f'href="{url}"' not in client.get("/catalog").get_data(as_text=True)

    login(client, STUDENT_A)
    assert client.post(url, data={
        "start_date": "2026-11-17", "end_date": "2026-11-20",
    }).status_code == 400


def test_equipment_becoming_unavailable_prevents_reservation(client, seeded_app,
                                                              available_equipment):
    login(client, STUDENT_A)
    url = f"/catalog/{available_equipment}/reserve"
    assert client.get(url).status_code == 200
    with transaction(seeded_app.config["DATABASE"]) as connection:
        # Simulate maintenance starting after the student opened the form.
        connection.execute("UPDATE equipment SET status = 'maintenance' WHERE id = ?",
                           (available_equipment,))
    response = client.post(url, data={
        "csrf_token": get_token(client), "start_date": "2026-11-17",
        "end_date": "2026-11-20",
    })
    assert response.status_code == 400
    assert b"no longer available" in response.data
    with transaction(seeded_app.config["DATABASE"]) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM reservations WHERE equipment_id = ?", (available_equipment,),
        ).fetchone()[0] == 0
