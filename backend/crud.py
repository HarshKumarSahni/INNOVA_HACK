from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, OnboardingData, Syllabus, StudyPlan, DailyTask, SubjectProgress
from schemas import UserCreate, OnboardingCreate, OnboardingUpdate
from auth import hash_password
import pandas as pd
from typing import List, IO, Dict, Optional
from datetime import date, datetime

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_onboarding_status(db: Session, user_id: int, status: bool = True):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.has_completed_onboarding = status
        db.commit()
        db.refresh(db_user)
    return db_user

def create_onboarding_data(db: Session, user_id: int, onboarding: OnboardingCreate):
    db_onboarding = OnboardingData(
        user_id=user_id,
        exam_name=onboarding.exam_name,
        exam_date=onboarding.exam_date,
        current_preparation_level=onboarding.current_preparation_level,
        daily_study_hours=onboarding.daily_study_hours,
        preferred_study_time=onboarding.preferred_study_time,
        topics_covered=onboarding.topics_covered,
        weak_subjects=onboarding.weak_subjects,
        strong_subjects=onboarding.strong_subjects,
        additional_notes=onboarding.additional_notes
    )
    db.add(db_onboarding)
    db.commit()
    db.refresh(db_onboarding)
    return db_onboarding

def get_onboarding_data_by_user_id(db: Session, user_id: int):
    return db.query(OnboardingData).filter(OnboardingData.user_id == user_id).first()

def update_onboarding_data(db: Session, user_id: int, onboarding_update: OnboardingUpdate):
    db_onboarding = db.query(OnboardingData).filter(OnboardingData.user_id == user_id).first()
    if db_onboarding:
        update_data = onboarding_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_onboarding, field, value)
        db.commit()
        db.refresh(db_onboarding)
    return db_onboarding

def delete_onboarding_data(db: Session, user_id: int):
    db_onboarding = db.query(OnboardingData).filter(OnboardingData.user_id == user_id).first()
    if db_onboarding:
        db.delete(db_onboarding)
        db.commit()
        return True
    return False

# Syllabus Funcs
def parse_syllabus_file(file: IO) -> List[str]:
    """
    (Step 2: Validation)
    Reads an Excel file in-memory and parses the first column into a list of topics.
    Raises ValueError if the file is invalid.
    """
    try:
        # Read the file directly from the upload stream
        df = pd.read_excel(file)
        if df.empty or len(df.columns) == 0:
            raise ValueError("File is empty or has no columns.")
        
        # Get the first column, drop any empty rows, and convert to list of strings
        topic_column = df.columns[0]
        topics = df[topic_column].dropna().astype(str).tolist()
        
        if not topics:
            raise ValueError("No topics found in the first column.")
            
        return topics
    except Exception as e:
        # Catch pandas errors, bad file types, etc.
        raise ValueError(f"Failed to parse Excel file: {e}")

def create_user_syllabus(db: Session, user_id: int, name: str, topics: List[str]) -> Syllabus:
    """
    (Step 3: Storing)
    Creates and saves a new syllabus for a user.
    """
    db_syllabus = Syllabus(name=name, topics=topics, owner_id=user_id)
    db.add(db_syllabus)
    db.commit()
    db.refresh(db_syllabus)
    return db_syllabus

def get_syllabuses_by_user_id(db: Session, user_id: int) -> List[Syllabus]:
    """
    (Step 5: Selecting)
    Fetches all syllabuses owned by a specific user.
    """
    return db.query(Syllabus).filter(Syllabus.owner_id == user_id).order_by(Syllabus.name).all()

def get_syllabus_by_id(db: Session, syllabus_id: int, user_id: int) -> Syllabus:
    """
    (Step 4: Using)
    Fetches a single syllabus, ensuring it belongs to the correct user.
    """
    return db.query(Syllabus).filter(Syllabus.id == syllabus_id, Syllabus.owner_id == user_id).first()

def delete_syllabus_by_id(db: Session, syllabus_id: int, user_id: int) -> bool:
    """
    (Bonus: Managing)
    Deletes a syllabus, ensuring it belongs to the correct user.
    """
    db_syllabus = get_syllabus_by_id(db, syllabus_id, user_id)
    if db_syllabus:
        db.delete(db_syllabus)
        db.commit()
        return True
    return False


# ============================================================
# === STUDY PLANNER CRUD ===
# ============================================================

def create_study_plan(
    db: Session,
    user_id: int,
    exam_name: str,
    target_exam_date: date,
    daily_available_hours: float,
    excluded_topics: Optional[List[dict]] = None,
) -> StudyPlan:
    """Creates a new active study plan for a user."""
    plan = StudyPlan(
        user_id=user_id,
        exam_name=exam_name,
        target_exam_date=target_exam_date,
        daily_available_hours=daily_available_hours,
        status="active",
        excluded_topics=excluded_topics or [],
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_active_plan(db: Session, user_id: int) -> Optional[StudyPlan]:
    """Returns the active study plan for a user, or None."""
    return (
        db.query(StudyPlan)
        .filter(StudyPlan.user_id == user_id, StudyPlan.status == "active")
        .first()
    )


def get_plan_by_id(db: Session, plan_id: int, user_id: int) -> Optional[StudyPlan]:
    """Returns a specific plan, verifying ownership."""
    return (
        db.query(StudyPlan)
        .filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id)
        .first()
    )


