"""JSON persistence (F7) and safe reload validation.

OWNER: Engineer A writes the wrapper; both engineers rely on the contract below.
"""
import json
import os
import tempfile

from .tickets import (
    CATEGORIES,
    URGENCIES,
    ValidationError,
    calculate_priority,
    validate_note_input,
)
from .workflow import STATUSES

REQUIRED_KEYS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
}
NOTE_KEYS = {"note_id", "author", "message"}


class StorageError(Exception):
    """Raised when the data file cannot be read or validated safely."""


def _is_valid_prefixed_id(raw_id, prefix):
    """Verify IDs like 'T001' or 'N001' have prefix + positive ASCII digits."""
    if not isinstance(raw_id, str) or len(raw_id) < 2 or not raw_id.startswith(prefix):
        return False
    digits = raw_id[1:]
    return digits.isascii() and digits.isdigit() and int(digits) > 0


def validate_ticket_record(record):
    """Validate a single decoded JSON ticket dict and return a normalized copy."""
    if not isinstance(record, dict) or not (REQUIRED_KEYS <= record.keys()):
        raise StorageError("Ticket record is missing required keys.")

    ticket_id = record["id"]
    if not _is_valid_prefixed_id(ticket_id, "T"):
        raise StorageError(f"Invalid ticket ID '{ticket_id}'.")

    title = record["title"]
    if not isinstance(title, str) or not title.strip():
        raise StorageError(f"Ticket {ticket_id} has an invalid or blank title.")

    category = record["category"]
    if category not in CATEGORIES:
        raise StorageError(f"Ticket {ticket_id} has invalid category '{category}'.")

    urgency = record["urgency"]
    if urgency not in URGENCIES:
        raise StorageError(f"Ticket {ticket_id} has invalid urgency '{urgency}'.")

    users = record["affected_users"]
    if type(users) is not int or users <= 0:
        raise StorageError(f"Ticket {ticket_id} has invalid affected_users '{users}'.")

    expected_priority = calculate_priority(urgency, users)
    if record["priority"] != expected_priority:
        raise StorageError(
            f"Ticket {ticket_id} priority '{record['priority']}' does not match "
            f"calculated priority '{expected_priority}'."
        )

    status = record["status"]
    if status not in STATUSES:
        raise StorageError(f"Ticket {ticket_id} has invalid status '{status}'.")

    assigned = record["assigned_to"]
    if assigned is not None and (not isinstance(assigned, str) or not assigned.strip()):
        raise StorageError(f"Ticket {ticket_id} has an invalid assigned_to value.")
    if status == "in_progress" and not assigned:
        raise StorageError(f"Ticket {ticket_id} cannot be in_progress without assigned_to.")

    raw_notes = record.get("notes", [])
    if not isinstance(raw_notes, list):
        raise StorageError(f"Ticket {ticket_id} field 'notes' must be a list.")

    seen_note_ids = set()
    validated_notes = []
    for note in raw_notes:
        if not isinstance(note, dict) or set(note.keys()) != NOTE_KEYS:
            raise StorageError(f"Ticket {ticket_id} contains a malformed note.")
        nid = note["note_id"]
        if not _is_valid_prefixed_id(nid, "N"):
            raise StorageError(f"Ticket {ticket_id} has invalid note_id '{nid}'.")
        if nid in seen_note_ids:
            raise StorageError(f"Ticket {ticket_id} has duplicate note_id '{nid}'.")
        seen_note_ids.add(nid)
        try:
            clean_author, clean_message = validate_note_input(note["author"], note["message"])
        except ValidationError as err:
            raise StorageError(f"Ticket {ticket_id} note {nid} is invalid: {err}") from err
        validated_notes.append(
            {"note_id": nid, "author": clean_author, "message": clean_message}
        )

    cleaned = dict(record)
    cleaned["title"] = title.strip()
    cleaned["assigned_to"] = assigned.strip() if isinstance(assigned, str) else None
    cleaned["notes"] = validated_notes
    return cleaned


def load_tickets(path):
    """Load and validate all tickets from JSON before returning.

    If any record is malformed or has duplicate IDs, raises StorageError.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as err:
        raise StorageError(
            f"'{path}' contains invalid JSON ({err}). Your data has NOT been changed."
        ) from err
    except OSError as err:
        raise StorageError(f"Could not read '{path}': {err}") from err

    if not isinstance(data, list):
        raise StorageError(f"'{path}' is not a valid ticket file.")

    validated = []
    seen_ids = set()
    for item in data:
        cleaned = validate_ticket_record(item)
        if cleaned["id"] in seen_ids:
            raise StorageError(
                f"Duplicate ticket ID '{cleaned['id']}' in '{path}'. "
                "Your data has NOT been changed."
            )
        seen_ids.add(cleaned["id"])
        validated.append(cleaned)

    return validated


def reload_tickets_into(tickets, path):
    """Safely replace in-memory `tickets` list only if `path` loads with zero errors."""
    fresh = load_tickets(path)
    tickets[:] = fresh
    return tickets


def save_tickets(tickets, path):
    directory = os.path.dirname(os.path.abspath(path))
    try:
        fd, temp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle, indent=4)
        os.replace(temp_path, path)
    except OSError as err:
        raise StorageError(f"Could not save to '{path}': {err}") from err