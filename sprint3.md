# CampusGear — Sprint 3 Plan and Requirements Artifacts

## Sprint Overview

**Sprint:** 3 of 4  
**Sprint Length:** 1 week  
**Total Product Backlog:** 189 story points  
**Sprint 3 Commitment:** 47 story points  

**Sprint Goal:** Strengthen CampusGear's reservation reliability and equipment-management capabilities. The system will prevent simultaneous reservation requests from double-booking the same equipment, allow staff to report damage and manage repair work, support equipment updates and catalog search/filtering, block equipment during maintenance, notify students about overdue equipment, and give staff an overview of equipment and repair activity.

## Sprint 3 Requirements

| Requirement ID | Requirement | Story Points | Priority |
|---|---|---:|---:|
| 14 | Prevent simultaneous reservation requests from double-booking the same equipment | 8 | 14 |
| 17 | Allow staff to report damaged equipment and record the damage details | 3 | 17 |
| 18 | Allow staff to create repair tickets for damaged equipment | 5 | 18 |
| 19 | Allow staff to update the status of repair tickets | 5 | 19 |
| 20 | Allow staff to update existing equipment information | 3 | 20 |
| 21 | Allow users to search and filter the equipment catalog | 5 | 21 |
| 22 | Allow staff to mark equipment unavailable during maintenance | 8 | 22 |
| 23 | Notify students when borrowed equipment becomes overdue | 5 | 23 |
| 24 | Display an equipment-management dashboard for staff | 5 | 24 |
|  | **Total** | **47** | |

## Sprint Goal

At the end of Sprint 3, CampusGear should handle competing reservation requests safely so that the same equipment cannot be booked by two students for overlapping dates. Staff should be able to document equipment damage, create repair tickets, update repair progress, edit equipment information, and mark equipment unavailable while maintenance is taking place. Students and staff should be able to find equipment using catalog search and filters, students should receive an overdue reminder for an unreturned loan, and staff should be able to review key equipment, loan, maintenance, and repair information from a dashboard.

---

# Sprint 3 Requirements Artifacts

## Requirement 14 — Prevent Simultaneous Double Bookings

**Story Points:** 8

**Description:**

The system shall prevent two students from successfully reserving the same equipment for overlapping dates when reservation requests are submitted at nearly the same time. The system must check availability and save a reservation as one protected operation so that two requests cannot both pass the availability check before either reservation is recorded.

**Inputs:**
- Selected equipment
- Reservation start date
- Reservation end date
- Student account
- Existing reservation records
- Existing active loan records
- Other reservation requests being processed for the same equipment

**Expected Output:**
- A saved reservation for the request that successfully obtains the equipment for the requested dates.
- An error message for a competing request when the equipment has already been reserved or made unavailable for overlapping dates.
- No duplicate or overlapping reservation records created by simultaneous requests.

**Acceptance Criteria:**
- The system checks the equipment's reservation and loan records when a reservation is submitted.
- The availability check and reservation creation are handled as one protected operation.
- When two students submit overlapping reservation requests for the same equipment at nearly the same time, no more than one request succeeds.
- The request that cannot be completed receives a clear message that the equipment is no longer available for the selected dates.
- The system does not create a reservation record for a request that loses the availability check.
- Reservations for the same equipment are allowed when their date ranges do not overlap and no active loan or maintenance restriction makes the equipment unavailable.
- A failed reservation attempt does not leave partially saved reservation data.
- The system continues to enforce the normal reservation date-validation rules.

**Verification Steps:**
1. Prepare one equipment item that has no reservation, active loan, or maintenance restriction for the test dates.
2. Log in using two separate student accounts in separate browser sessions.
3. Select the same equipment and the same overlapping reservation dates in both sessions.
4. Submit both reservation requests as close together as possible.
5. Verify that only one request succeeds.
6. Verify that the other session receives an unavailable-equipment message.
7. Inspect the database or reservation list and verify that only one reservation exists for the overlapping date range.
8. Repeat the test with two requests whose date ranges do not overlap.
9. Verify that both non-overlapping reservations can be saved when the equipment is otherwise available.
10. Attempt another reservation for dates that overlap the successful reservation and verify that the system rejects it.