def bulk_create_tasks(db: Session, plan_id: int, tasks: List[Dict]) -> List[DailyTask]:
    """
    Bulk inserts daily tasks from the LLM-parsed schedule.
    Each task dict: {date, subject, topic, estimated_hours, priority, status}
    """
    db_tasks = [
        DailyTask(
            plan_id=plan_id,
            date=t["date"],
            subject=t["subject"],
            topic=t["topic"],
            estimated_hours=t["estimated_hours"],
            priority=t.get("priority", 3),
            status="pending",
        )
        for t in tasks
    ]
    db.bulk_save_objects(db_tasks)
    db.commit()
    # Reload with IDs
    return db.query(DailyTask).filter(DailyTask.plan_id == plan_id).order_by(DailyTask.date).all()


def get_tasks_by_date(db: Session, plan_id: int, query_date: date) -> List[DailyTask]:
    """Returns all tasks for a specific plan on a given date."""
    return (
        db.query(DailyTask)
        .filter(DailyTask.plan_id == plan_id, DailyTask.date == query_date)
        .order_by(DailyTask.priority)
        .all()
    )


def update_task_status(
    db: Session, task_id: int, user_id: int, new_status: str
) -> Optional[DailyTask]:
    """
    Updates a task status after verifying the task belongs to the user.
    Returns None if not found or ownership check fails (treat as 404).
    """
    task = (
        db.query(DailyTask)
        .join(StudyPlan, DailyTask.plan_id == StudyPlan.id)
        .filter(DailyTask.id == task_id, StudyPlan.user_id == user_id)
        .first()
    )
    if not task:
        return None

    task.status = new_status
    task.completed_at = datetime.utcnow() if new_status == "done" else None
    db.commit()
    db.refresh(task)
    return task


def get_subject_progress(db: Session, user_id: int) -> List[Dict]:
    """
    Returns per-subject progress: tasks_done, tasks_total, mastery_level.
    Joins SubjectProgress with DailyTask counts via active plan.
    """
    active_plan = get_active_plan(db, user_id)
    if not active_plan:
        return []

    # Total tasks per subject
    total_q = (
        db.query(DailyTask.subject, func.count(DailyTask.id).label("total"))
        .filter(DailyTask.plan_id == active_plan.id)
        .group_by(DailyTask.subject)
        .all()
    )

    # Done tasks per subject
    done_q = (
        db.query(DailyTask.subject, func.count(DailyTask.id).label("done"))
        .filter(DailyTask.plan_id == active_plan.id, DailyTask.status == "done")
        .group_by(DailyTask.subject)
        .all()
    )

    total_map = {row.subject: row.total for row in total_q}
    done_map = {row.subject: row.done for row in done_q}

    progress_records = (
        db.query(SubjectProgress)
        .filter(SubjectProgress.user_id == user_id)
        .all()
    )

    result = []
    result = []
    for sp in progress_records:
        subj = sp.subject
        clean_subj = subj if subj else "General"
        result.append({
            "subject": clean_subj,
            "weightage_score": float(sp.weightage_score) if sp.weightage_score is not None else 1.0,
            "mastery_level": sp.mastery_level if sp.mastery_level is not None else "mastered",
            "tasks_completed": int(done_map.get(subj, 1)),
            "tasks_total": int(total_map.get(subj, 1)),
        })

    return result

def delete_subject_progress(db: Session, user_id: int, subject: str):
    db.query(SubjectProgress).filter(
        SubjectProgress.user_id == user_id,
        SubjectProgress.subject == subject
    ).delete()
    db.commit()


def upsert_subject_progress(
    db: Session,
    user_id: int,
    subject: str,
    mastery_level: str,
    weightage_score: float = 1.0,
) -> SubjectProgress:
    """Creates or updates a SubjectProgress row for the given user+subject."""
    existing = (
        db.query(SubjectProgress)
        .filter(
            SubjectProgress.user_id == user_id,
            SubjectProgress.subject == subject,
        )
        .first()
    )
    if existing:
        existing.mastery_level = mastery_level
        existing.weightage_score = weightage_score
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        sp = SubjectProgress(
            user_id=user_id,
            subject=subject,
            weightage_score=weightage_score,
            mastery_level=mastery_level,
        )
        db.add(sp)
        db.commit()
        db.refresh(sp)
        return sp


def archive_active_plan(db: Session, user_id: int) -> Optional[StudyPlan]:
    """Archives any existing active plan for a user before creating a new one."""
    plan = get_active_plan(db, user_id)
    if plan:
        plan.status = "archived"
        db.commit()
        db.refresh(plan)
    return plan