# CampusFlow
# CampusFlow


1 | UNDERSTAND THE PRODUCT YOU ARE BUILDING
1.1 The real-world problem
Learn2Earn campus staff receive technical support requests: Wi-Fi outages, faulty laptops, broken development environments, and inaccessible platforms. Informal reports get lost. Build CampusFlow, a Python command-line ticket manager that records problems, prioritizes work, assigns responsibility, and tracks progress.
Think like engineers: Which inputs does the system need? What must it calculate? What could go wrong? What should be preserved after the program closes?
1.2 Ticket fields (required)
Each ticket stores: id, title, category, urgency, affected_users, priority, status, and assigned_to.
EXAMPLE (Python dictionary):
{
  "id": "T001",
  "title": "Campus Wi-Fi is down",
  "category": "Network",
  "urgency": "high",
  "affected_users": 15,
  "priority": "critical",
  "status": "open",
  "assigned_to": None
}
• Ticket IDs are unique and automatically generated (T001, T002, T003, …).
• Allowed categories: Network, Hardware, Software, Other.
• Allowed urgency levels: low, medium, high.
• Title must not be blank. affected_users must be a positive integer (not zero, a negative number, a decimal, or text).
• Accept and normalize valid case variations consistently; display useful errors for invalid input.
1.3 Calculate priority exactly as specified
Your function must check the following rules IN THIS ORDER and apply the first match:
RULE 1   high urgency AND 10 or more affected users  →  critical
RULE 2   high urgency OR 10 or more affected users    →  high
RULE 3   medium urgency OR 3 or more affected users   →  medium
RULE 4   all remaining valid tickets                  →  low
Important: This engine is ordinary Python business logic, not an AI model. You use AI to LEARN and BUILD, not as the priority engine itself.
1.4 Build these seven features
• F1 — CREATE: Collect ticket details, validate inputs, calculate priority, assign a unique ID and store the record.
• F2 — LIST / VIEW: Show all tickets and details for one chosen ticket.
• F3 — ASSIGN: Assign a ticket to a non-empty staff member name; reject unknown ticket IDs.
• F4 — WORKFLOW: Support open → in_progress → resolved. Do not move an unassigned ticket into in_progress. A resolved ticket may only be modified after an explicit reopen that sets it to open.
• F5 — WORK QUEUE: Show open, unresolved tickets in critical → high → medium → low order; break priority ties using the earlier numeric ticket ID.
• F6 — REPORTS: Show total tickets and breakdowns by status and priority; handle zero tickets correctly.
• F7 — PERSISTENCE: Save to JSON and reload on startup. Missing file should allow a fresh start; malformed JSON should produce a clear error rather than silently erase data. IDs must remain unique after reload.
Create a menu that keeps running until Exit. The interface can be text-only. Do not spend sprint time building a GUI or website.
