# backend/services/studyPlanner/StudyPlanGenerator.py

import os
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from openai import OpenAI

from services.studyPlanner.PromptsDict import STUDY_PLAN_SEQUENCING_PROMPT

# OpenAI client
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# ============================================================
# 1. PURE COMPUTATION — No DB, No LLM. Fully unit-testable.
# ============================================================

def compute_hour_budget(
    syllabus_topics: List[Dict],   # List of {"subject": str, "topic": str, "weightage": float}
    topics_already_done: List[str],
    weak_subjects: List[str],
    daily_hours: float,
    days_remaining: int,
    days_per_week: int = 7,
) -> Dict[str, Any]:
    """
    Computes hour allocation per topic based on weightage priority.
    - Excludes topics marked 'already done'.
    - Calculates available study days based on days_per_week available.
    - Conducts a feasibility check: fits highest-weightage topics within available hours.
    - Returns: {"budget": {subj: {topic: hours}}, "excluded_topics": [...], "warning": str}
    """
    if days_remaining <= 0:
        raise ValueError("Exam date must be in the future.")

    # 1. Available time budget
    effective_days_per_week = max(1, min(7, days_per_week))
    actual_study_days = max(1, round(days_remaining * (effective_days_per_week / 7.0)))
    total_available_hours = daily_hours * actual_study_days

    # 2. Exclude topics marked "already done"
    done_set = set()
    for t in (topics_already_done or []):
        t_clean = t.strip()
        done_set.add(t_clean)
        done_set.add(t_clean.split('\n')[0].strip())

    remaining_syllabus = []
    for item in syllabus_topics:
        t_full = item["topic"].strip()
        t_first = t_full.split('\n')[0].strip()
        if t_full not in done_set and t_first not in done_set:
            remaining_syllabus.append(item)

    if not remaining_syllabus:
        raise ValueError("All syllabus topics are marked as done! No remaining topics to plan.")

    # 3. Group by subject & sort by weightage (highest weightage first)
    by_subject: Dict[str, List[Dict]] = {}
    for item in remaining_syllabus:
        subj = item["subject"]
        if subj not in by_subject:
            by_subject[subj] = []
        by_subject[subj].append(item)

    for subj in by_subject:
        by_subject[subj].sort(key=lambda x: float(x.get("weightage", 1.0)), reverse=True)

    # 4. Interleave topics across subjects for diversity (Physics, Chemistry, Maths)
    interleaved = []
    subjs = list(by_subject.keys())
    indices = {s: 0 for s in subjs}

    while any(indices[s] < len(by_subject[s]) for s in subjs):
        for s in subjs:
            if indices[s] < len(by_subject[s]):
                interleaved.append(by_subject[s][indices[s]])
                indices[s] += 1

    # 5. Allocate hours to topics within total_available_hours budget
    hour_budget: Dict[str, Dict[str, float]] = {s: {} for s in subjs}
    excluded_topics: List[Dict[str, str]] = []
    remaining_hours = total_available_hours

    for item in interleaved:
        subj = item["subject"]
        topic = item["topic"]
        weight = float(item.get("weightage", 1.0))

        # Base hours needed per topic (1.5h to 4h based on weightage share)
        req_hours = round(max(1.5, min(4.0, (weight / 0.03) * 2.5)) * 2) / 2
        if subj in weak_subjects:
            req_hours = round((req_hours * 1.25) * 2) / 2

        if remaining_hours >= req_hours:
            hour_budget[subj][topic] = req_hours
            remaining_hours -= req_hours
        else:
            excluded_topics.append({
                "subject": subj,
                "topic": topic,
                "reason": f"Skipped due to limited time budget ({total_available_hours:.1f} total hours available)"
            })

    # Clean up empty subjects
    hour_budget = {s: t_dict for s, t_dict in hour_budget.items() if t_dict}

    warning_msg = None
    if excluded_topics:
        warning_msg = (
            f"{len(excluded_topics)} lower-priority topics were skipped due to limited time budget. "
            "Consider increasing daily study hours or days per week to cover the full syllabus."
        )

    return {
        "budget": hour_budget,
        "excluded_topics": excluded_topics,
        "warning": warning_msg
    }


# ============================================================
# 2. PROMPT BUILDING
# ============================================================

