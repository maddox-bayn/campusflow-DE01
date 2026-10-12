"""Assignment and status workflow (F3 ASSIGN, F4 WORKFLOW).

OWNER: Engineer B  (branch feat/2-ticket-operations-reporting)

Allowed path: open -> in_progress -> resolved.
A resolved ticket is locked until reopen_ticket() sets it back to open.
"""
from .tickets import TicketError, get_ticket

STATUSES = ("open", "in_progress", "resolved")
ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": set(),
}


class WorkflowError(TicketError):
    """Raised when an assignment or status change is not allowed."""


def assign_ticket(tickets, ticket_id, staff_name):
    ticket = get_ticket(tickets, ticket_id)  # unknown ID -> TicketNotFoundError
    name = (staff_name or "").strip()
    if not name:
        raise WorkflowError("Staff name cannot be empty.")
    if ticket["status"] == "resolved":
        raise WorkflowError(f"{ticket['id']} is resolved. Reopen it before changing it.")
    ticket["assigned_to"] = name
    return ticket


def change_status(tickets, ticket_id, new_status):
    ticket = get_ticket(tickets, ticket_id)
    new_status = (new_status or "").strip().lower()
    if new_status not in STATUSES:
        raise WorkflowError(f"Status must be one of: {', '.join(STATUSES)}.")

    current = ticket["status"]
    if current == "resolved":
        raise WorkflowError(f"{ticket['id']} is resolved. Use reopen to modify it.")
    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise WorkflowError(f"Cannot move {ticket['id']} from {current} to {new_status}.")
    if new_status == "in_progress" and not ticket["assigned_to"]:
        raise WorkflowError(f"Assign {ticket['id']} to someone before starting work.")

    ticket["status"] = new_status
    return ticket


def reopen_ticket(tickets, ticket_id):
    ticket = get_ticket(tickets, ticket_id)
    if ticket["status"] != "resolved":
        raise WorkflowError(f"{ticket['id']} is not resolved, so it cannot be reopened.")
    ticket["status"] = "open"
    return ticket