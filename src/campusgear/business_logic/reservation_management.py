"""Validate and save student reservation dates (Requirement 8)."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from flask import current_app

from ..db import get_record, insert_record, transaction


# Use the KU campus time zone so the date rolls over at local midnight.
CAMPUS_TIMEZONE = ZoneInfo("America/Chicago")


class ReservationError(ValueError):
    """The reservation cannot be saved as submitted."""


def reservation_today():
    """Use the KU campus calendar for the form and server validation."""
    return datetime.now(CAMPUS_TIMEZONE).date()


def _parse_date(value, label):
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ReservationError(f"Enter a valid {label} (YYYY-MM-DD).") from error
    # Require the YYYY-MM-DD format produced by the form.
    if parsed.isoformat() != value:
        raise ReservationError(f"Enter a valid {label} (YYYY-MM-DD).")
    return parsed


def create_reservation(student_id, equipment_id, start_date, end_date, *, today):
    """Save one reservation for an available item after validating the dates."""
    # Validate on the server because requests can bypass browser controls.
    start = _parse_date(start_date, "start date")
    end = _parse_date(end_date, "end date")
    if start < today:
        raise ReservationError("The start date cannot be in the past.")
    if end <= start:
        raise ReservationError("The end date must be later than the start date.")

    with transaction(current_app.config["DATABASE"]) as connection:
        # Keep the equipment status check and insert in the same write transaction.
        connection.execute("BEGIN IMMEDIATE")
        equipment = get_record(connection, "equipment", equipment_id)
        if equipment is None or equipment["status"] != "available":
            raise ReservationError("This equipment is no longer available.")
        # Store the selected dates in the existing pickup and return columns.
        insert_record(connection, "reservations", user_id=student_id,
                      equipment_id=equipment_id, pickup_date=start.isoformat(),
                      return_date=end.isoformat())
