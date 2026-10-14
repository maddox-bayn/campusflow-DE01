"""Ticket creation, validation, lookup and display (F1 CREATE, F2 LIST / VIEW).

OWNER: Engineer A  (branch feat/1-ticket-core-management)

Tickets are plain dictionaries kept in one in-memory list:
    id, title, category, urgency, affected_users, priority, status, assigned_to
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
        ]
    )