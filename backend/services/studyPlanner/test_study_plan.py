# backend/services/studyPlanner/test_study_plan.py
"""
Unit tests for the StudyPlanGenerator module.
Run with: python -m pytest backend/services/studyPlanner/test_study_plan.py -v
No DB or network connection required for these tests.
"""

import pytest
from services.studyPlanner.StudyPlanGenerator import (
    compute_hour_budget,
    _validate_and_cap_daily_hours,
    compute_mastery_from_completion,
    redistribute_overdue_tasks,
)
from datetime import date, timedelta


# ============================================================
# 1. compute_hour_budget tests
# ============================================================

MOCK_TOPICS = [
    {"subject": "Physics", "topic": "Thermodynamics", "weightage": 2.0},
    {"subject": "Physics", "topic": "Optics", "weightage": 1.0},
    {"subject": "Chemistry", "topic": "Periodic Table", "weightage": 1.5},
    {"subject": "Chemistry", "topic": "Organic Basics", "weightage": 1.5},
    {"subject": "Maths", "topic": "Calculus", "weightage": 2.0},
]


def test_budget_sums_to_total_hours():
    """Total allocated hours should roughly equal daily_hours * days_remaining."""
    result = compute_hour_budget(MOCK_TOPICS, [], 4.0, 30)
    budget = result["budget"]
    total_allocated = sum(h for subj in budget.values() for h in subj.values())
    expected_total = 4.0 * 30
    # Allow ±20% tolerance due to rounding to 0.5h increments
    assert abs(total_allocated - expected_total) <= expected_total * 0.20


def test_weak_subject_boost():
    """Weak subjects should receive more hours than non-weak subjects of equal weight."""
    result_normal = compute_hour_budget(MOCK_TOPICS, [], 4.0, 30)
    result_weak = compute_hour_budget(MOCK_TOPICS, ["Maths"], 4.0, 30)

    normal_maths = sum(result_normal["budget"].get("Maths", {}).values())
    boosted_maths = sum(result_weak["budget"].get("Maths", {}).values())

    assert boosted_maths > normal_maths, "Weak subject should receive more hours after boost"


def test_past_exam_date_raises():
    """Negative days_remaining should raise ValueError."""
    with pytest.raises(ValueError, match="already passed"):
        compute_hour_budget(MOCK_TOPICS, [], 4.0, -5)


def test_zero_days_raises():
    """Zero days_remaining should raise ValueError."""
    with pytest.raises(ValueError, match="already passed"):
        compute_hour_budget(MOCK_TOPICS, [], 4.0, 0)


def test_empty_topics_raises():
    """Empty topic list should raise ValueError."""
    with pytest.raises(ValueError, match="No syllabus topics"):
        compute_hour_budget([], [], 4.0, 30)


def test_all_subjects_present_in_budget():
    """All subjects from input should appear in the output budget."""
    result = compute_hour_budget(MOCK_TOPICS, [], 4.0, 30)
    budget = result["budget"]
    assert "Physics" in budget
    assert "Chemistry" in budget
    assert "Maths" in budget


def test_no_warning_for_realistic_plan():
    """A realistic plan (sufficient hours) should have no warning."""
    result = compute_hour_budget(MOCK_TOPICS, [], 6.0, 60)
    assert result["warning"] is None


# ============================================================
# 2. _validate_and_cap_daily_hours tests
# ============================================================

def test_cap_prevents_overflow():
    """No day should exceed daily_available_hours after validation."""
    raw = [
        {
            "date": "2026-08-01",
            "tasks": [
                {"subject": "Physics", "topic": "A", "hours": 3.0},
                {"subject": "Maths", "topic": "B", "hours": 3.0},  # Would overflow 4h cap
            ]
        }
    ]
    validated = _validate_and_cap_daily_hours(raw, daily_available_hours=4.0)
    for day in validated:
        day_total = sum(float(t.get("hours", 0)) for t in day["tasks"])
        assert day_total <= 4.05, f"Day {day['date']} exceeded daily cap: {day_total}h"


def test_empty_days_passthrough():
    """Empty days list should return empty list."""
    result = _validate_and_cap_daily_hours([], 4.0)
    assert result == []


# ============================================================
# 3. compute_mastery_from_completion tests
# ============================================================

def test_mastery_strong():
    assert compute_mastery_from_completion(8, 10) == "strong"


def test_mastery_moderate():
    assert compute_mastery_from_completion(5, 10) == "moderate"


def test_mastery_weak():
    assert compute_mastery_from_completion(2, 10) == "weak"


def test_mastery_zero_total():
    """Zero total tasks should return moderate (safe default)."""
    assert compute_mastery_from_completion(0, 0) == "moderate"


# ============================================================
# 4. redistribute_overdue_tasks tests
# ============================================================

def test_redistribution_respects_cap():
    """Redistributed tasks should not exceed the daily cap."""
    today = date.today()
    remaining = [today + timedelta(days=i) for i in range(5)]
    existing_loads = {d.isoformat(): 2.0 for d in remaining}  # 2h already scheduled
    overdue = [
        {"estimated_hours": 1.5, "subject": "Physics", "topic": "Waves"},
        {"estimated_hours": 1.0, "subject": "Maths", "topic": "Calculus"},
    ]
    additions = redistribute_overdue_tasks(overdue, remaining, 4.0, existing_loads)
    # After adding to days that have 2h, no day should exceed 4h
    for day_str, tasks in additions.items():
        added_hours = sum(float(t.get("estimated_hours", 0)) for t in tasks)
        original_load = 2.0
        assert added_hours + original_load <= 4.05, f"Day {day_str} exceeded cap"
