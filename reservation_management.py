# AI-assisted integration draft: OpenAI Codex, November 22, 2026.
# The two original prologues below are preserved as source attribution.
# Their review/revision statements describe the source branches, not this draft.
# The team must reconcile the final prologue and document the changed logic.
# AI integration note: cancellation uses (student_id, reservation_id).
# Zema's reservation-first callers must be aligned before the merge is committed.

"""
Module Name: reservation_management.py

Description:
    Reservation Management component of the Business Logic Layer.
    Implements Requirements 9, 10, and 15 for the CampusGear application.

    Requirement 9 — Prevent reservations for unavailable equipment:
        check_availability() detects date-range conflicts against both the
        reservations and loans tables. create_reservation() validates dates,
        calls check_availability(), and inserts the new row.

    Requirement 10 — Role-based reservation views:
        get_reservations_for_user() returns all reservations for staff and
        only the signed-in student's own reservations for student accounts.

    Requirement 15 — Student-initiated cancellation:
        cancel_reservation() verifies ownership and status before setting
        the reservation status to 'cancelled'.

    All database access uses campusgear.db.transaction(). No raw user input
    is ever interpolated into an SQL string; every variable value is passed
    as a bound parameter (?), preventing SQL injection.

Inputs:
    Function arguments: user IDs, equipment IDs, and date strings in
    YYYY-MM-DD format. Database path is read from Flask's app config.

Outputs:
    Reservation IDs on creation. Lists of reservation dicts for views.
    ReservationError exceptions for all business-rule violations.

Implementation Author: Zema Samuel.
Creation Date: November 21, 2026.
Reviewed by: Zema Samuel.
Revisions: None.
Documentation Author: Zema Samuel.
External Sources / Attribution: Uses Flask, SQLite, and the project's
    existing db.py helpers (transaction, insert_record).
Code Origin: Newly written for EECS 581 Project 3, Sprint 2,
    Requirements 9, 10, and 15.
"""

# Name: reservation_management.py
# Description: Reservation Management module of the Business Logic Layer.
#              Handles reservation date validation, reservation creation,
#              and student reservation cancellation. Uses the KU campus
#              timezone (America/Chicago) when determining the current date.
#              The create_reservation() function validates the selected
#              start and end dates, checks equipment availability, and
#              saves valid reservations to the database (Requirement 8).
#              The cancel_reservation() function works to achieve the reservation
#              cancellation workflow.
# Programmer: Jake Crawford and John Pannell, with substantial code-drafting assistance from ChatGPT Pro-6.
# Dates: November 19, 2026
# Revisions: None
# Preconditions: A Flask application context must be active, and
#                app.config["DATABASE"] must contain the configured database
#                path. The database must be initialized with the required
#                equipment, reservation, and loan tables. Reservation dates
#                must be supplied in YYYY-MM-DD format. A valid student ID
#                and equipment ID must be provided when creating a reservation.
# Postconditions: A successful reservation creates a database record
#                 containing the student ID, equipment ID, pickup date,
#                 and return date. A successful cancellation changes the
#                 reservation status to 'cancelled'. Reservations that fail
#                 validation or eligibility checks are not saved or canceled.
# Errors: Invalid or past start dates, invalid end dates, or an end date
#         that is not later than the start date -> ReservationError.
#         Missing or unavailable equipment -> ReservationError.
#         Reservation does not belong to the student, is not in reserved
#         status, or already has an associated loan -> ReservationError.

from contextlib import nullcontext
from datetime import date, datetime
from zoneinfo import ZoneInfo

from flask import current_app

from ..db import get_record, insert_record, transaction


CAMPUS_TIMEZONE = ZoneInfo("America/Chicago")


class ReservationError(ValueError):
    """Raised when a reservation action violates a business rule."""


def _db_path():
    """Return the shared database path from the Flask app config."""
    return current_app.config["DATABASE"]


