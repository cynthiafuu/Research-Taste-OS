from research_taste_os.utils.scoring import decision_for_scores, total_score


def test_promote_when_score_and_hard_rules_pass():
    scores = {
        "Question Importance": 5,
        "Theoretical Tension": 4,
        "Setting Quality": 4,
        "Identification Credibility": 4,
        "Construct Validity": 4,
        "Mechanism Testability": 4,
        "Contribution": 5,
        "Feasibility": 4,
    }
    assert total_score(scores) == 34
    assert decision_for_scores(scores) == "Promote"


def test_low_identification_blocks_promotion():
    scores = {
        "Question Importance": 5,
        "Theoretical Tension": 5,
        "Setting Quality": 5,
        "Identification Credibility": 2,
        "Construct Validity": 5,
        "Mechanism Testability": 5,
        "Contribution": 5,
        "Feasibility": 5,
    }
    assert total_score(scores) == 37
    assert decision_for_scores(scores) == "Revise"
