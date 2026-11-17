from contextlib import contextmanager
from datetime import date
from sqlite3 import OperationalError

import pytest

from campusgear.db import insert_record, transaction
from conftest import STAFF, STUDENT_A, get_token, login, logout


RECORDS = "/students/1/records"
CREATED = b"Reservation created successfully."
CANCELED = b"Reservation canceled successfully."


@pytest.fixture
def reservable_item(seeded_app, monkeypatch):
    # Pin the date so validation has the same result whenever the suite runs.
    monkeypatch.setattr("campusgear.presentation.student.reservation_today",
                        lambda: date(2026, 11, 17))
    with transaction(seeded_app.config["DATABASE"]) as connection:
        return insert_record(connection, "equipment", asset_id="KU-003",
                             name="Tripod", category="Demo", description="Test item")


def submit_reservation(client, equipment_id, end="2026-11-20"):
    return client.post(f"/catalog/{equipment_id}/reserve", data={
        "csrf_token": get_token(client), "start_date": "2026-11-17", "end_date": end,
    }, follow_redirects=True)


def submit_cancellation(client, reservation_id):
    return client.post(f"/student/reservations/{reservation_id}/cancel",
                       data={"csrf_token": get_token(client)}, follow_redirects=True)


def test_create_and_cancel_confirm_only_after_saving(client, seeded_app, reservable_item):
    login(client, STUDENT_A)
    response = submit_reservation(client, reservable_item)
    assert response.request.path == RECORDS
    assert CREATED in response.data
    assert CREATED not in client.get(RECORDS).data
    with transaction(seeded_app.config["DATABASE"]) as connection:
        row = connection.execute(
            "SELECT id, status FROM reservations WHERE equipment_id = ?", (reservable_item,),
        ).fetchone()
        assert row["status"] == "reserved"
        reservation_id = row["id"]

    # The records page provides the cancellation form for the pending reservation.
    assert f'/student/reservations/{reservation_id}/cancel'.encode() in response.data
    response = submit_cancellation(client, reservation_id)
    assert CANCELED in response.data
    assert CREATED not in response.data
    assert CANCELED not in client.get(RECORDS).data
    with transaction(seeded_app.config["DATABASE"]) as connection:
        row = connection.execute("SELECT status FROM reservations WHERE id = ?",
                                 (reservation_id,)).fetchone()
        assert row["status"] == "cancelled"

    assert b"This reservation cannot be canceled." in submit_cancellation(
        client, reservation_id).data
    assert CANCELED not in client.get(RECORDS).data


def test_failed_validation_and_ineligible_cancellations_show_errors(client, reservable_item):
    login(client, STUDENT_A)
    response = submit_reservation(client, reservable_item, end="2026-11-17")
    assert b"end date must be later" in response.data
    assert CREATED not in response.data

    # Seeded reservation 1 is already checked out. Reservation 2 belongs to Student B.
    for reservation_id in (1, 2, 999):
        response = submit_cancellation(client, reservation_id)
        assert b"This reservation cannot be canceled." in response.data
        assert CANCELED not in response.data
    assert client.post("/student/reservations/1/cancel").status_code == 400

    logout(client)
    login(client, STAFF)
    assert client.post("/student/reservations/1/cancel").status_code == 403
    assert b"/student/reservations/1/cancel" not in client.get(RECORDS).data


def test_write_failure_rolls_back_and_never_confirms(
        client, seeded_app, reservable_item, monkeypatch):
    with transaction(seeded_app.config["DATABASE"]) as connection:
        reservation_id = insert_record(
            connection, "reservations", user_id=1, equipment_id=reservable_item,
            pickup_date="2026-11-17", return_date="2026-11-20",
        )

    @contextmanager
    def fail_before_commit(path):
        # Throw after the write so the real transaction manager must roll back.
        with transaction(path) as connection:
            yield connection
            raise OperationalError("simulated write failure")

    monkeypatch.setattr("campusgear.business_logic.reservation_management.transaction",
                        fail_before_commit)
    login(client, STUDENT_A)
    response = submit_reservation(client, reservable_item)
    assert response.status_code == 500
    assert b"Could not save your reservation" in response.data
    assert CREATED not in response.data

    response = submit_cancellation(client, reservation_id)
    assert b"Could not cancel your reservation" in response.data
    assert CANCELED not in response.data
    with transaction(seeded_app.config["DATABASE"]) as connection:
        rows = connection.execute(
            "SELECT id, status FROM reservations WHERE equipment_id = ?", (reservable_item,),
        ).fetchall()
        assert [tuple(row) for row in rows] == [(reservation_id, "reserved")]
