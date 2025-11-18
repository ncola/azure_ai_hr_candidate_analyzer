from streamlit_app import _compute_score


def test_compute_score_basic():
    candidate = {
        "matched_skills": ["Python", "SQL"],
        "missing_skills": ["Java"]
    }
    score = _compute_score(candidate)
    assert score == 2/3


def test_compute_score_no_missing():
    candidate = {
        "matched_skills": ["Python", "SQL"],
        "missing_skills": []
    }
    score = _compute_score(candidate)
    assert score == 1.0


def test_compute_score_no_skills():
    candidate = {
        "matched_skills": [],
        "missing_skills": []
    }
    score = _compute_score(candidate)
    assert score == 0.0


def test_compute_score_only_missing():
    candidate = {
        "matched_skills": [],
        "missing_skills": ["Python"]
    }
    score = _compute_score(candidate)
    assert score == 0.0