"""Shared persistence tests (F7) - written by A, reviewed by B."""
import os
import tempfile
import unittest

from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket, next_ticket_id


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "tickets.json")

    def tearDown(self):
        self.dir.cleanup()

    def test_missing_file_gives_fresh_start(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_malformed_json_errors_and_keeps_file(self):
        with open(self.path, "w") as handle:
            handle.write("{ not valid json")
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        with open(self.path) as handle:
            self.assertEqual(handle.read(), "{ not valid json")

    def test_round_trip_and_ids_stay_unique_after_reload(self):
        tickets = []
        create_ticket(tickets, "A", "Other", "low", "1")
        create_ticket(tickets, "B", "Other", "low", "1")
        save_tickets(tickets, self.path)
        reloaded = load_tickets(self.path)
        self.assertEqual(reloaded, tickets)
        self.assertEqual(next_ticket_id(reloaded), "T003")

    def test_wrong_structure_rejected(self):
        with open(self.path, "w") as handle:
            handle.write('{"tickets": []}')
        with self.assertRaises(StorageError):
            load_tickets(self.path)


if __name__ == "__main__":
    unittest.main()