def reservation_today():
    """Use the KU campus calendar for the form and server validation."""
    return datetime.now(CAMPUS_TIMEZONE).date()


def _parse_date(value, label):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise ReservationError(f"Enter a valid {label} (YYYY-MM-DD).") from error
    if parsed.isoformat() != value:
        raise ReservationError(f"Enter a valid {label} (YYYY-MM-DD).")
    return parsed


def check_availability(equipment_id, pickup_date, return_date, *, connection=None):
    """Raise ReservationError if the equipment is unavailable for the period.

    Checks both the reservations table and the loans table for any record
    whose date range overlaps the requested period.

    Two date ranges overlap when:
        existing_start < requested_end  AND  existing_end > requested_start

    This is the standard interval-overlap test. It correctly handles all
    partial and full overlaps without special-casing adjacency.

    Reservations with status 'cancelled' or 'completed' do not block new
    reservations. Loans with status 'returned' do not block new reservations.
    """
    context = transaction(_db_path()) if connection is None else nullcontext(connection)
    with context as conn:
        # Check the reservations table first (Req 9: "already reserved").
        # A reservation that was cancelled or completed no longer holds the
        # equipment, so those statuses are excluded from the conflict check.
        conflict_reservation = conn.execute(
            """
            SELECT id FROM reservations
            WHERE equipment_id = ?
              AND status NOT IN ('cancelled', 'completed')
              AND pickup_date < ?
              AND return_date > ?
            LIMIT 1
            """,
            (equipment_id, return_date, pickup_date),
        ).fetchone()

        if conflict_reservation:
            raise ReservationError(
                "That equipment is already reserved for some or all of the "
                "dates you selected. Please choose different dates or a "
                "different item.")

        # Check the loans table (Req 9: "already checked out").
        # An active loan occupies the equipment from checkout_date through
        # due_date. Returned loans no longer block new reservations.
        conflict_loan = conn.execute(
            """
            SELECT id FROM loans
            WHERE equipment_id = ?
              AND status = 'checked_out'
              AND checkout_date < ?
              AND due_date > ?
            LIMIT 1
            """,
            (equipment_id, return_date, pickup_date),
        ).fetchone()

        if conflict_loan:
            raise ReservationError(
                "That equipment is already checked out during some or all of "
                "the dates you selected. Please choose different dates or a "
                "different item.")


def create_reservation(student_id, equipment_id, start_date, end_date, *, today=None):
    """Save one reservation for an available item after validating the dates."""
    if today is None:
        today = reservation_today()
    start = _parse_date(start_date, "start date")
    end = _parse_date(end_date, "end date")
    if start < today:
        raise ReservationError(
            "The start date cannot be in the past. Choose a date no earlier than today.")
    if end <= start:
        raise ReservationError("The end date must be later than the start date.")

    with transaction(current_app.config["DATABASE"]) as connection:
        # Keep the equipment status check and insert in the same write transaction.
        connection.execute("BEGIN IMMEDIATE")
        equipment = get_record(connection, "equipment", equipment_id)
        if equipment is None or equipment["status"] != "available":
            raise ReservationError("This equipment is no longer available.")
        check_availability(equipment_id, start.isoformat(), end.isoformat(),
                           connection=connection)
        reservation_id = insert_record(
            connection, "reservations", user_id=student_id,
            equipment_id=equipment_id, pickup_date=start.isoformat(),
            return_date=end.isoformat())

    return reservation_id


# ---------------------------------------------------------------------------
# Requirement 10 — Role-based reservation views
# ---------------------------------------------------------------------------