## Requirement 17 — Report Damaged Equipment

**Story Points:** 3

**Description:**

The system shall allow staff members to record a damage report for equipment that is damaged, malfunctioning, or otherwise not suitable for use. The report must identify the equipment, describe the problem, record when the problem was reported, and identify the staff member who submitted the report.

**Inputs:**
- Staff account
- Equipment record
- Damage description
- Date the damage was reported
- Equipment condition or severity, when applicable

**Expected Output:**
- A saved damage report associated with the correct equipment item and staff member.
- The equipment marked unavailable when the reported damage makes it unsafe or unsuitable to borrow.
- A confirmation message after the report is saved.

**Acceptance Criteria:**
- Only an authenticated staff member can submit a damage report.
- A damage report must be associated with an existing equipment record.
- The report records a description of the damage and the date it was reported.
- The report identifies the staff account that submitted it.
- The system does not save a report when required information is missing.
- Equipment that is reported as unsafe or unusable is not displayed as available for reservation or checkout.
- Saving a damage report does not delete or overwrite the equipment's existing loan or reservation history.
- The system displays a confirmation after a report is successfully saved and an error when it cannot be saved.

**Verification Steps:**
1. Log in using a staff account.
2. Navigate to the equipment-management area.
3. Select an existing equipment item.
4. Open the damage-report form.
5. Enter a damage description and submit the report.
6. Verify that the report is saved and linked to the selected equipment.
7. Verify that the report includes the reporting staff member and report date.
8. Verify that equipment reported as unsafe or unusable is no longer shown as available.
9. Attempt to submit a damage report without a required description or equipment selection.
10. Verify that the system displays a validation message and does not save an incomplete report.
11. Log in using a student account and verify that the student cannot access the staff damage-report function.

## Requirement 18 — Create Repair Tickets

**Story Points:** 5

**Description:**

The system shall allow staff members to create a repair ticket for equipment that requires inspection, service, or repair. Each repair ticket must identify the equipment and describe the issue so staff can track the work needed to return the item to usable condition. A repair ticket may be associated with an existing damage report when one is available.

**Inputs:**
- Staff account creating the ticket
- Equipment record
- Repair or maintenance issue description
- Date the ticket was created
- Related damage report, when applicable

**Expected Output:**
- A new repair ticket with a unique identifier.
- The repair ticket associated with the correct equipment item.
- The ticket saved with an initial status such as Open or Reported.
- A confirmation message after successful creation.

**Acceptance Criteria:**
- Only authenticated staff members can create repair tickets.
- Each repair ticket is associated with an existing equipment record.
- Each ticket contains a description of the repair or inspection needed.
- The system assigns each ticket a unique identifier.
- The system records the ticket creation date and the staff member who created it.
- A repair ticket can be linked to a damage report for the same equipment when a damage report exists.
- A ticket cannot be created with missing required equipment or issue information.
- Creating a ticket does not remove the equipment's existing history or associated loan records.
- The system displays a confirmation when the ticket is saved and an error when creation fails.

**Verification Steps:**
1. Log in using a staff account.
2. Navigate to the repair or maintenance-management page.
3. Select equipment that has a damage report or requires service.
4. Create a repair ticket with a description of the work needed.
5. Submit the ticket.
6. Verify that the ticket is saved with a unique identifier.
7. Verify that the ticket is associated with the correct equipment.
8. Verify that the creation date and staff account are recorded.
9. Verify that the ticket is linked to the related damage report when one is selected.
10. Attempt to create a ticket without selecting equipment or entering an issue description.
11. Verify that the system rejects the incomplete ticket.
12. Log in using a student account and verify that the student cannot create repair tickets.

## Requirement 19 — Update Repair Ticket Status

**Story Points:** 5

**Description:**

