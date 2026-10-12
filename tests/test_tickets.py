"""ENGINEER A tests: input validation and priority rules (F1)."""
import unittest

from campusflow.tickets import (
    ValidationError, calculate_priority, create_ticket, next_ticket_id,
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
        for bad in ["0", "-3", "abc", "2.5", "", " "]:
            with self.subTest(value=bad), self.assertRaises(ValidationError):
                create_ticket([], "Laptop", "Hardware", "low", bad)

    def test_failed_create_does_not_store_ticket(self):
        tickets = []
        with self.assertRaises(ValidationError):
            create_ticket(tickets, "ok", "Other", "bad-urgency", "1")
        self.assertEqual(tickets, [])


class TestPriority(unittest.TestCase):
    def test_exact_rules(self):
        cases = [
            ("high", 10, "critical"), ("high", 9, "high"), ("low", 10, "high"),
            ("medium", 1, "medium"), ("low", 3, "medium"), ("low", 2, "low"),
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
        self.assertEqual(next_ticket_id(tickets), "T003")


if __name__ == "__main__":
    unittest.main()