def build_llm_sequencing_prompt(
    hour_budget_dict: Dict[str, Dict[str, float]],
    start_date: date,
    target_exam_date: date,
    days_remaining: int,
    daily_available_hours: float,
) -> str:
    """Formats the fixed hour budget into the sequencing prompt for OpenAI, interleaving topics across subjects."""
    by_subj = {subj: list(topics.items()) for subj, topics in hour_budget_dict.items()}
    subjs = list(by_subj.keys())
    indices = {s: 0 for s in subjs}
    
    budget_list = []
    while any(indices[s] < len(by_subj[s]) for s in subjs):
        for s in subjs:
            if indices[s] < len(by_subj[s]):
                topic, hours = by_subj[s][indices[s]]
                budget_list.append({
                    "subject": s,
                    "topic": topic,
                    "hours": hours
                })
                indices[s] += 1

    return STUDY_PLAN_SEQUENCING_PROMPT.format(
        daily_available_hours=daily_available_hours,
        hour_budget_json=json.dumps(budget_list, indent=2),
        start_date=start_date.isoformat(),
        exam_date=target_exam_date.isoformat(),
        days_remaining=days_remaining,
    )


# ============================================================
# 3. LLM CALL + JSON PARSING (with 1 retry)
# ============================================================

def _call_openai_and_parse(prompt: str, strict: bool = False) -> List[Dict]:
    """
    Calls GPT-4o with the sequencing prompt.
    Returns the parsed list of day dicts: [{"date": ..., "tasks": [...]}]
    Raises RuntimeError on JSON parse failure.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a JSON-only output API. You NEVER include markdown fences, "
                "explanations, or any text outside the JSON object."
                + (" Return ONLY valid JSON. Nothing else." if strict else "")
            ),
        },
        {"role": "user", "content": prompt},
    ]

    response = _client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
    )
    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        parsed = json.loads(raw)
        if "days" not in parsed:
            raise ValueError("Missing 'days' key in LLM response")
        return parsed["days"]
    except (json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Failed to parse LLM JSON output: {e}\nRaw output: {raw[:500]}")


def _generate_schedule_from_llm(
    hour_budget: Dict[str, Dict[str, float]],
    start_date: date,
    target_exam_date: date,
    days_remaining: int,
    daily_available_hours: float,
) -> List[Dict]:
    """Calls LLM to sequence the schedule. Retries once on parse failure."""
    prompt = build_llm_sequencing_prompt(
        hour_budget, start_date, target_exam_date, days_remaining, daily_available_hours
    )
    try:
        return _call_openai_and_parse(prompt, strict=False)
    except RuntimeError:
        # Retry once with stricter instruction
        try:
            return _call_openai_and_parse(prompt, strict=True)
        except RuntimeError as e:
            raise RuntimeError(
                f"Study plan generation failed after 2 attempts. Please try again. Details: {e}"
            )


# ============================================================
# 4. POST-GENERATION VALIDATION
# ============================================================

def _validate_and_cap_daily_hours(
    days: List[Dict], daily_available_hours: float
) -> List[Dict]:
    """
    Ensures no single day exceeds daily_available_hours.
    Splits overflow into the next day rather than silently dropping tasks.
    """
    validated = []
    overflow_tasks = []

    for day_entry in days:
        tasks = overflow_tasks + day_entry.get("tasks", [])
        overflow_tasks = []
        day_total = 0.0
        accepted = []

        for task in tasks:
            task_hours = float(task.get("hours", 0))
            if day_total + task_hours <= daily_available_hours + 0.01:  # 0.01 float tolerance
                accepted.append(task)
                day_total += task_hours
            else:
                overflow_tasks.append(task)

        validated.append({"date": day_entry["date"], "tasks": accepted})

    # Append any remaining overflow tasks to last day(s)
    if overflow_tasks:
        for task in overflow_tasks:
            if validated:
                validated[-1]["tasks"].append(task)

    return validated


# ============================================================
# 5. ADAPTIVE REGENERATION (rule-based, no LLM in common case)
# ============================================================

def redistribute_overdue_tasks(
    overdue_tasks: List[Dict],
    remaining_days: List[date],
    daily_available_hours: float,
    existing_day_loads: Dict[str, float],  # {date_str: current_hours}
) -> Dict[str, List[Dict]]:
    """
    Spreads overdue tasks proportionally across remaining days.
    Returns: {date_str: [new_tasks_to_add]}
    """
    additions: Dict[str, List[Dict]] = {d.isoformat(): [] for d in remaining_days}

    for task in overdue_tasks:
        # Find the day with the least current load
        best_day = min(
            remaining_days,
            key=lambda d: existing_day_loads.get(d.isoformat(), 0.0),
        )
        best_day_str = best_day.isoformat()

        # Only add if it won't exceed daily cap
        current_load = existing_day_loads.get(best_day_str, 0.0)
        task_hours = float(task.get("estimated_hours", 1.0))
        if current_load + task_hours <= daily_available_hours:
            additions[best_day_str].append(task)
            existing_day_loads[best_day_str] = current_load + task_hours

    return additions


def compute_mastery_from_completion(done: int, total: int) -> str:
    """Derives mastery level from task completion ratio."""
    if total == 0:
        return "moderate"
    ratio = done / total
    if ratio >= 0.7:
        return "strong"
    elif ratio >= 0.4:
        return "moderate"
    else:
        return "weak"