The system shall allow staff members to update the status of an existing repair ticket as work progresses. Staff should be able to identify tickets that are open, in progress, resolved, or canceled. The system must preserve the ticket's equipment association and repair history when its status changes.

**Inputs:**
- Staff account
- Existing repair ticket
- New repair ticket status
- Status update date
- Optional repair notes or resolution details

**Expected Output:**
- The repair ticket saved with its updated status.
- The date of the status update recorded.
- Any entered repair or resolution notes associated with the ticket.
- A confirmation message after a successful update.

**Acceptance Criteria:**
- Staff members can view existing repair tickets.
- Staff members can update the status of a repair ticket.
- The system supports the agreed ticket statuses, such as Open, In Progress, Resolved, and Canceled.
- The system records the updated status and the date of the change.
- Staff can add notes describing the repair work or resolution when applicable.
- A ticket's equipment association and original issue description remain intact after an update.
- The system does not allow an update to a ticket that does not exist.
- Equipment is not automatically made available merely because a ticket is marked Resolved; staff must verify that the equipment is usable and that no maintenance restriction remains.
- Students cannot update repair-ticket statuses.

**Verification Steps:**
1. Log in using a staff account.
2. Navigate to the repair-ticket list.
3. Select an existing Open repair ticket.
4. Change its status to In Progress and save the update.
5. Verify that the new status and update date are stored.
6. Add a repair note and verify that it remains associated with the ticket.
7. Change the ticket status to Resolved after the repair is complete.
8. Verify that the original equipment and issue information are still present.
9. Verify that the equipment remains unavailable until its condition and any maintenance restriction are cleared.
10. Attempt to update a nonexistent ticket and verify that the system displays an error.
11. Log in using a student account and verify that the student cannot update repair tickets.

## Requirement 20 — Update Equipment Information

**Story Points:** 3

**Description:**

The system shall allow staff members to update the information stored for an existing equipment item. Staff should be able to correct or change identifying information and descriptive details while preserving the equipment record and its associated reservation, loan, damage, and repair history.

**Inputs:**
- Staff account
- Existing equipment record
- Updated equipment name
- Updated category
- Updated description
- Updated condition or other editable equipment details

**Expected Output:**
- The existing equipment record saved with the updated information.
- A confirmation message after a successful update.
- A validation message when required information is missing or invalid.

**Acceptance Criteria:**
- Only authenticated staff members can update equipment information.
- Staff can select an existing equipment item to edit.
- The system allows staff to update the supported equipment details, including name, category, description, and condition.
- Required fields cannot be saved as blank.
- An equipment update changes the existing record rather than creating a duplicate equipment item.
- The equipment's unique asset identifier remains unique; duplicate asset identifiers are rejected if the identifier can be edited.
- Updating equipment information does not delete or change its reservation, loan, damage-report, or repair-ticket history.
- Changes are visible when the equipment item is viewed again in the catalog or staff equipment list.
- Students cannot edit equipment records.

**Verification Steps:**
1. Log in using a staff account.
2. Navigate to the equipment-management page.
3. Select an existing equipment item and open its edit form.
4. Change its name, category, description, or condition.
5. Save the changes.
6. Verify that the existing equipment record displays the updated information.
7. Verify that the equipment was updated rather than duplicated.
8. Verify that any existing reservation, loan, damage, or repair records remain associated with the equipment.
9. Attempt to save the form with a required field missing.
10. Verify that the system displays a validation message and does not save invalid information.
11. If asset identifiers are editable, attempt to use an identifier already assigned to another item and verify that the system rejects it.
12. Log in using a student account and verify that equipment-editing actions are unavailable or denied.

## Requirement 21 — Search and Filter the Equipment Catalog

**Story Points:** 5

**Description:**

The system shall allow users to search and filter the equipment catalog to locate equipment that matches their needs. Users should be able to search by equipment name or keyword and narrow the displayed results using supported filters such as category and availability.

