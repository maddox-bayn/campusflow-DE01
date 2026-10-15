# AI Learning Log

## Concepts to revisit
- Why logic functions raise exceptions and only `main.py` prints
- Why the queue sorts on the numeric ID instead of the ID string
- Why saves write a temp file first, then replace


## Learning Cycles & Engineering Reflections

### Cycle 1: Strict Input Validation & Type Safety
- **Challenge:** Handling edge cases where Python treats `True` as a valid integer (`isinstance(True, int)` evaluates to `True`) or where floats and negative numbers bypass basic string checks.
- **Insight:** Explicitly checking `isinstance(raw, bool)` and `isinstance(raw, float)` before checking integer ranges prevents silent data corruption.
- **Application:** Upgraded `parse_affected_users()` to rigorously reject booleans, floats, negative numbers, and zeros while safely parsing valid numeric strings from CLI inputs.

### Cycle 2: Atomic State & Validation-Before-Load Storage Safety
- **Challenge:** Preventing malformed JSON files or duplicate ticket IDs (`T001` appearing twice) from wiping out valid in-memory data during a reload.
- **Insight:** Implementing a two-phase validation pattern: load and validate the entire file into a temporary structure *first*, and only update the live in-memory list via slice assignment (`tickets[:] = fresh`) if 100% of records pass schema checks.
- **Application:** Built `validate_ticket_record()` and `reload_tickets_into()` in `campusflow/storage.py` to guarantee zero data loss on load errors.

### Cycle 3: Isolated State Mutation in Follow-Up Notes
- **Challenge:** Ensuring that failed validation on a new note (e.g., message too short) does not accidentally consume a sequential note ID (like skipping from `N001` to `N003`).
- **Insight:** All validation checks must happen *before* generating a new note ID or mutating the ticket dictionary.
- **Application:** Structured `add_note()` to validate author and message length first, ensuring rejected notes leave the ticket state completely untouched.

### Cycle 4: Comprehensive Automated Test Suite Design
- **Challenge:** Ensuring full coverage across standard requirements and potential regression bugs without breaking existing workflow tests.
- **Insight:** Utilizing `unittest.TestCase` with subtests (`self.subTest`) makes it easy to test arrays of invalid inputs cleanly while maintaining clear failure logs.
- **Application:** Wrote 10 new targeted unit tests in `test_tickets.py` and `test_storage.py`, bringing the total test suite to 23 passing tests.