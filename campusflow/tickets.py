"""Ticket creation, validation, lookup and display (F1 CREATE, F2 LIST / VIEW).

OWNER: Engineer A  (branch feat/1-ticket-core-management)

Tickets are plain dictionaries kept in one in-memory list:
    id, title, category, urgency, affected_users, priority, status, assigned_to, notes
"""

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCIES = ("low", "medium", "high")


class TicketError(Exception):
    """Base class for every expected, user-facing error."""


class ValidationError(TicketError):
    """Raised when user input is rejected."""


class TicketNotFoundError(TicketError):
    """Raised when a ticket ID does not exist."""


# ---------------------------------------------------------------- validation
def validate_title(raw):
    title = (raw or "").strip()
    if not title:
        raise ValidationError("Title cannot be blank.")
    return title


def normalize_category(raw):
    value = (raw or "").strip().lower()
    for category in CATEGORIES:
        if category.lower() == value:
            return category
    raise ValidationError(f"Category must be one of: {', '.join(CATEGORIES)}.")


def normalize_urgency(raw):
    value = (raw or "").strip().lower()
    if value not in URGENCIES:
        raise ValidationError(f"Urgency must be one of: {', '.join(URGENCIES)}.")
    return value


def parse_affected_users(raw):
    # Explicitly reject booleans (since isinstance(True, int) is True in Python) and floats
    if isinstance(raw, bool) or isinstance(raw, float):
        raise ValidationError("Affected users must be a whole number greater than 0.")
    if isinstance(raw, int):
        if raw <= 0:
            raise ValidationError("Affected users must be greater than 0.")
        return raw
    if isinstance(raw, str):
        text = raw.strip()
        if text.isascii() and text.isdigit():
            number = int(text)
            if number > 0:
                return number
    raise ValidationError("Affected users must be a whole number greater than 0.")


# ------------------------------------------------------------------ priority
def calculate_priority(urgency, affected_users):
    """Rules are checked in this exact order (design contract)."""
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


# ----------------------------------------------------------------------- IDs
def ticket_number(ticket_id):
    """'T012' -> 12 (used for numeric tie-breaking and ID generation)."""
    return int(ticket_id[1:])


def next_ticket_id(tickets):
    """Next ID is max existing number + 1, so IDs stay unique after a reload."""
    highest = max((ticket_number(t["id"]) for t in tickets), default=0)
    return f"T{highest + 1:03d}"


# -------------------------------------------------------------------- create
def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate input, build the ticket, append it to `tickets` and return it."""
    ticket = {
        "id": next_ticket_id(tickets),
        "title": validate_title(title),
        "category": normalize_category(category),
        "urgency": normalize_urgency(urgency),
        "affected_users": parse_affected_users(affected_users),
        "priority": None,
        "status": "open",
        "assigned_to": None,
        "notes": [],  # <-- Added notes list
    }
    ticket["priority"] = calculate_priority(ticket["urgency"], ticket["affected_users"])
    tickets.append(ticket)
    return ticket


# -------------------------------------------------------------------- lookup
def get_ticket(tickets, ticket_id):
    """Return the ticket with this ID (case-insensitive) or raise."""
    wanted = (ticket_id or "").strip().upper()
    for ticket in tickets:
        if ticket["id"] == wanted:
            return ticket
    raise TicketNotFoundError(f"No ticket with ID '{(ticket_id or '').strip()}'.")


# ------------------------------------------------------------------- display
def format_ticket_list(tickets):
    if not tickets:
        return "No tickets recorded yet."
    lines = [
        f"{'ID':<6} | {'Title':<24} | {'Category':<9} | {'Priority':<8} | {'Status':<11} | Assigned",
        "-" * 82,
    ]
    for t in tickets:
        title = t["title"] if len(t["title"]) <= 24 else t["title"][:21] + "..."
        lines.append(
            f"{t['id']:<6} | {title:<24} | {t['category']:<9} | {t['priority']:<8} | "
            f"{t['status']:<11} | {t['assigned_to'] or 'unassigned'}"
        )
    return "\n".join(lines)


def format_ticket_detail(ticket):
    notes = ticket.get("notes", [])
    return "\n".join(
        [
            f"=== Ticket {ticket['id']} ===",
            f"Title:          {ticket['title']}",
            f"Category:       {ticket['category']}",
            f"Urgency:        {ticket['urgency']}",
            f"Affected users: {ticket['affected_users']}",
            f"Priority:       {ticket['priority']}",
            f"Status:         {ticket['status']}",
            f"Assigned to:    {ticket['assigned_to'] or 'unassigned'}",
            f"Notes count:    {len(notes)}",
        ]
    )


# --------------------------------------------------------------------- notes
def note_number(note_id):
    """'N005' -> 5."""
    if (
        not isinstance(note_id, str)
        or len(note_id) < 2
        or not note_id.startswith("N")
        or not (note_id[1:].isascii() and note_id[1:].isdigit())
    ):
        raise ValidationError(f"Invalid note ID format: '{note_id}'.")
    num = int(note_id[1:])
    if num <= 0:
        raise ValidationError(f"Invalid note ID number: '{note_id}'.")
    return num


def next_note_id(ticket):
    """Return next sequential note ID (N001, N002...) for a single ticket."""
    notes = ticket.get("notes", [])
    highest = max((note_number(n["note_id"]) for n in notes), default=0)
    return f"N{highest + 1:03d}"


def validate_note_input(author, message):
    """Validate author and message (5-300 chars) before mutating any state."""
    if not isinstance(author, str) or not author.strip():
        raise ValidationError("Note author cannot be blank.")
    if not isinstance(message, str):
        raise ValidationError("Note message must be between 5 and 300 characters.")

    clean_author = author.strip()
    clean_message = message.strip()
    if len(clean_message) < 5 or len(clean_message) > 300:
        raise ValidationError("Note message must be between 5 and 300 characters.")

    return clean_author, clean_message


def add_note(tickets, ticket_id, author, message):
    """Validate and append a follow-up note to an open or in_progress ticket.

    Rejected notes never mutate the ticket or consume a note ID.
    """
    ticket = get_ticket(tickets, ticket_id)
    if ticket["status"] not in ("open", "in_progress"):
        raise ValidationError(
            f"Cannot add a note to {ticket['id']} while status is '{ticket['status']}'. "
            "Reopen the ticket first."
        )

    clean_author, clean_message = validate_note_input(author, message)
    if "notes" not in ticket or not isinstance(ticket["notes"], list):
        ticket["notes"] = []

    note = {
        "note_id": next_note_id(ticket),
        "author": clean_author,
        "message": clean_message,
    }
    ticket["notes"].append(note)
    return note


def get_ticket_notes(tickets, ticket_id):
    """Return all notes for a ticket ordered by numeric note ID."""
    ticket = get_ticket(tickets, ticket_id)
    notes = list(ticket.get("notes", []))
    notes.sort(key=lambda n: note_number(n["note_id"]))
    return notes


def format_ticket_notes(tickets, ticket_id):
    """Format all notes for a ticket for CLI display (used by Engineer B)."""
    ticket = get_ticket(tickets, ticket_id)
    notes = get_ticket_notes(tickets, ticket_id)
    if not notes:
        return f"No follow-up notes for {ticket['id']}."
    lines = [f"=== Notes for {ticket['id']} ({ticket['title']}) ==="]
    for n in notes:
        lines.append(f"[{n['note_id']}] {n['author']}: {n['message']}")
    return "\n".join(lines)