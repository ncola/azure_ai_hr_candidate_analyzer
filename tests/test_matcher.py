from processing.matcher import Matcher

def calculate_score(candidate):
    matched = len(candidate.get("matched_skills", []))
    missing = len(candidate.get("missing_skills", []))
    total = matched + missing
    return matched / total if total else 0


def test_matcher_returns_top_3():
    matcher = Matcher()
    result = matcher.match(MOCK_JOB_OFFER, MOCK_CVS)
    assert len(result["top_3"]) <= 3
 
def test_matcher_score_calculation():
    candidate = {
    "matched_skills": ["Python", "SQL"],
    "missing_skills": ["Java"]
    }
    score = calculate_score(candidate)
    assert score == 2/3