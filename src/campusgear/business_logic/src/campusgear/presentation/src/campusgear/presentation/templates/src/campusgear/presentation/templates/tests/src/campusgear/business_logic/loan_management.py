"""Read the equipment and due dates for a student's active loans."""

from flask import current_app

from ..db import transaction


def get_active_loans(student_id):
    """Return currently checked-out equipment, ordered by expected return date."""
    with transaction(current_app.config["DATABASE"]) as connection:
        # The loan supplies the due date. The equipment join supplies its name
        # and asset ID so students can distinguish items with the same name.
        return connection.execute(
            """
            SELECT e.name AS equipment_name, e.asset_id, l.due_date
            FROM loans AS l
            JOIN equipment AS e ON e.id = l.equipment_id
            WHERE l.user_id = ? AND l.status = 'checked_out'
            ORDER BY l.due_date, l.id
            """,
            (student_id,),
        ).fetchall()
