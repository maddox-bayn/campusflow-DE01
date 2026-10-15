"""ENGINEER A tests: safe JSON persistence, validation, and ID continuity (F7)."""
import copy
import json
import os
import tempfile
import unittest

from campusflow.storage import (
    StorageError,
    load_tickets,
    save_tickets,
)
from campusflow.tickets import (
    add_note,
    create_ticket,
    next_note_id,
    next_ticket_id,
)


class TestStorageSafety(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.json_path = os.path.join(self.temp_dir.name, "tickets.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_list(self):
        missing = os.path.join(self.temp_dir.name, "does_not_exist.json")
        self.assertEqual(load_tickets(missing), [])

    def test_save_and_load_preserves_notes_and_next_ids(self):
        tickets = []
        create_ticket(tickets, "Router down", "Network", "high", 15)
        create_ticket(tickets, "Mouse broken", "Hardware", "low", 1)
        add_note(tickets, "T001", "Mentor A", "Checked power supply")
        add_note(tickets, "T001", "Mentor B", "Escalated to ISP team")

        save_tickets(tickets, self.json_path)
        reloaded = load_tickets(self.json_path)

        self.assertEqual(reloaded, tickets)
        self.assertEqual(next_ticket_id(reloaded), "T003")
        self.assertEqual(next_note_id(reloaded[0]), "N003")
        self.assertEqual(next_note_id(reloaded[1]), "N001")

    def test_corrupt_json_rejected_without_state_loss(self):
        memory = []
        create_ticket(memory, "Valid in-memory ticket", "Software", "medium", 4)
        snapshot = copy.deepcopy(memory)

        with open(self.json_path, "w", encoding="utf-8") as f:
            f.write("{corrupted json: [unclosed")

        with self.assertRaises(StorageError):
            memory[:] = load_tickets(self.json_path)
        self.assertEqual(memory, snapshot)

    def test_duplicate_ticket_ids_rejected_without_state_loss(self):
        memory = []
        create_ticket(memory, "Original memory", "Network", "low", 2)
        snapshot = copy.deepcopy(memory)

        bad_data = [
            {
                "id": "T001",
                "title": "First ticket",
                "category": "Network",
                "urgency": "low",
                "affected_users": 1,
                "priority": "low",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            },
            {
                "id": "T001",
                "title": "Second ticket with same ID",
                "category": "Hardware",
                "urgency": "low",
                "affected_users": 1,
                "priority": "low",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            },
        ]
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(bad_data, f)

        with self.assertRaises(StorageError):
            memory[:] = load_tickets(self.json_path)
        self.assertEqual(memory, snapshot)


if __name__ == "__main__":
    unittest.main()