## Design Decision: Feature Branch Integration & Ownership

### 1. Context & Linked Issues
This section details how our concurrent Python feature branches collaborate to deliver the required 7-feature ticket management system before merging into `main`. 

*   **Feature Branch A:** `feat/1-ticket-core-management` (Resolves: F1 — CREATE, F2 — LIST / VIEW, F7 — PERSISTENCE)
*   **Feature Branch B:** `feat/2-ticket-operations-reporting` (Resolves: F3 — ASSIGN, F4 — WORKFLOW, F5 — WORK QUEUE, F6 — REPORTS)

### 2. Agreed Interfaces
Both branches operate inside a text-only, continuously looping CLI menu (`while True:`) running in a Python environment. To prevent merge conflicts and ensure data integrity, both branches adhere to the following shared contracts:

#### A. Central Data Schema (Python Dictionary Structure)
Tickets are stored as objects inside a centralized in-memory list and serialized into JSON format.
```python
{
    "id": str,                 # Unique ID auto-generated as "T001", "T002", etc.
    "title": str,              # Validated non-empty string
    "category": str,           # Restricted to normalized: "Network", "Hardware", "Software", "Other"
    "urgency": str,            # Restricted to normalized: "low", "medium", "high"
    "affected_users": int,     # Positive integer (> 0)
    "priority": str,           # Auto-calculated: "critical", "high", "medium", "low"
    "status": str,             # Restricted to: "open", "in_progress", "resolved"
    "assigned_to": str | None  # Staff name (non-empty string) or None if unassigned
}
```

#### B. Component Communication & Functional Constraints
*   **F1 Priority Calculation Contract (Engineer A):** Priority is calculated sequentially checking rules in this exact order:
    1.  `urgency == "high"` and `affected_users >= 10` \(\rightarrow\) `"critical"`
    2.  `urgency == "high"` or `affected_users >= 10` \(\rightarrow\) `"high"`
    3.  `urgency == "medium"` or `affected_users >= 3` \(\rightarrow\) `"medium"`
    4.  All remaining valid tickets \(\rightarrow\) `"low"`
*   **F4 Workflow & F3 Assignment Guard (Engineer B):** Transition rules are strictly checked before updating states. Transitioning to `"in_progress"` is rejected if `assigned_to` is `None`. Modifying a `"resolved"` ticket is blocked unless an explicit reopen command sets it back to `"open"`.
*   **F5 Sorting Key (Engineer B):** Sorting the work queue resolves priority ties stably using the sequential unique text ID string (`"T001"` < `"T002"`).
    ```python
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    open_unresolved = [t for t in tickets if t["status"] != "resolved"]
    open_unresolved.sort(key=lambda t: (priority_order[t["priority"]], t["id"]))
    ```
*   **F7 Persistence Contract (Both):** Handled via `tickets.json`. If `FileNotFoundError` is thrown, the application instantiates a fresh start (`[]`). If `json.JSONDecodeError` occurs, the app outputs an explicit error message instead of corrupting or wiping existing data.

### 3. Ownership Matrix
Post-merge ownership is established as follows to manage maintenance and track automated test suites:
*   **Engineer A Core Engine (`feat/1-ticket-core-management`):** 
    *   Governs the CLI loop framework, unique ID counter state, and strict user input validation (category normalization, blank title rejection, positive integer checking).
    *   Responsible for the F1 priority rule algorithm.
    *   **Test Suite:** Minimum of 4 automated tests verifying input validation edge cases and exact priority rule matches.
*   **Engineer B Operations Engine (`feat/2-ticket-operations-reporting`):**
    *   Governs ticket assignment validation (rejecting empty strings or unknown IDs) and F4 state transitions (reopening blocks/assignment guards).
    *   Responsible for the stable tie-breaking logic in F5 and zero-safe status aggregation summaries in F6.
    *   **Test Suite:** Minimum of 4 automated tests verifying transition restrictions, work queue order sorting, and empty dataset breakdowns.

### 4. Integration & Merge Workflow
To seamlessly deploy all 7 features under genuine peer-reviewed Pull Requests:
1.  **Interface Signature Freeze:** Both engineers sign off on the JSON dictionary model structure before beginning coding sprint.
2.  **Stubs Implementation:** Engineer A pushes the central shell including the persistence wrapper and placeholder hooks with Python `pass` statements (`assign_ticket()`, `process_workflow()`, `view_queue()`, `show_reports()`).
3.  **Merge Sequence:** 
    *   **Step 1:** Engineer A opens a PR for `feat/1-ticket-core-management`. Engineer B performs a code review, approves, and merges it into `main`.
    *   **Step 2:** Engineer B rebases `main` down into `feat/2-ticket-operations-reporting`.
    *   **Step 3:** Engineer B completes the functionality inside the placeholder interfaces and writes the remaining test assertions.
4.  **Definition of Done Verification:** Confirm at least 8 automated tests pass successfully on the shared branch, data input validation prevents memory corruption, and tickets accurately survive clean restarts.
