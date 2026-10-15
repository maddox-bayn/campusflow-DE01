"""Interactive CLI Engineering Understanding Check (Section 05).

OWNER: Engineer B (branch feat/22-search-and-insights)
"""
from .tickets import ValidationError

VALID_CHOICES = ("A", "B", "C", "D")

QUESTION_BANK = (
    {
        "id": "Q1",
        "prompt": "Q1. Ticket T001 is open and unassigned. A user tries to move it to in_progress.",
        "options": {
            "A": "Accept",
            "B": "Reject and preserve all data",
            "C": "Resolve it automatically",
            "D": "Remove ticket",
        },
        "answer": "B",
    },
    {
        "id": "Q2",
        "prompt": "Q2. The app has zero tickets. What should resolution percentage display?",
        "options": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "answer": "C",
    },
    {
        "id": "Q3",
        "prompt": "Q3. Filter title='wifi', category='Network', status='open'. Which records should match?",
        "options": {
            "A": "Any record matching one filter",
            "B": "Only records matching all supplied filters",
            "C": "All network records",
            "D": "All open records",
        },
        "answer": "B",
    },
    {
        "id": "Q4",
        "prompt": "Q4. A resolved ticket receives 'Add note'. What should happen?",
        "options": {
            "A": "Append anyway",
            "B": "Delete old notes",
            "C": "Reject until reopened",
            "D": "Change status silently",
        },
        "answer": "C",
    },
    {
        "id": "Q5",
        "prompt": "Q5. The JSON file includes two tickets with the same ID. What should load do?",
        "options": {
            "A": "Keep both",
            "B": "Replace memory with duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename IDs silently",
        },
        "answer": "C",
    },
    {
        "id": "Q6",
        "prompt": "Q6. A PR changes validation but has no negative-case tests. Best review action?",
        "options": {
            "A": "Approve because it runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "answer": "B",
    },
)


def validate_choice(raw_choice):
    """Normalize and validate an A/B/C/D multiple-choice answer."""
    choice = (raw_choice or "").strip().upper()
    if choice not in VALID_CHOICES:
        raise ValidationError("Invalid choice. Please enter A, B, C, or D.")
    return choice


def score_answers(submitted_answers, questions=QUESTION_BANK):
    """Pure scoring function: validates choices and computes total score (0 to len(questions))."""
    if len(submitted_answers) != len(questions):
        raise ValidationError(f"Expected {len(questions)} answers, got {len(submitted_answers)}.")

    score = 0
    results = []
    for raw_ans, q in zip(submitted_answers, questions):
        choice = validate_choice(raw_ans)
        is_correct = choice == q["answer"]
        if is_correct:
            score += 1
        results.append({
            "id": q["id"],
            "submitted": choice,
            "expected": q["answer"],
            "correct": is_correct,
        })

    return {
        "score": score,
        "total": len(questions),
        "details": results,
    }


def run_understanding_check(input_fn=input, print_fn=print):
    """Interactive CLI runner with retry loops and 2 reflection explanations."""
    print_fn("\n=== ENGINEERING UNDERSTANDING CHECK ===")
    submitted = []

    for q in QUESTION_BANK:
        print_fn(f"\n{q['prompt']}")
        for letter, text in q["options"].items():
            print_fn(f"  {letter}) {text}")
        while True:
            try:
                choice = validate_choice(input_fn("Your answer (A/B/C/D): "))
                submitted.append(choice)
                break
            except ValidationError as err:
                print_fn(f"[Error] {err}")

    outcome = score_answers(submitted)
    print_fn(f"\nFinal Score: {outcome['score']} / {outcome['total']}")

    explanations = {}
    for q_id in ("Q1", "Q5"):
        while True:
            text = (input_fn(f"Briefly explain WHY your answer for {q_id} is important in CampusFlow: ") or "").strip()
            if text:
                explanations[q_id] = text
                break
            print_fn("[Error] Explanation cannot be blank.")

    print_fn("\nRecorded Explanations for Mentor Discussion:")
    for q_id, exp in explanations.items():
        print_fn(f"  - {q_id}: {exp}")

    return outcome, explanations