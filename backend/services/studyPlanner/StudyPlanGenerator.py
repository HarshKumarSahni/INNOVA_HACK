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
    weak_subjects: List[str],
    daily_hours: float,
    days_remaining: int,
) -> Dict[str, Dict[str, float]]:
    """
    Computes how many hours to allocate per topic based on weightage.
    Applies a 1.3x boost to weak subjects.
    Returns: {subject: {topic: allocated_hours}}
    Raises ValueError if exam date already passed or timeline is unrealistic.
    """
    if days_remaining <= 0:
        raise ValueError(
            "Exam date has already passed or is today. Cannot generate a study plan."
        )

    total_available_hours = daily_hours * days_remaining

    # --- Step 1: Group topics by subject, sum weightage per subject ---
    subject_weight: Dict[str, float] = {}
    topic_weights: Dict[str, Dict[str, float]] = {}  # {subject: {topic: weight}}

    for item in syllabus_topics:
        subj = item["subject"]
        topic = item["topic"]
        weight = float(item.get("weightage", 1.0))

        subject_weight[subj] = subject_weight.get(subj, 0.0) + weight
        if subj not in topic_weights:
            topic_weights[subj] = {}
        topic_weights[subj][topic] = weight

    if not subject_weight:
        raise ValueError("No syllabus topics found to generate a study plan.")

    # --- Step 2: Apply weak-subject boost ---
    adjusted_weight: Dict[str, float] = {
        subj: w * (1.3 if subj in weak_subjects else 1.0)
        for subj, w in subject_weight.items()
    }

    # --- Step 3: Normalize subject shares ---
    total_adjusted = sum(adjusted_weight.values())
    subject_share: Dict[str, float] = {
        subj: w / total_adjusted for subj, w in adjusted_weight.items()
    }

    # --- Step 4: Allocate hours per subject ---
    subject_hour_budget: Dict[str, float] = {
        subj: share * total_available_hours
        for subj, share in subject_share.items()
    }

    # --- Step 5: Distribute within each subject across topics (Prioritized) ---
    hour_budget: Dict[str, Dict[str, float]] = {}
    min_hours_per_topic = 1.0  # Minimum time to meaningfully cover a topic
    unrealistic = False

    for subj, topic_map in topic_weights.items():
        # Sort topics by weightage (highest first)
        sorted_topics = sorted(topic_map.items(), key=lambda item: item[1], reverse=True)
        
        subj_total_weight = sum(topic_map.values())
        subj_hours = subject_hour_budget[subj]
        topic_allocation: Dict[str, float] = {}

        for topic, w in sorted_topics:
            allocated = (w / subj_total_weight) * subject_hour_budget[subj]
            allocated = round(allocated * 2) / 2
            
            if allocated < min_hours_per_topic:
                allocated = min_hours_per_topic
                
            if subj_hours >= allocated:
                topic_allocation[topic] = allocated
                subj_hours -= allocated
            else:
                # We ran out of budget for this subject! Skip the remaining lower-weightage topics.
                unrealistic = True
                break

        hour_budget[subj] = topic_allocation

    result = {"budget": hour_budget, "warning": None}
    if unrealistic:
        result["warning"] = (
            "Due to limited time, lower weightage topics were skipped to prioritize high-yield areas. "
            "Consider increasing daily study hours to cover the full syllabus."
        )

    return result


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
    """Formats the fixed hour budget into the sequencing prompt for OpenAI."""
    # Flatten budget into a list for LLM consumption
    budget_list = []
    for subject, topics in hour_budget_dict.items():
        for topic, hours in topics.items():
            budget_list.append({
                "subject": subject,
                "topic": topic,
                "hours": hours
            })

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