**Inputs:**
- Search text or keyword
- Selected equipment category filter
- Selected availability or status filter, when supported
- Equipment records in the catalog

**Expected Output:**
- A list of equipment records that match the entered search text and selected filters.
- A clear message when no equipment matches the search or filter selections.
- The ability to clear the search and filters and return to the unfiltered catalog.

**Acceptance Criteria:**
- Users can enter a search term to locate equipment by name or supported descriptive text.
- Users can filter equipment by category.
- Users can filter equipment by availability or status when that filter is provided in the interface.
- Search terms and selected filters are applied to the equipment records rather than only hiding unrelated hard-coded page content.
- Search and filter selections can be used together.
- Search results display enough information to identify each matching equipment item.
- The system displays a clear empty-state message when no equipment matches.
- Users can clear the search and filters to display the full catalog again.
- Search results do not incorrectly label unavailable, checked-out, damaged, or maintenance-blocked equipment as available.

**Verification Steps:**
1. Open the equipment catalog.
2. Search for an equipment item by its full name.
3. Verify that the matching item appears.
4. Search using a partial name or keyword and verify that matching results appear.
5. Select a category filter and verify that only equipment in that category is displayed.
6. Combine a search term with a category or availability filter and verify that both are applied.
7. Search for a term that does not match any equipment.
8. Verify that the system displays a clear no-results message.
9. Clear the search term and filters.
10. Verify that the catalog returns to its normal unfiltered view.
11. Verify that unavailable or maintenance-blocked equipment is not shown as available in the results.

## Requirement 22 — Mark Equipment Unavailable During Maintenance

**Story Points:** 8

**Description:**

The system shall allow staff members to mark equipment as unavailable when it requires scheduled maintenance, inspection, or servicing. Staff must be able to record the maintenance reason and applicable maintenance period. Equipment subject to a maintenance restriction must not be reserved or checked out while the restriction is active.

**Inputs:**
- Staff account
- Equipment record
- Maintenance reason or description
- Maintenance start date
- Maintenance end date, when known
- Maintenance status or release action

**Expected Output:**
- A maintenance record or restriction associated with the selected equipment.
- Equipment marked unavailable for the active maintenance period.
- Reservation and checkout requests blocked when they overlap the maintenance period.
- Equipment returned to an available status only after staff clears the restriction and confirms that the item can be used.

**Acceptance Criteria:**
- Only authenticated staff members can create or clear a maintenance restriction.
- Staff can select an existing equipment item and record why it requires maintenance.
- The system records the maintenance start date and an end date when one is known.
- Equipment under active maintenance is not displayed as available.
- Students cannot reserve equipment for dates that overlap an active maintenance restriction.
- Staff cannot directly check out equipment while an active maintenance restriction applies.
- The system allows reservations outside the maintenance period when no other reservation, loan, or status restriction applies.
- Staff can clear or complete a maintenance restriction after the work is finished.
- Clearing a maintenance restriction does not automatically make equipment available if it is still damaged, checked out, or subject to another restriction.
- The maintenance information remains recorded for staff review.

**Verification Steps:**
1. Log in using a staff account.
2. Navigate to the equipment-management or maintenance page.
3. Select an equipment item that is currently available.
4. Create a maintenance restriction with a reason and start date; enter an end date if known.
5. Save the restriction.
6. Verify that the equipment is no longer displayed as available during the maintenance period.
7. Log in using a student account and attempt to reserve the equipment for dates that overlap maintenance.
8. Verify that the reservation is rejected with an appropriate message.
9. Log in as staff and attempt a direct checkout of the same equipment while maintenance is active.
10. Verify that the system prevents checkout.
11. Attempt to reserve the equipment for dates outside the maintenance period, with no other restrictions in place.
12. Verify that the system allows the valid reservation.
13. Complete or clear the maintenance restriction as staff.
14. Verify that the equipment becomes available only when no other condition or status prevents borrowing.

## Requirement 23 — Notify Students About Overdue Equipment

**Story Points:** 5

**Description:**

