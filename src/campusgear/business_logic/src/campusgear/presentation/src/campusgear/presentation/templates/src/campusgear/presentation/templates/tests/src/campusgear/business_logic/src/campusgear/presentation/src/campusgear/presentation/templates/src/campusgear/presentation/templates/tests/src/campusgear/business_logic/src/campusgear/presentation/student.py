# Name: student.py
# Description: Student Interface of the Presentation Layer. Defines the
#              "student" Blueprint with the student landing page (/student)
#              and a student's private records page
#              (/students/<id>/records). The landing page is a placeholder
#              that the Requirement 7 owners will extend with borrowing and
#              reservation options. The records page is protected by
#              @owner_or_staff_required (Requirement 6): a student sees only
#              their own records, staff may open any student's.
# Programmer: Zema Samuel
# Dates: November 7, 2026
# Revisions: None
# Preconditions: The Blueprint is registered by create_app(); the database has
#                been initialized. The user is signed in (decorators redirect
#                to /login otherwise).
# Postconditions: Only a student (for /student) or the owning student / any
#                 staff member (for the records page) receives a 200 response.
#                 No password hash is rendered.
# Errors: Not signed in -> 302 to /login. Wrong role or another student's id
#         -> 403. A staff request for an id that is not a student -> 404.

from sqlite3 import Error as DatabaseError

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from ..business_logic.loan_management import get_active_loans
from ..business_logic.reservation_management import (
    ReservationError, cancel_reservation, create_reservation, reservation_today,
)
from ..business_logic.user_access import (csrf_is_valid, current_user, get_student_records,
                                          owner_or_staff_required,
                                          role_required)
from ..config import ROLE_STUDENT
from ..db import get_record, transaction

student_bp = Blueprint("student", __name__)


@student_bp.get("/student")
@role_required(ROLE_STUDENT)
def student_home():
    """Placeholder Student Interface; students land here after login."""
    return render_template("student_home.html", active_page="student",
                           user=current_user())


@student_bp.get("/student/loans/active")
@role_required(ROLE_STUDENT)
def active_loans():
    """Show due dates for equipment checked out by the signed-in student."""
    # Take the borrower ID from the session so the URL cannot select another student.
    loans = get_active_loans(current_user()["id"])
    return render_template("active_loans.html", active_page="student", loans=loans)


@student_bp.get("/students/<int:student_id>/records")
@owner_or_staff_required("student_id")
def student_records(student_id):
    """A student's private reservations and loans (owner or staff only)."""
    data = get_student_records(student_id)
    if data is None:
        abort(404)  # no such student (only reachable by staff)
    return render_template("student_records.html", active_page="student",
                           user=current_user(), **data)


@student_bp.route("/catalog/<int:equipment_id>/reserve", methods=["GET", "POST"])
@role_required(ROLE_STUDENT)
def reserve_equipment(equipment_id):
    """Show the date form and save valid reservations for the signed-in student."""
    if request.method == "POST" and not csrf_is_valid():
        abort(400)

    with transaction(current_app.config["DATABASE"]) as connection:
        equipment = get_record(connection, "equipment", equipment_id)
    if equipment is None:
        abort(404)

    student = current_user()
    today = reservation_today()
    form = request.form
    error = None
    status = 200
    if request.method == "POST":
        try:
            create_reservation(student["id"], equipment_id, form.get("start_date", ""),
                               form.get("end_date", ""), today=today)
        except ReservationError as exc:
            error, status = str(exc), 400
        except DatabaseError:
            current_app.logger.exception("Could not save reservation")
            error, status = "Could not save your reservation. Please try again.", 500
        else:
            # The business operation returns only after its transaction commits.
            flash("Reservation created successfully.", "success")
            return redirect(url_for("student.student_records", student_id=student["id"]),
                            code=303)
    elif equipment["status"] != "available":
        abort(404)

    return render_template("reserve_equipment.html", active_page="catalog",
                           equipment=equipment, today=today.isoformat(),
                           form=form, error=error), status


@student_bp.post("/student/reservations/<int:reservation_id>/cancel")
@role_required(ROLE_STUDENT)
def cancel_student_reservation(reservation_id):
    """Cancel the student's reservation and report the result on their records page."""
    if not csrf_is_valid():
        abort(400)

    student_id = current_user()["id"]
    try:
        cancel_reservation(student_id, reservation_id)
    except ReservationError as exc:
        flash(str(exc), "error")
    except DatabaseError:
        current_app.logger.exception("Could not cancel reservation")
        flash("Could not cancel your reservation. Please try again.", "error")
    else:
        # Only confirm a cancellation after the status change commits.
        flash("Reservation canceled successfully.", "success")
    return redirect(url_for("student.student_records", student_id=student_id), code=303)
