from __future__ import annotations


SCORE_FIELDS = [
    "Question Importance",
    "Theoretical Tension",
    "Setting Quality",
    "Identification Credibility",
    "Construct Validity",
    "Mechanism Testability",
    "Contribution",
    "Feasibility",
]


def decision_for_scores(scores: dict[str, int]) -> str:
    total = sum(int(scores.get(field, 0)) for field in SCORE_FIELDS)
    if (
        int(scores.get("Identification Credibility", 0)) < 3
        or int(scores.get("Contribution", 0)) < 3
        or int(scores.get("Feasibility", 0)) < 3
    ):
        return "Revise" if total >= 28 else "Hold" if total >= 22 else "Archive"
    if total >= 34:
        return "Promote"
    if total >= 28:
        return "Revise"
    if total >= 22:
        return "Hold"
    return "Archive"


def total_score(scores: dict[str, int]) -> int:
    return sum(int(scores.get(field, 0)) for field in SCORE_FIELDS)
