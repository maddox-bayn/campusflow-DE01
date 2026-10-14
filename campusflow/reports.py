"""Work queue and summary reports (F5 WORK QUEUE, F6 REPORTS, Requirement D).

OWNER: Engineer B (branch feat/22-search-and-insights)
"""
from .tickets import CATEGORIES, ticket_number
from .workflow import STATUSES

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def work_queue(tickets):
    """Original Open Work Queue: ONLY 'open' tickets, ordered critical -> low, then numeric ID."""
    pending = [t for t in tickets if t["status"] == "open"]
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
    """Zero-safe counts: every status, priority, category, and resolution metric is present."""
    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITY_ORDER}
    by_category = {category: 0 for category in CATEGORIES}

    for t in tickets:
        by_status[t["status"]] += 1
        by_priority[t["priority"]] += 1
        by_category[t["category"]] += 1

    total = len(tickets)
    resolved_count = by_status["resolved"]
    unresolved_count = by_status["open"] + by_status["in_progress"]
    resolution_percentage = (resolved_count / total * 100.0) if total > 0 else 0.0

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
        "unresolved": unresolved_count,
        "resolved": resolved_count,
        "resolution_percentage": round(resolution_percentage, 2),
    }


def format_report(tickets):
    report = build_report(tickets)
    lines = [
        f"Total tickets:         {report['total']}",
        f"Unresolved tickets:    {report['unresolved']}",
        f"Resolved tickets:      {report['resolved']}",
        f"Resolution percentage: {report['resolution_percentage']:.1f}%",
        "",
        "By status:",
    ]
    lines += [f"  {name:<12} {count}" for name, count in report["by_status"].items()]
    lines += ["", "By priority:"]
    lines += [f"  {name:<12} {count}" for name, count in report["by_priority"].items()]
    lines += ["", "By category:"]
    lines += [f"  {name:<12} {count}" for name, count in report["by_category"].items()]
    return "\n".join(lines)