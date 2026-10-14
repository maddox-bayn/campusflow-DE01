# Baseline Diagnostic Check

## 1. Test Command & Environment
- **Command:** `python3 -m unittest discover -s tests -v`
- **Result:** Ran 22 tests in 0.002s — `OK` (All passing).
- **Observation:** Noticeable test duplication between `test_storage` and `test_workflow` (both contain `TestAssignment`, `TestQueueAndReports`, and `TestTransitions`).

## 2. Manual CLI Smoke Test (3 Scenarios)
1. **Ticket Creation:** Created ticket with title `"Wi-Fi disconnects in Lab 2"`, category `"Network"`, urgency `"high"`, affected users `12` $\rightarrow$ Correctly assigned priority `critical`.
2. **Assignment Gate:** Attempted to transition unassigned ticket `T001` directly from `open` to `in_progress` $\rightarrow$ System rejected transition as expected.
3. **Queue Sorting:** Checked Open Work Queue order $\rightarrow$ Evaluated priority hierarchy `critical > high > medium > low` with numeric ID tie-breaking.

## 3. Sprint Scope & Audit Focus
- **Current State:** Core priority rules, basic status lifecycle, and simple reports are functional.
- **Sprint Target:** Upgrade to CampusFlow Next:
  - Add structured follow-up notes schema (`notes: []` with `note_id`, `author`, `message`).
  - Implement read-only multi-filter search (casefold substring match + `AND` logic).
  - Harden JSON loading with validate-before-replace semantics (zero data loss on corrupt/duplicate-ID files).
  - Implement CLI Understanding Check with separate scoring logic.