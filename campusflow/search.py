"""Read-only search and multi-filter capabilities (Requirement C & D).

OWNER: Engineer B (branch feat/22-search-and-insights)
"""
from .reports import PRIORITY_ORDER
from .tickets import CATEGORIES, ValidationError, format_ticket_list, ticket_number
from .workflow import STATUSES

PRIORITIES = ("low", "medium", "high", "critical")


def normalize_optional_filter(raw, allowed_values, field_name):
    """Validate an optional filter string. Empty string means 'no filter' (None)."""
    cleaned = (raw or "").strip()
    if not cleaned:
        return None
    cleaned_folded = cleaned.casefold()
    for valid in allowed_values:
        if valid.casefold() == cleaned_folded:
            return valid
    raise ValidationError(
        f"Invalid {field_name} filter '{cleaned}'. Choose from: {', '.join(allowed_values)} (or press Enter to skip)."
    )


def search_tickets(tickets, title_query="", category=None, status=None, priority=None, sort_by_priority=False):
    """Filter tickets without mutating the input collection.

    All supplied filters combine with logical AND.
    """
    query_folded = (title_query or "").strip().casefold()
    cat_filter = normalize_optional_filter(category, CATEGORIES, "category")
    stat_filter = normalize_optional_filter(status, STATUSES, "status")
    prio_filter = normalize_optional_filter(priority, PRIORITIES, "priority")

    results = []
    for ticket in tickets:
        if query_folded and query_folded not in ticket["title"].casefold():
            continue
        if cat_filter is not None and ticket["category"] != cat_filter:
            continue
        if stat_filter is not None and ticket["status"] != stat_filter:
            continue
        if prio_filter is not None and ticket["priority"] != prio_filter:
            continue
        results.append(ticket)

    if sort_by_priority:
        results.sort(key=lambda t: (PRIORITY_ORDER[t["priority"]], ticket_number(t["id"])))

    return results


def format_search_results(tickets):
    """Format matched tickets using the standard read-only table layout."""
    if not tickets:
        return "No matching tickets found."
    return format_ticket_list(tickets)