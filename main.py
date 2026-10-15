"""CampusFlow command-line interface.

Engineer A owns the CLI loop and the menu entries for F1/F2/F7.
Engineer B owns the handlers marked ENGINEER B (F3-F6 + CampusFlow Next menus).
"""
import sys

from campusflow.reports import format_report, format_work_queue
from campusflow.search import (
    PRIORITIES,
    format_search_results,
    normalize_optional_filter,
    search_tickets,
)
from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import (
    CATEGORIES,
    TicketError,
    add_note,
    create_ticket,
    format_ticket_detail,
    format_ticket_list,
    format_ticket_notes,
    get_ticket,
)
from campusflow.understanding_check import run_understanding_check
from campusflow.workflow import STATUSES, assign_ticket, change_status, reopen_ticket

DATA_FILE = "tickets.json"


# ----------------------------------------------------------- ENGINEER A handlers
def handle_create(tickets):
    ticket = create_ticket(
        tickets,
        input("Title: "),
        input("Category (Network/Hardware/Software/Other): "),
        input("Urgency (low/medium/high): "),
        input("Affected users: "),
    )
    save_tickets(tickets, DATA_FILE)
    print(f"Created {ticket['id']} with {ticket['priority']} priority.")


def handle_list(tickets):
    print(format_ticket_list(tickets))
    if tickets:
        chosen = input("\nTicket ID to view in detail (Enter to skip): ").strip()
        if chosen:
            print(format_ticket_detail(get_ticket(tickets, chosen)))


# ----------------------------------------------------------- ENGINEER B handlers
def handle_assign(tickets):
    ticket = assign_ticket(tickets, input("Ticket ID: "), input("Staff member name: "))
    save_tickets(tickets, DATA_FILE)
    print(f"{ticket['id']} assigned to {ticket['assigned_to']}.")


def handle_status(tickets):
    ticket = change_status(
        tickets,
        input("Ticket ID: "),
        input("New status (in_progress/resolved): "),
    )
    save_tickets(tickets, DATA_FILE)
    print(f"{ticket['id']} is now {ticket['status']}.")


def handle_reopen(tickets):
    ticket = reopen_ticket(tickets, input("Ticket ID: "))
    save_tickets(tickets, DATA_FILE)
    print(f"{ticket['id']} reopened.")


def handle_queue(tickets):
    print(format_work_queue(tickets))


def handle_reports(tickets):
    print(format_report(tickets))


def _prompt_valid_filter(prompt_text, allowed_values, field_name):
    """Re-prompt until the user enters a valid filter value or blank to skip."""
    while True:
        raw = input(prompt_text)
        try:
            return normalize_optional_filter(raw, allowed_values, field_name)
        except TicketError as err:
            print(f"[Error] {err}")


def handle_search(tickets):
    title_query = input("Search title substring (Enter to skip): ")
    category = _prompt_valid_filter(
        "Filter by category (Network/Hardware/Software/Other or Enter to skip): ",
        CATEGORIES,
        "category",
    )
    status = _prompt_valid_filter(
        "Filter by status (open/in_progress/resolved or Enter to skip): ",
        STATUSES,
        "status",
    )
    priority = _prompt_valid_filter(
        "Filter by priority (low/medium/high/critical or Enter to skip): ",
        PRIORITIES,
        "priority",
    )
    sort_choice = input("Sort results by priority then ID? (y/N): ").strip().lower()
    sort_by_prio = sort_choice in ("y", "yes")

    matches = search_tickets(
        tickets,
        title_query=title_query,
        category=category,
        status=status,
        priority=priority,
        sort_by_priority=sort_by_prio,
    )
    print(format_search_results(matches))


def handle_add_note(tickets):
    ticket_id = input("Ticket ID: ")
    author = input("Note author: ")
    message = input("Note message (5-300 chars): ")
    note = add_note(tickets, ticket_id, author, message)
    save_tickets(tickets, DATA_FILE)
    print(f"Added note {note['note_id']} to {ticket_id.strip().upper()}.")


def handle_view_notes(tickets):
    ticket_id = input("Ticket ID: ")
    print(format_ticket_notes(tickets, ticket_id))


def handle_understanding_check(tickets):
    run_understanding_check()


# ----------------------------------------------------------- Menu & Dispatch
HANDLERS = {
    "1": handle_create,
    "2": handle_list,
    "3": handle_assign,
    "4": handle_status,
    "5": handle_reopen,
    "6": handle_queue,
    "7": handle_reports,
    "8": handle_search,
    "9": handle_add_note,
    "10": handle_view_notes,
    "11": handle_understanding_check,
}

MENU = """
--- CAMPUSFLOW NEXT ---
1. Create ticket
2. List / view tickets
3. Assign ticket
4. Update status
5. Reopen resolved ticket
6. Work queue
7. Reports
8. Search tickets
9. Add follow-up note
10. View ticket notes
11. Engineering Understanding Check
12. Exit"""


# ------------------------------------------------------------ ENGINEER A: loop
def main():
    try:
        tickets = load_tickets(DATA_FILE)
    except StorageError as err:
        print(f"[Error] {err}")
        return 1

    while True:
        print(MENU)
        choice = input("Choose 1-12: ").strip()
        if choice == "12":
            print("Goodbye.")
            return 0
        handler = HANDLERS.get(choice)
        if handler is None:
            print("[Error] Please choose a number from 1 to 12.")
            continue
        try:
            handler(tickets)
        except (TicketError, StorageError) as err:
            print(f"[Error] {err}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0


if __name__ == "__main__":
    sys.exit(main())