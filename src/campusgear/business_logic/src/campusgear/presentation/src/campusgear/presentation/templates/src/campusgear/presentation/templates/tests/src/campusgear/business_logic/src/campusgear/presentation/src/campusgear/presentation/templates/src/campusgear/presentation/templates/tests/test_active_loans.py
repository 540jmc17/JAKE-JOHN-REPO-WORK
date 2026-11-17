import re

from campusgear.db import insert_record, transaction
from conftest import STAFF, STUDENT_A, STUDENT_B, login, logout


ACTIVE_LOANS_URL = "/student/loans/active"


def test_due_dates_match_equipment_and_exclude_other_students(client, seeded_app):
    # Give Student A a second item with a different due date to verify each pairing.
    with transaction(seeded_app.config["DATABASE"]) as connection:
        item_id = insert_record(connection, "equipment", asset_id="KU-003",
                                name="Tripod", category="Demo", description="Test item",
                                status="checked_out")
        insert_record(connection, "loans", user_id=1, equipment_id=item_id,
                      checkout_date="2026-11-03", due_date="2026-11-15")

    login(client, STUDENT_A)
    assert f'href="{ACTIVE_LOANS_URL}"' in client.get("/student").get_data(as_text=True)
    # A supplied student ID cannot override the borrower from the session.
    response = client.get(f"{ACTIVE_LOANS_URL}?student_id=2")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert re.search(r"Raspberry Pi Kit</td>\s*<td>KU-001</td>\s*"
                     r'<td><time datetime="2026-11-10">2026-11-10</time>', html)
    assert re.search(r"Tripod</td>\s*<td>KU-003</td>\s*"
                     r'<td><time datetime="2026-11-15">2026-11-15</time>', html)
    assert "Camera Kit" not in html

    logout(client)
    login(client, STUDENT_B)
    html = client.get(ACTIVE_LOANS_URL).get_data(as_text=True)
    assert "Camera Kit" in html
    assert "Raspberry Pi Kit" not in html
    assert "Tripod" not in html


def test_returned_equipment_disappears_from_active_loans(client, seeded_app):
    login(client, STUDENT_A)
    assert b"Raspberry Pi Kit" in client.get(ACTIVE_LOANS_URL).data

    # Record the return and verify that the active page reflects it on the next load.
    with transaction(seeded_app.config["DATABASE"]) as connection:
        connection.execute(
            "UPDATE loans SET status = 'returned', actual_return_date = ? WHERE user_id = ?",
            ("2026-11-08", 1),
        )
    response = client.get(ACTIVE_LOANS_URL)
    assert response.status_code == 200
    assert b"Raspberry Pi Kit" not in response.data
    assert b"You have no equipment checked out." in response.data


def test_active_loans_requires_student_login(client):
    assert client.get(ACTIVE_LOANS_URL).status_code == 302
    login(client, STAFF)
    assert client.get(ACTIVE_LOANS_URL).status_code == 403
