"""CampusFlow command-line interface.

Engineer A owns the CLI loop and the menu entries for F1/F2/F7.
Engineer B owns the handlers marked ENGINEER B (F3-F6); they only call B's modules.
"""
import sys

from campusflow.reports import format_report, format_work_queue
from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import (
    TicketError, create_ticket, format_ticket_detail, format_ticket_list, get_ticket,
)
from campusflow.workflow import assign_ticket, change_status, reopen_ticket

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
    ticket = change_status(tickets, input("Ticket ID: "), input("New status (in_progress/resolved): "))
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


HANDLERS = {
    "1": handle_create, "2": handle_list, "3": handle_assign, "4": handle_status,
    "5": handle_reopen, "6": handle_queue, "7": handle_reports,
}