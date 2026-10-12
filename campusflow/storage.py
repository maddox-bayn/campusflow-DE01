"""JSON persistence (F7).

OWNER: Engineer A writes the wrapper (stub pushed first); both engineers rely on
the contract below and review it.

Contract:
  * missing file       -> fresh start (empty list)
  * malformed JSON     -> StorageError with a clear message; the file is NOT touched
  * saves are atomic   -> write a temp file, then replace, so a crash can't wipe data
"""
import json
import os
import tempfile

REQUIRED_KEYS = {
    "id", "title", "category", "urgency",
    "affected_users", "priority", "status", "assigned_to",
}


class StorageError(Exception):
    """Raised when the data file cannot be read safely."""


def load_tickets(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as err:
        raise StorageError(
            f"'{path}' contains invalid JSON ({err}). Your data has NOT been changed. "
            "Fix or move the file, then restart."
        ) from err
    except OSError as err:
        raise StorageError(f"Could not read '{path}': {err}") from err

    if not isinstance(data, list) or not all(
        isinstance(t, dict) and REQUIRED_KEYS <= t.keys() for t in data
    ):
        raise StorageError(
            f"'{path}' is not a valid ticket file. Your data has NOT been changed."
        )
    return data


def save_tickets(tickets, path):
    directory = os.path.dirname(os.path.abspath(path))
    try:
        fd, temp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle, indent=4)
        os.replace(temp_path, path)
    except OSError as err:
        raise StorageError(f"Could not save to '{path}': {err}") from err