def get_reservations_for_user(user_id, role):
    """Return reservation rows filtered by role.

    Students (role='student') see only their own reservations.
    Staff (role='staff') see every reservation in the system.

    Each returned dict contains:
        id, equipment_name, asset_id, pickup_date, return_date,
        status, student_name  (always present; useful for staff view).

    Rows are ordered newest first (pickup_date DESC, then id DESC).

    Args:
        user_id (int): The signed-in user's ID (used only for students).
        role    (str): 'student' or 'staff'.

    Returns:
        list[dict]: Reservation rows as dictionaries.
    """
    with transaction(_db_path()) as conn:
        if role == "staff":
            # Staff see all reservations with the student's name.
            rows = conn.execute(
                """
                SELECT r.id,
                       e.name  AS equipment_name,
                       e.asset_id,
                       r.pickup_date,
                       r.return_date,
                       r.status,
                       u.name  AS student_name
                FROM   reservations r
                JOIN   equipment    e ON e.id = r.equipment_id
                JOIN   users        u ON u.id = r.user_id
                ORDER  BY r.pickup_date DESC, r.id DESC
                """,
            ).fetchall()
        else:
            # Students see only their own reservations (Req 10).
            # The WHERE clause uses a bound parameter — never a string
            # built from user input — so there is no SQL-injection risk.
            rows = conn.execute(
                """
                SELECT r.id,
                       e.name  AS equipment_name,
                       e.asset_id,
                       r.pickup_date,
                       r.return_date,
                       r.status,
                       u.name  AS student_name
                FROM   reservations r
                JOIN   equipment    e ON e.id = r.equipment_id
                JOIN   users        u ON u.id = r.user_id
                WHERE  r.user_id = ?
                ORDER  BY r.pickup_date DESC, r.id DESC
                """,
                (user_id,),
            ).fetchall()

    return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# Requirement 15 — Cancel reservation
# ---------------------------------------------------------------------------

def cancel_reservation(student_id, reservation_id):
    """Cancel a student's own reservation if it has not been checked out.

    Business rules (Requirement 15 acceptance criteria):
      - The reservation must exist.
      - The signed-in student must own the reservation.
      - The reservation's current status must be 'reserved'.
        (Already checked-out or cancelled reservations cannot be cancelled.)
      - On success the status is updated to 'cancelled'.

    Args:
        student_id          (int): The signed-in student's user ID.
        reservation_id      (int): The reservation to cancel.

    Raises:
        ReservationError: If any business rule is violated.
    """
    with transaction(_db_path()) as conn:
        conn.execute("BEGIN IMMEDIATE")
        # Fetch the reservation so we can verify ownership and status.
        row = conn.execute(
            "SELECT id, user_id, status FROM reservations WHERE id = ?",
            (reservation_id,),
        ).fetchone()

        if row is None:
            raise ReservationError("This reservation cannot be canceled. Reservation not found.")

        reservation = dict(row)

        # Verify ownership (Req 15: students cannot cancel another
        # student's reservation). Compare as ints; both come from the
        # database or the session, never from user-supplied strings.
        if reservation["user_id"] != student_id:
            raise ReservationError(
                "This reservation cannot be canceled. You can only cancel your own reservations.")

        # Verify the reservation has not already been checked out or
        # cancelled (Req 15: cannot cancel after checkout).
        if reservation["status"] != "reserved":
            if reservation["status"] == "checked_out":
                raise ReservationError(
                    "This reservation cannot be canceled. It has already been checked out and "
                    "cannot be cancelled.")
            if reservation["status"] == "cancelled":
                raise ReservationError(
                    "This reservation cannot be canceled. It has already been cancelled.")
            raise ReservationError(
                "This reservation cannot be canceled.")

        # Check ownership and eligibility in the same write. A concurrent
        # checkout or a repeat cancellation cannot pass this update twice.
        result = conn.execute(
            """
            UPDATE reservations
            SET status = 'cancelled'
            WHERE id = ? AND user_id = ? AND status = 'reserved'
              AND NOT EXISTS (
                  SELECT 1 FROM loans WHERE reservation_id = reservations.id
              )
            """,
            (reservation_id, student_id),
        )
        if result.rowcount != 1:
            raise ReservationError("This reservation cannot be canceled.")
