"""Work queue and summary reports (F5 WORK QUEUE, F6 REPORTS).

OWNER: Engineer B  (branch feat/2-ticket-operations-reporting)
"""
from .tickets import ticket_number
from .workflow import STATUSES

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def work_queue(tickets):
    """Unresolved tickets: critical -> low, ties broken by earlier numeric ID."""
    pending = [t for t in tickets if t["status"] != "resolved"]
    pending.sort(key=lambda t: (PRIORITY_ORDER[t["priority"]], ticket_number(t["id"])))
    return pending


def format_work_queue(tickets):
    queue = work_queue(tickets)
    if not queue:
        return "The work queue is empty."
    lines = [f"{'#':<3} {'ID':<6} {'Priority':<9} {'Status':<12} {'Assigned':<12} Title"]
    for position, t in enumerate(queue, start=1):
        lines.append(
            f"{position:<3} {t['id']:<6} {t['priority']:<9} {t['status']:<12} "
            f"{(t['assigned_to'] or 'unassigned'):<12} {t['title']}"
        )
    return "\n".join(lines)


def build_report(tickets):
    """Zero-safe counts: every status and priority is always present."""
    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITY_ORDER}
    for t in tickets:
        by_status[t["status"]] += 1
        by_priority[t["priority"]] += 1
    return {"total": len(tickets), "by_status": by_status, "by_priority": by_priority}


def format_report(tickets):
    report = build_report(tickets)
    lines = [f"Total tickets: {report['total']}", "", "By status:"]
    lines += [f"  {name:<12} {count}" for name, count in report["by_status"].items()]
    lines += ["", "By priority:"]
    lines += [f"  {name:<12} {count}" for name, count in report["by_priority"].items()]
    return "\n".join(lines)