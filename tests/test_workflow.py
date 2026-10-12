"""ENGINEER B tests: assignment, transitions, work queue order, empty reports."""
import unittest

from campusflow.reports import build_report, work_queue
from campusflow.tickets import TicketNotFoundError, create_ticket
from campusflow.workflow import WorkflowError, assign_ticket, change_status, reopen_ticket


def make(tickets, title="t", urgency="low", users="1"):
    return create_ticket(tickets, title, "Other", urgency, users)


class TestAssignment(unittest.TestCase):
    def test_unknown_id_and_empty_name_rejected(self):
        tickets = []
        make(tickets)
        with self.assertRaises(TicketNotFoundError):
            assign_ticket(tickets, "T999", "Sam")
        with self.assertRaises(WorkflowError):
            assign_ticket(tickets, "T001", "   ")


class TestTransitions(unittest.TestCase):
    def test_unassigned_cannot_start(self):
        tickets = []
        make(tickets)
        with self.assertRaises(WorkflowError):
            change_status(tickets, "T001", "in_progress")

    def test_happy_path_and_no_skipping(self):
        tickets = []
        make(tickets)
        with self.assertRaises(WorkflowError):  # open -> resolved is not allowed
            change_status(tickets, "T001", "resolved")
        assign_ticket(tickets, "T001", "Sam")
        self.assertEqual(change_status(tickets, "T001", "in_progress")["status"], "in_progress")
        self.assertEqual(change_status(tickets, "T001", "resolved")["status"], "resolved")

    def test_resolved_locked_until_reopened(self):
        tickets = []
        make(tickets)
        assign_ticket(tickets, "T001", "Sam")
        change_status(tickets, "T001", "in_progress")
        change_status(tickets, "T001", "resolved")
        with self.assertRaises(WorkflowError):
            assign_ticket(tickets, "T001", "Alex")
        with self.assertRaises(WorkflowError):
            change_status(tickets, "T001", "open")
        self.assertEqual(reopen_ticket(tickets, "T001")["status"], "open")
        self.assertEqual(assign_ticket(tickets, "T001", "Alex")["assigned_to"], "Alex")


class TestQueueAndReports(unittest.TestCase):
    def test_queue_order_with_numeric_tie_break(self):
        tickets = []
        make(tickets, "low")                          # T001 low
        make(tickets, "crit", "high", "12")           # T002 critical
        make(tickets, "high-a", "high", "1")          # T003 high
        make(tickets, "high-b", "high", "2")          # T004 high
        done = make(tickets, "done", "high", "50")    # T005 critical but resolved
        done["status"] = "resolved"
        self.assertEqual([t["id"] for t in work_queue(tickets)],
                         ["T002", "T003", "T004", "T001"])

    def test_queue_uses_numeric_not_text_id_order(self):
        tickets = []
        for number in (999, 1000):
            ticket = make(tickets)
            ticket["id"] = f"T{number}"
        self.assertEqual([t["id"] for t in work_queue(tickets)], ["T999", "T1000"])

    def test_empty_report_is_all_zero(self):
        report = build_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(set(report["by_status"].values()), {0})
        self.assertEqual(set(report["by_priority"].values()), {0})
        self.assertEqual(len(report["by_status"]), 3)
        self.assertEqual(len(report["by_priority"]), 4)

    def test_report_counts(self):
        tickets = []
        make(tickets, "a", "high", "10")
        make(tickets, "b")
        report = build_report(tickets)
        self.assertEqual(report["by_priority"]["critical"], 1)
        self.assertEqual(report["by_status"]["open"], 2)


if __name__ == "__main__":
    unittest.main()
