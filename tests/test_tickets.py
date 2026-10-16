"""ENGINEER A tests: input validation, priority rules, and follow-up notes."""
import copy
import unittest

from campusflow.tickets import (
    ValidationError,
    add_note,
    calculate_priority,
    create_ticket,
    format_ticket_notes,
    get_ticket_notes,
    next_note_id,
    next_ticket_id,
)
from campusflow.workflow import (
    WorkflowError,
    assign_ticket,
    change_status,
    reopen_ticket,
)


class TestValidation(unittest.TestCase):
    def test_blank_title_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "   ", "Network", "low", "1")

    def test_category_is_normalized_and_invalid_rejected(self):
        tickets = []
        ticket = create_ticket(tickets, "Wi-Fi down", "  nEtWoRk ", "HIGH", "2")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        with self.assertRaises(ValidationError):
            create_ticket(tickets, "x", "Plumbing", "low", "1")

    def test_affected_users_must_be_positive_integer(self):
        bad_values = ["0", "-3", "abc", "2.5", "", " ", 0, -5, 2.5, True, False, None]
        for bad in bad_values:
            with self.subTest(value=bad), self.assertRaises(ValidationError):
                create_ticket([], "Laptop", "Hardware", "low", bad)

    def test_failed_create_does_not_store_ticket(self):
        tickets = []
        with self.assertRaises(ValidationError):
            create_ticket(tickets, "ok", "Other", "bad-urgency", "1")
        self.assertEqual(tickets, [])

    def test_unassigned_open_to_in_progress_leaves_data_unchanged(self):
        tickets = []
        create_ticket(tickets, "Projector broken", "Hardware", "medium", 4)
        snapshot = copy.deepcopy(tickets)
        with self.assertRaises(WorkflowError):
            change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets, snapshot)

    def test_resolved_ticket_assignment_mutation_rejected_unchanged(self):
        tickets = []
        create_ticket(tickets, "VPN issue", "Network", "low", 1)
        assign_ticket(tickets, "T001", "Alice")
        change_status(tickets, "T001", "in_progress")
        change_status(tickets, "T001", "resolved")
        snapshot = copy.deepcopy(tickets)
        with self.assertRaises(WorkflowError):
            assign_ticket(tickets, "T001", "Bob")
        self.assertEqual(tickets, snapshot)

    def test_malformed_ticket_id_raises_validation_error(self):
        # Covers Engineer B's review: strict validation on ticket_number
        from campusflow.tickets import ticket_number
        for bad_id in ["ABC", "T-5", "T000", "", None, 123]:
            with self.subTest(bad_id=bad_id), self.assertRaises(ValidationError):
                ticket_number(bad_id)

class TestPriority(unittest.TestCase):
    def test_exact_rules(self):
        cases = [
            ("high", 10, "critical"),
            ("high", 9, "high"),
            ("low", 10, "high"),
            ("medium", 1, "medium"),
            ("low", 3, "medium"),
            ("low", 2, "low"),
        ]
        for urgency, users, expected in cases:
            with self.subTest(urgency=urgency, users=users):
                self.assertEqual(calculate_priority(urgency, users), expected)

    def test_ids_are_sequential_and_new_ticket_defaults(self):
        tickets = []
        first = create_ticket(tickets, "A", "Other", "low", "1")
        second = create_ticket(tickets, "B", "Other", "low", "1")
        self.assertEqual((first["id"], second["id"]), ("T001", "T002"))
        self.assertEqual((first["status"], first["assigned_to"]), ("open", None))
        self.assertEqual(first["notes"], [])
        self.assertEqual(next_ticket_id(tickets), "T003")


class TestFollowUpNotes(unittest.TestCase):
    def test_valid_note_added_and_note_id_sequence(self):
        tickets = []
        t = create_ticket(tickets, "Wi-Fi router", "Network", "high", 12)
        n1 = add_note(tickets, "T001", "  Mentor A ", "  Router reboot attempted  ")
        n2 = add_note(tickets, "T001", "Mentor B", "Investigating switch ports")
        self.assertEqual(n1, {"note_id": "N001", "author": "Mentor A", "message": "Router reboot attempted"})
        self.assertEqual(n2["note_id"], "N002")
        self.assertEqual(len(get_ticket_notes(tickets, "T001")), 2)
        self.assertEqual(next_note_id(t), "N003")
        self.assertIn("[N001] Mentor A: Router reboot attempted", format_ticket_notes(tickets, "T001"))

    def test_rejected_note_does_not_consume_id_or_mutate_ticket(self):
        tickets = []
        create_ticket(tickets, "Switch down", "Network", "medium", 5)
        add_note(tickets, "T001", "Mentor A", "Initial inspection complete")
        snapshot = copy.deepcopy(tickets)

        invalid_inputs = [
            ("", "Valid length message"),
            ("   ", "Valid length message"),
            ("Mentor A", ""),
            ("Mentor A", "abcd"),
            ("Mentor A", "   abcd   "),
            ("Mentor A", "x" * 301),
        ]
        for bad_author, bad_msg in invalid_inputs:
            with self.subTest(author=bad_author, msg_len=len(bad_msg)):
                with self.assertRaises(ValidationError):
                    add_note(tickets, "T001", bad_author, bad_msg)
                self.assertEqual(tickets, snapshot)

        next_valid = add_note(tickets, "T001", "Mentor B", "Replaced patch cable")
        self.assertEqual(next_valid["note_id"], "N002")

    def test_note_rejected_on_resolved_ticket_and_accepted_after_reopen(self):
        tickets = []
        create_ticket(tickets, "Lab PC freezes", "Hardware", "low", 2)
        add_note(tickets, "T001", "Tech 1", "Ran memory diagnostics")
        assign_ticket(tickets, "T001", "Tech 1")
        change_status(tickets, "T001", "in_progress")
        add_note(tickets, "T001", "Tech 1", "Swapped faulty RAM stick")
        change_status(tickets, "T001", "resolved")

        snapshot = copy.deepcopy(tickets)
        with self.assertRaises(ValidationError):
            add_note(tickets, "T001", "Tech 1", "Trying to add note while resolved")
        self.assertEqual(tickets, snapshot)

        reopen_ticket(tickets, "T001")
        n3 = add_note(tickets, "T001", "Tech 2", "Issue recurred after reboot")
        self.assertEqual(n3["note_id"], "N003")
        self.assertEqual(len(get_ticket_notes(tickets, "T001")), 3)


if __name__ == "__main__":
    unittest.main()