The system shall identify active equipment loans whose expected return dates have passed and notify the associated students that their equipment is overdue. The reminder must identify the overdue equipment and its due date so students know which item needs to be returned.

**Inputs:**
- Active loan records
- Expected return dates
- Current date
- Student account associated with each loan
- Equipment information

**Expected Output:**
- An overdue reminder associated with the student who has the overdue loan.
- The reminder identifies the equipment item and its expected return date.
- A record that the reminder was generated or displayed, where notification history is supported.

**Acceptance Criteria:**
- The system identifies loans that have not been returned and whose expected return dates are earlier than the current date.
- The system does not classify a returned loan as overdue.
- The system associates each reminder with the student who borrowed the equipment.
- The reminder identifies the overdue equipment and its expected return date.
- Students can view reminders associated with their own accounts.
- Students cannot view overdue reminders belonging to other students.
- The system does not display an overdue reminder for a loan that has not passed its expected return date.
- The same overdue loan is not repeatedly represented as a new reminder every time the student opens the page, unless the system's notification rules intentionally create a new reminder.
- Staff can determine which loans are overdue using the loan information available to them.

**Verification Steps:**
1. Prepare an active loan whose expected return date is earlier than the current date.
2. Prepare a second active loan whose expected return date is today or in the future.
3. Prepare a returned loan whose expected return date is in the past.
4. Log in using the student account associated with the overdue active loan.
5. Navigate to the student's notifications or loan page.
6. Verify that an overdue reminder appears for the past-due active loan.
7. Verify that the reminder identifies the correct equipment and due date.
8. Verify that the not-yet-overdue loan does not receive an overdue reminder.
9. Verify that the returned loan does not receive an overdue reminder.
10. Log in using a different student account and verify that the first student's reminder is not visible.
11. Verify that staff can identify the overdue loan from the staff-facing loan or dashboard view.

## Requirement 24 — Display an Equipment-Management Dashboard for Staff

**Story Points:** 5

**Description:**

The system shall provide staff members with a dashboard that summarizes important equipment and borrowing information. The dashboard should help staff understand the current state of the equipment inventory and identify items that are checked out, unavailable, overdue, under maintenance, or associated with open repair work.

**Inputs:**
- Staff account
- Equipment records and equipment statuses
- Active and returned loan records
- Reservation records, where applicable
- Maintenance records
- Damage reports and repair tickets

**Expected Output:**
- A staff-only dashboard displaying summary counts or lists for key equipment and loan statuses.
- Current information retrieved from the system's stored records.
- Links or navigation to the related management pages when those pages are available.

**Acceptance Criteria:**
- Only authenticated staff members can access the staff equipment dashboard.
- The dashboard displays the total number of equipment records.
- The dashboard summarizes equipment by relevant statuses, such as Available, Checked Out, Unavailable, or Under Maintenance.
- The dashboard identifies the number of overdue active loans.
- The dashboard summarizes open or in-progress repair tickets when repair-ticket data exists.
- Dashboard values are based on stored application records and reflect changes after equipment, loan, maintenance, or repair information is updated.
- A dashboard count is consistent with the corresponding records in the system.
- The dashboard displays a reasonable empty state when there are no records for a category.
- Students cannot access the staff dashboard or its private management information.

**Verification Steps:**
1. Log in using a staff account.
2. Navigate to the staff dashboard.
3. Verify that the dashboard displays the total equipment count.
4. Compare the displayed equipment-status counts with the equipment records in the database or staff inventory list.
5. Verify that the dashboard's overdue-loan count matches the active overdue loans.
6. Verify that open or in-progress repair-ticket information matches the repair-ticket records.
7. Change an equipment status or update a loan, maintenance record, or repair ticket.
8. Refresh the dashboard and verify that the relevant summary values reflect the update.
9. Test a category with no matching records and verify that the dashboard displays an appropriate zero or empty state.
10. Log out and log in using a student account.
11. Attempt to access the staff dashboard directly and verify that access is denied.
