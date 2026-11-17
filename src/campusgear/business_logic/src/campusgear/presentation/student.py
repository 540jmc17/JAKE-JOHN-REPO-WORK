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

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from ..business_logic.reservation_management import (
    ReservationError, create_reservation, reservation_today,
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


@student_bp.get("/students/<int:student_id>/records")
@owner_or_staff_required("student_id")
def student_records(student_id):
    """A student's private reservations and loans (owner or staff only)."""
    data = get_student_records(student_id)
    if data is None:
        abort(404)  # no such student (only reachable by staff)
    return render_template("student_records.html", active_page="student",
                           user=current_user(), **data)


# GET opens the date form. POST validates and saves the reservation.
@student_bp.route("/catalog/<int:equipment_id>/reserve", methods=["GET", "POST"])
@role_required(ROLE_STUDENT)
def reserve_equipment(equipment_id):
    """Show the date form and save valid reservations for the signed-in student."""
    # Require a valid session token before processing a submission.
    if request.method == "POST" and not csrf_is_valid():
        abort(400)

    with transaction(current_app.config["DATABASE"]) as connection:
        equipment = get_record(connection, "equipment", equipment_id)
    if equipment is None:
        abort(404)

    # Use the signed-in account as the borrower so form data cannot pick another user.
    student = current_user()
    today = reservation_today()
    form = request.form
    error = None
    status = 200
    if request.method == "POST":
        try:
            create_reservation(student["id"], equipment_id, form.get("start_date", ""),
                               form.get("end_date", ""), today=today)
        # Display the validation message while keeping the submitted values.
        except ReservationError as exc:
            error, status = str(exc), 400
        else:
            # The 303 sends the browser to the records page with a GET.
            return redirect(url_for("student.student_records", student_id=student["id"]),
                            code=303)
    elif equipment["status"] != "available":
        abort(404)

    return render_template("reserve_equipment.html", active_page="catalog",
                           equipment=equipment, today=today.isoformat(),
                           form=form, error=error), status
