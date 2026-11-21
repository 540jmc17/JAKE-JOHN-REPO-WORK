# Name: student.py
#
# Description: Student Interface of the Presentation Layer.
#              Defines the "student" Blueprint and routes for:
#              - Displaying the student landing page.
#              - Displaying a student's private reservations and loans.
#              - Displaying active equipment loans and their due dates.
#              - Showing the reservation form and submitting reservations.
#              - Canceling reservations and displaying confirmation messages.
#
#              Student-only routes require the student role. The private
#              records page allows access to the owning student or staff.
#              Reservation rules and database updates are handled by
#              functions in the business-logic layer.
#
# Requirements:
#              Requirement 6: Restrict access to student records.
#              Requirement 7: Provide the student landing page.
#              Requirement 8: Select and submit reservation dates.
#              Requirement 16: Display due dates for active loans.
#              Requirement 25: Display reservation confirmation messages.
#
# Programmer: Zema Samuel
# Dates: November 7, 2026
#
# Revisions:
#              November 19, 2026 - Jake Crawford / John Pannell:
#              Added active loans and due-date display (Requirement 16).
#              Added the reservation form and submission route
#              (Requirement 8). Added reservation cancellation and
#              success/error feedback (Requirement 25).
#
#              November 21, 2026 - Documentation update with ChatGPT:
#              Expanded the prologue and explanatory comments.
#              No executable logic changed.
#
# Preconditions:
#              - create_app() has registered this Blueprint.
#              - The database and required tables are initialized.
#              - The referenced templates and business-logic functions exist.
#              - The user must pass the route's authentication/access checks.
#              - Reservation and cancellation POST requests require a valid
#                CSRF token.
#
# Postconditions:
#              - Authorized users receive the requested student pages.
#              - Active loans are retrieved for the signed-in student.
#              - Successful reservation creation or cancellation redirects
#                the student to their records page with a success message.
#              - Handled reservation errors display feedback to the user.
#
# Errors:
#              302: Access decorators redirect unsigned-in users to login.
#              400: Invalid CSRF token or invalid reservation submission.
#              403: The user does not have permission to access the route.
#              404: Student records or equipment cannot be found, or a GET
#                   request tries to reserve unavailable equipment.
#              500: A database error during create_reservation() causes
#                   the reservation form to display a retry message.
#              Cancellation errors are flashed on the records page after
#              a redirect instead of returning an error page here.


# Give SQLite's general error class a descriptive name so database
# failures can be handled separately from reservation validation errors.
from sqlite3 import Error as DatabaseError

# Flask tools used to define routes, read requests, display templates,
# show messages, and redirect the browser.
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

# Business-logic function that retrieves a student's active equipment loans.
from ..business_logic.loan_management import get_active_loans

# Reservation functions handle creation, cancellation, and the current
# reservation date. ReservationError represents a rejected operation,
# such as invalid dates or a reservation that cannot be canceled.
from ..business_logic.reservation_management import (
    ReservationError, cancel_reservation, create_reservation, reservation_today,
)

# Access helpers identify the signed-in user, check CSRF tokens,
# retrieve student records, and restrict who can use each route.
from ..business_logic.user_access import (csrf_is_valid, current_user, get_student_records,
                                          owner_or_staff_required,
                                          role_required)

# Use the configured student-role value for student-only access checks.
from ..config import ROLE_STUDENT

# Database helpers retrieve individual records and manage transactions.
from ..db import get_record, transaction


# Group these routes under a Blueprint named "student".
# Endpoint names include this prefix, such as "student.student_records".
student_bp = Blueprint("student", __name__)


# GET requests display pages. This route opens the student landing page.
@student_bp.get("/student")
# Check the user's role before allowing the function to run.
@role_required(ROLE_STUDENT)
def student_home():
    """Placeholder Student Interface; students land here after login."""

    # Render the page with the signed-in user's information.
    # active_page tells the template which navigation section is active.
    return render_template("student_home.html", active_page="student",
                           user=current_user())


# Requirement 16: Display checked-out equipment and its due dates.
@student_bp.get("/student/loans/active")
@role_required(ROLE_STUDENT)
def active_loans():
    """Show due dates for equipment checked out by the signed-in student."""

    # Use the signed-in user's ID instead of an ID supplied in the URL.
    # This prevents a student from choosing another student's loan list.
    loans = get_active_loans(current_user()["id"])

    # Pass the retrieved loans to the template for display.
    return render_template("active_loans.html", active_page="student", loans=loans)


