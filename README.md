# CampusFlow

A Python command-line ticket manager for Learn2Earn campus support requests.
It records problems, calculates priority, assigns responsibility and tracks progress.
Standard library only (Python 3.8+).

## Run

```bash
python main.py
```

Tickets are saved to `tickets.json` in the folder you run it from and reloaded on startup.

## Test

```bash
python -m unittest discover -s tests -v
```

## Features

| Feature | Where | Owner |
|---|---|---|
| F1 Create (validation, priority, unique ID) | `campusflow/tickets.py` | Engineer A |
| F2 List / View | `campusflow/tickets.py`, `main.py` | Engineer A |
| F3 Assign | `campusflow/workflow.py` | Engineer B |
| F4 Workflow (open -> in_progress -> resolved, reopen) | `campusflow/workflow.py` | Engineer B |
| F5 Work queue | `campusflow/reports.py` | Engineer B |
| F6 Reports | `campusflow/reports.py` | Engineer B |
| F7 Persistence | `campusflow/storage.py` | Engineer A (wrapper), shared contract |

## Ownership

- **Engineer A** (`feat/1-ticket-core-management`): `main.py` loop, `tickets.py`, `storage.py`, `tests/test_tickets.py`, `tests/test_storage.py`
- **Engineer B** (`feat/2-ticket-operations-reporting`): `workflow.py`, `reports.py`, `tests/test_workflow.py`, and the F3-F6 handlers in `main.py`

See `docs/design-decisions.md` for the agreed interfaces and merge workflow.