# Flask reads the integer in the URL and passes it as student_id.
# Example: /students/3/records calls student_records(student_id=3).
@student_bp.get("/students/<int:student_id>/records")
# Only the student who owns these records, or a staff member, may access them.
@owner_or_staff_required("student_id")
def student_records(student_id):
    """A student's private reservations and loans (owner or staff only)."""

    # Retrieve the requested student's information, reservations, and loans.
    data = get_student_records(student_id)

    # Stop with a "Not Found" response if no student records were found.
    if data is None:
        abort(404)

    # **data unpacks the dictionary into named template arguments.
    # For example, {"loans": loan_list} becomes loans=loan_list.
    return render_template("student_records.html", active_page="student",
                           user=current_user(), **data)


# Requirement 8: GET displays the form; POST submits the selected dates.
# The equipment ID comes from the URL.
@student_bp.route("/catalog/<int:equipment_id>/reserve", methods=["GET", "POST"])
@role_required(ROLE_STUDENT)
def reserve_equipment(equipment_id):
    """Show the date form and save valid reservations for the signed-in student."""

    # Before processing a submitted form, check its CSRF token.
    # This helps protect against another website submitting an unwanted
    # request using the student's signed-in browser session.
    if request.method == "POST" and not csrf_is_valid():
        abort(400)

    # Open a managed database transaction using the application's
    # configured database path, then look up the requested equipment.
    with transaction(current_app.config["DATABASE"]) as connection:
        equipment = get_record(connection, "equipment", equipment_id)

    # There is no reservation form to show if this equipment does not exist.
    if equipment is None:
        abort(404)

    # Get the signed-in student and the date used for reservation validation.
    student = current_user()
    today = reservation_today()

    # request.form contains submitted form fields.
    # Keeping it allows the template to redisplay entered values on errors.
    form = request.form

    # Start with no error and a normal HTTP 200 response.
    error = None
    status = 200

    # Process the dates only when the student submits the form.
    if request.method == "POST":
        try:
            # Delegate date validation and saving to the business layer.
            # Ownership comes from the signed-in student, not a form field.
            # .get(..., "") supplies an empty string if a date is missing.
            create_reservation(student["id"], equipment_id, form.get("start_date", ""),
                               form.get("end_date", ""), today=today)

        except ReservationError as exc:
            # A reservation rule rejected the submission.
            # Redisplay the form with its error message and HTTP 400.
            error, status = str(exc), 400

        except DatabaseError:
            # Log technical details for debugging, but show the student
            # a general retry message instead of internal database details.
            current_app.logger.exception("Could not save reservation")
            error, status = "Could not save your reservation. Please try again.", 500

        else:
            # This else belongs to try/except: it runs only if the call
            # completed without raising an exception.
            # Confirm success after the business operation has committed.
            flash("Reservation created successfully.", "success")

            # url_for builds the URL for this student's records page.
            # HTTP 303 tells the browser to follow the redirect with GET,
            # so refreshing that page does not repeat the form submission.
            return redirect(url_for("student.student_records", student_id=student["id"]),
                            code=303)

    # This branch runs for GET requests only.
    # Do not display the form for equipment that is unavailable.
    # POST availability checks are delegated to create_reservation().
    elif equipment["status"] != "available":
        abort(404)

    # Display the initial form or redisplay it after a handled POST error.
    # isoformat() converts today's date to YYYY-MM-DD for the template.
    # Returning (rendered_page, status) sets the HTTP response status.
    return render_template("reserve_equipment.html", active_page="catalog",
                           equipment=equipment, today=today.isoformat(),
                           form=form, error=error), status


# Accept cancellations through POST, since cancellation changes stored data.
@student_bp.post("/student/reservations/<int:reservation_id>/cancel")
@role_required(ROLE_STUDENT)
def cancel_student_reservation(reservation_id):
    """Cancel the student's reservation and report the result on their records page."""

    # Reject the cancellation request if the CSRF token is missing or invalid.
    if not csrf_is_valid():
        abort(400)

    # Use the signed-in student's ID when requesting the cancellation.
    student_id = current_user()["id"]

    try:
        # The business layer checks ownership and cancellation eligibility,
        # then updates the reservation. Cancellation is a status change,
        # rather than deleting the reservation record here.
        cancel_reservation(student_id, reservation_id)

    except ReservationError as exc:
        # Save the reason cancellation was rejected for display after redirect.
        flash(str(exc), "error")

    except DatabaseError:
        # Log the database failure and give the student a retry message.
        current_app.logger.exception("Could not cancel reservation")
        flash("Could not cancel your reservation. Please try again.", "error")

    else:
        # Requirement 25: Confirm cancellation only after the operation succeeds.
        flash("Reservation canceled successfully.", "success")

    # For success or either handled error, return to this student's records.
    # flash() stores feedback for the template to display after the redirect.
    return redirect(url_for("student.student_records", student_id=student_id), code=303)
