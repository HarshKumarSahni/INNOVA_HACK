# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User
from schemas import (
    UserCreate, UserLogin, UserResponse,
    OnboardingCreate, OnboardingResponse, OnboardingUpdate,
    StudyPlanCreateRequest, StudyPlanOut, DailyTaskOut,
    TaskUpdateRequest, RegeneratePlanRequest, SubjectProgressOut,
    GoogleLoginRequest
)
from crud import (
    get_user_by_email, create_user, get_user_by_id,
    create_onboarding_data, get_onboarding_data_by_user_id,
    update_onboarding_data, update_user_onboarding_status,
    get_syllabuses_by_user_id, get_syllabus_by_id,
    parse_syllabus_file, create_user_syllabus, delete_syllabus_by_id,
    # Study Planner
    create_study_plan, get_active_plan, get_plan_by_id,
    bulk_create_tasks, get_tasks_by_date, update_task_status,
    get_subject_progress, upsert_subject_progress, archive_active_plan
)
from auth import verify_password, create_access_token, get_current_user_from_token

from typing import Dict, List, Optional
from pydantic import BaseModel
import os
from datetime import date as date_type

# Since uvicorn runs from 'src', Python can find MockTestAutomation directly
from services.mocktest.Generation import run_generation_task
from services.mocktest.PromptsDict import prompt_templates
from services.studyPlanner.StudyPlanGenerator import (
    compute_hour_budget, _generate_schedule_from_llm,
    _validate_and_cap_daily_hours, redistribute_overdue_tasks, compute_mastery_from_completion
)

# Initialize Database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AceTrack API", version="1.0.0")

# --- Pydantic Models for Mock Test Generator ---
class QuestionGenerationRequest(BaseModel):
    question_plan: Dict[str, int]
    testing_mode: bool = False
    exam_name: str
    output_format: str = 'pdf'
    questions_per_chunk: int
    syllabus_id: int 
    subjects: Optional[List[str]] = None

class QuestionGenerationResponse(BaseModel):
    success: bool
    message: str
    files: Optional[Dict[str, str]] = None

class QuestionType(BaseModel):
    name: str
    description: str

class SyllabusResponse(BaseModel):
    id: int
    name: str
    created_at: str
    topic_count: int

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Create Router with /api prefix ---
api_router = APIRouter(prefix="/api")

# ===============================================================
# === MOCK TEST GENERATOR API ENDPOINTS ===
# ===============================================================

@api_router.get("/syllabus-subjects", response_model=List[str])
async def get_syllabus_subjects():
    from utils.syllabus_parser import get_available_subjects
    try:
        return get_available_subjects()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading syllabus file: {str(e)}")

@api_router.get("/question-types", response_model=List[QuestionType])
async def get_question_types():
    descriptions = {
        "MTF": "Match the Following questions.", "2S": "Two-statement reasoning questions.",
        "3S": "Three-statement analysis questions.", "4S": "Four-statement analysis questions.",
        "5S": "Five-statement, highly analytical questions.", "SL": "Single-liner scenario-based questions.",
        "AR": "Assertion and Reasoning questions.", "CS": "Case study comprehension questions.",
        "CH": "Chronological ordering questions.", "FU": "Fill in the Blanks questions.",
        "MCQ": "Multiple choice questions.", "NU": "Numerical answer type questions."
    }
    try:
        if not prompt_templates:
            raise HTTPException(status_code=500, detail="Prompt templates are not loaded.")
        return [
            QuestionType(name=qtype, description=descriptions.get(qtype, f"Generate {qtype} questions."))
            for qtype in prompt_templates.keys()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading question types: {str(e)}")

@api_router.post("/generate-questions", response_model=QuestionGenerationResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.id == current_user["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        syllabus = get_syllabus_by_id(db, request.syllabus_id, current_user["user_id"])
        if not syllabus:
            raise HTTPException(status_code=404, detail="Syllabus not found or you don't have access to it")
        from utils.syllabus_parser import parse_syllabus_weightage
        parsed_syllabus = parse_syllabus_weightage()
        
        final_topics = {}
        if request.subjects and parsed_syllabus:
            for subj in request.subjects:
                if subj in parsed_syllabus:
                    final_topics[subj] = [t["topic"] for t in parsed_syllabus[subj]]
        
        # Fallback to DB syllabus topics if no subjects selected or Excel failed
        if not final_topics:
            final_topics = {"General": syllabus.topics}

        result = run_generation_task(
            plan=request.question_plan,
            testing_mode=request.testing_mode,
            exam_name=request.exam_name,
            output_format=request.output_format,
            questions_per_chunk=request.questions_per_chunk,
            topics=final_topics
        )
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@api_router.get("/wakeup")
async def wakeup():
    return {"mssg":"I am ready"}

@api_router.get("/download-questions/{filename}")
async def download_questions_file(
    filename: str,
    current_user: dict = Depends(get_current_user_from_token)
):
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_script_dir, "data", "generated_files", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found.")
    
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')

# ===============================================================
# === SYLLABUS API ENDPOINTS ===
# ===============================================================

@api_router.get("/syllabus", response_model=List[SyllabusResponse])
async def get_user_syllabuses(
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    syllabuses = get_syllabuses_by_user_id(db, current_user["user_id"])
    return [
        SyllabusResponse(
            id=s.id, name=s.name, created_at=s.created_at.isoformat(), topic_count=len(s.topics)
        ) for s in syllabuses
    ]

@api_router.post("/syllabus/upload")
async def upload_syllabus(
    name: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only .xlsx and .xls files allowed.")
        topics = parse_syllabus_file(file.file)
        syllabus = create_user_syllabus(db, current_user["user_id"], name, topics)
        return SyllabusResponse(
            id=syllabus.id, name=syllabus.name, created_at=syllabus.created_at.isoformat(), topic_count=len(syllabus.topics)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router.delete("/syllabus/{syllabus_id}")
async def delete_syllabus(
    syllabus_id: int,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    success = delete_syllabus_by_id(db, syllabus_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    return {"message": "Syllabus deleted successfully"}

# ===============================================================
# === USER AUTH & ONBOARDING ENDPOINTS ===
# ===============================================================

@api_router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user: 
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user)
    return UserResponse(id=new_user.id, email=new_user.email, has_completed_onboarding=new_user.has_completed_onboarding)

@api_router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": db_user.email, "user_id": db_user.id})
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": UserResponse(id=db_user.id, email=db_user.email, has_completed_onboarding=db_user.has_completed_onboarding)
    }

@api_router.post("/auth/google")
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    import os
    import secrets
    from auth import hash_password, create_access_token
    
    CLIENT_ID = os.getenv("VITE_GOOGLE_CLIENT_ID")
    if not CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Client ID is not configured on the server.")
        
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            payload.credential, 
            google_requests.Request(), 
            CLIENT_ID
        )
        
        email = idinfo.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Google token did not contain an email address.")
            
        # Check if user exists
        db_user = get_user_by_email(db, email)
        if not db_user:
            # Create a new user with a random hashed password since they use Google
            random_pwd = secrets.token_urlsafe(32)
            user_create = UserCreate(email=email, password=random_pwd)
            db_user = create_user(db, user_create)
            
        access_token = create_access_token(data={"sub": db_user.email, "user_id": db_user.id})
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": UserResponse(id=db_user.id, email=db_user.email, has_completed_onboarding=db_user.has_completed_onboarding)
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")

@api_router.get("/me", response_model=UserResponse)
def get_current_user(current_user: dict = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    user = get_user_by_id(db, current_user["user_id"])
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, email=user.email, has_completed_onboarding=user.has_completed_onboarding)

@api_router.post("/onboarding", response_model=OnboardingResponse)
def create_user_onboarding(onboarding_data: OnboardingCreate, current_user: dict = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    if get_onboarding_data_by_user_id(db, user_id): 
        raise HTTPException(status_code=400, detail="Onboarding already completed.")
    db_onboarding = create_onboarding_data(db, user_id, onboarding_data)
    update_user_onboarding_status(db, user_id, True)
    return db_onboarding

@api_router.get("/onboarding", response_model=OnboardingResponse)
def get_user_onboarding(current_user: dict = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    onboarding_data = get_onboarding_data_by_user_id(db, user_id)
    if not onboarding_data: 
        raise HTTPException(status_code=404, detail="Onboarding data not found")
    return onboarding_data

@api_router.put("/onboarding", response_model=OnboardingResponse)
def update_user_onboarding(onboarding_update: OnboardingUpdate, current_user: dict = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    try:
        updated_onboarding = update_onboarding_data(db, user_id, onboarding_update)
        return updated_onboarding
    except Exception:
        raise HTTPException(status_code=500, detail="Update failed")

@api_router.get("/onboarding/status")
def check_onboarding_status(current_user: dict = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    user = get_user_by_id(db, current_user["user_id"])
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    return {"has_completed_onboarding": user.has_completed_onboarding, "user_id": user.id}


# ===============================================================
# === STUDY PLANNER API ENDPOINTS ===
# ===============================================================

def _plan_to_out(plan) -> StudyPlanOut:
    """Helper to serialize StudyPlan ORM object to StudyPlanOut schema."""
    return StudyPlanOut(
        id=plan.id,
        exam_name=plan.exam_name,
        target_exam_date=plan.target_exam_date,
        daily_available_hours=plan.daily_available_hours,
        status=plan.status,
        tasks=[
            DailyTaskOut(
                id=t.id,
                date=t.date,
                subject=t.subject,
                topic=t.topic,
                estimated_hours=t.estimated_hours,
                priority=t.priority,
                status=t.status,
                completed_at=t.completed_at,
            )
            for t in sorted(plan.tasks, key=lambda x: x.date)
        ]
    )


@api_router.post("/study-plan/generate", response_model=StudyPlanOut)
def generate_study_plan(
    request: StudyPlanCreateRequest,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Generates a new AI study plan. Returns 409 if an active plan already exists."""
    user_id = current_user["user_id"]

    # 409: Active plan already exists
    existing = get_active_plan(db, user_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="An active study plan already exists. Use /study-plan/regenerate to update it."
        )

    # Fetch onboarding for exam date + exam name
    onboarding = get_onboarding_data_by_user_id(db, user_id)
    if not onboarding:
        raise HTTPException(status_code=422, detail="Complete onboarding first to set your exam date.")

    from datetime import date as today_type
    today = today_type.today()
    days_remaining = (onboarding.exam_date - today).days

    if days_remaining <= 0:
        raise HTTPException(status_code=422, detail="Exam date has already passed. Please update your exam date in onboarding.")

    # Fetch syllabuses and flatten into topic dicts
    syllabuses = get_syllabuses_by_user_id(db, user_id)
    if not syllabuses:
        raise HTTPException(status_code=422, detail="Upload at least one syllabus file before generating a study plan.")

    # Build flat topic list from all syllabuses (each topic string = subject+topic)
    from utils.syllabus_parser import parse_syllabus_weightage
    parsed_syllabus = parse_syllabus_weightage()
    
    topic_list = []
    if parsed_syllabus:
        for subj, topics in parsed_syllabus.items():
            for t in topics:
                topic_list.append({
                    "subject": subj, 
                    "topic": t["topic"], 
                    "weightage": float(t.get("weightage", 1.0))
                })
    else:
        for syl in syllabuses:
            for i, topic_str in enumerate(syl.topics):
                parts = topic_str.split(":", 1)
                subject = parts[0].strip() if len(parts) == 2 else syl.name
                topic = parts[1].strip() if len(parts) == 2 else topic_str.strip()
                topic_list.append({"subject": subject, "topic": topic, "weightage": 1.0})

    if not topic_list:
        raise HTTPException(status_code=422, detail="No topics found in your syllabus files.")

    # Compute hour budget
    try:
        budget_result = compute_hour_budget(
            syllabus_topics=topic_list,
            weak_subjects=request.weak_subjects or [],
            daily_hours=request.daily_available_hours,
            days_remaining=days_remaining,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    hour_budget = budget_result["budget"]

    # Call LLM for sequencing
    try:
        raw_days = _generate_schedule_from_llm(
            hour_budget=hour_budget,
            start_date=today,
            target_exam_date=onboarding.exam_date,
            days_remaining=days_remaining,
            daily_available_hours=request.daily_available_hours,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Validate & cap daily hours
    validated_days = _validate_and_cap_daily_hours(raw_days, request.daily_available_hours)

    # Persist study plan
    plan = create_study_plan(
        db=db,
        user_id=user_id,
        exam_name=onboarding.exam_name,
        target_exam_date=onboarding.exam_date,
        daily_available_hours=request.daily_available_hours,
    )

    # Flatten tasks for bulk insert
    flat_tasks = []
    subject_set = set()
    for day_entry in validated_days:
        try:
            task_date = date_type.fromisoformat(day_entry["date"])
        except (ValueError, KeyError):
            continue
        for task in day_entry.get("tasks", []):
            flat_tasks.append({
                "date": task_date,
                "subject": task.get("subject", "General"),
                "topic": task.get("topic", "Study"),
                "estimated_hours": float(task.get("hours", 1.0)),
                "priority": 3,
            })
            subject_set.add(task.get("subject", "General"))

    bulk_create_tasks(db, plan.id, flat_tasks)

    # Subject progress is no longer initialized here; it's handled on task completion.
    # Reload plan with tasks
    plan = get_plan_by_id(db, plan.id, user_id)
    return _plan_to_out(plan)


@api_router.get("/study-plan/active", response_model=StudyPlanOut)
def get_active_study_plan(
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Returns the current active study plan, or 404 if none exists."""
    plan = get_active_plan(db, current_user["user_id"])
    if not plan:
        raise HTTPException(status_code=404, detail="No active study plan found. Generate one first.")
    return _plan_to_out(plan)


@api_router.get("/study-plan/today", response_model=List[DailyTaskOut])
def get_todays_tasks(
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Returns only today's tasks from the active plan."""
    plan = get_active_plan(db, current_user["user_id"])
    if not plan:
        raise HTTPException(status_code=404, detail="No active study plan found.")
    today = date_type.today()
    tasks = get_tasks_by_date(db, plan.id, today)
    return [
        DailyTaskOut(
            id=t.id, date=t.date, subject=t.subject, topic=t.topic,
            estimated_hours=t.estimated_hours, priority=t.priority,
            status=t.status, completed_at=t.completed_at
        )
        for t in tasks
    ]


@api_router.get("/study-plan/{plan_id}", response_model=StudyPlanOut)
def get_study_plan_by_id(
    plan_id: int,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Returns a specific plan by ID (ownership enforced)."""
    plan = get_plan_by_id(db, plan_id, current_user["user_id"])
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found.")
    return _plan_to_out(plan)


@api_router.patch("/study-plan/task/{task_id}", response_model=DailyTaskOut)
def patch_task_status(
    task_id: int,
    body: TaskUpdateRequest,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Updates a task status (pending/done/skipped). Validates ownership."""
    task = update_task_status(db, task_id, current_user["user_id"], body.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied.")

    from crud import upsert_subject_progress, delete_subject_progress
    if body.status == "done":
        from utils.syllabus_parser import parse_syllabus_weightage
        parsed = parse_syllabus_weightage()
        weight = 1.0
        if parsed and task.subject in parsed:
            for t in parsed[task.subject]:
                if t["topic"] == task.topic:
                    weight = float(t.get("weightage", 1.0))
                    break
        upsert_subject_progress(db, current_user["user_id"], task.topic, "mastered", weightage_score=weight)
    else:
        delete_subject_progress(db, current_user["user_id"], task.topic)
    return DailyTaskOut(
        id=task.id, date=task.date, subject=task.subject, topic=task.topic,
        estimated_hours=task.estimated_hours, priority=task.priority,
        status=task.status, completed_at=task.completed_at
    )


@api_router.post("/study-plan/regenerate", response_model=StudyPlanOut)
def regenerate_study_plan(
    body: RegeneratePlanRequest,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Adaptive regeneration:
    - force_full=False: rule-based rebalancing of overdue tasks.
    - force_full=True: archives current plan and generates a fresh LLM plan.
    """
    user_id = current_user["user_id"]
    plan = get_active_plan(db, user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No active study plan to regenerate.")

    if body.force_full:
        archive_active_plan(db, user_id)
        # Delegate to generate endpoint logic by raising to re-call
        # (We reuse generate logic inline to avoid HTTP redirect)
        from datetime import date as today_type
        today = today_type.today()
        onboarding = get_onboarding_data_by_user_id(db, user_id)
        if not onboarding:
            raise HTTPException(status_code=422, detail="Onboarding data missing.")
        days_remaining = (onboarding.exam_date - today).days
        if days_remaining <= 0:
            raise HTTPException(status_code=422, detail="Exam date has already passed.")
        syllabuses = get_syllabuses_by_user_id(db, user_id)
        from utils.syllabus_parser import parse_syllabus_weightage
        parsed_syllabus = parse_syllabus_weightage()
        
        topic_list = []
        if parsed_syllabus:
            for subj, topics in parsed_syllabus.items():
                for t in topics:
                    topic_list.append({
                        "subject": subj, 
                        "topic": t["topic"], 
                        "weightage": float(t.get("weightage", 1.0))
                    })
        else:
            for syl in syllabuses:
                for topic_str in syl.topics:
                    parts = topic_str.split(":", 1)
                    subject = parts[0].strip() if len(parts) == 2 else syl.name
                    topic = parts[1].strip() if len(parts) == 2 else topic_str.strip()
                    topic_list.append({"subject": subject, "topic": topic, "weightage": 1.0})
        try:
            budget_result = compute_hour_budget(topic_list, [], plan.daily_available_hours, days_remaining)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        try:
            raw_days = _generate_schedule_from_llm(
                hour_budget=budget_result["budget"],
                start_date=today,
                target_exam_date=onboarding.exam_date,
                days_remaining=days_remaining,
                daily_available_hours=plan.daily_available_hours,
            )
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
        validated_days = _validate_and_cap_daily_hours(raw_days, plan.daily_available_hours)
        new_plan = create_study_plan(db, user_id, onboarding.exam_name, onboarding.exam_date, plan.daily_available_hours)
        flat_tasks = []
        for day_entry in validated_days:
            try:
                task_date = date_type.fromisoformat(day_entry["date"])
            except (ValueError, KeyError):
                continue
            for task in day_entry.get("tasks", []):
                flat_tasks.append({
                    "date": task_date, "subject": task.get("subject", "General"),
                    "topic": task.get("topic", "Study"),
                    "estimated_hours": float(task.get("hours", 1.0)), "priority": 3,
                })
        bulk_create_tasks(db, new_plan.id, flat_tasks)
        new_plan = get_plan_by_id(db, new_plan.id, user_id)
        return _plan_to_out(new_plan)
    else:
        # Rule-based: redistribute overdue tasks across remaining days
        from datetime import date as today_type
        today = today_type.today()
        from models import DailyTask as DT
        overdue = (
            db.query(DT)
            .filter(DT.plan_id == plan.id, DT.date < today, DT.status == "pending")
            .all()
        )
        if not overdue:
            return _plan_to_out(plan)

        # Get remaining days in plan
        onboarding = get_onboarding_data_by_user_id(db, user_id)
        if not onboarding:
            return _plan_to_out(plan)
        remaining_days = [
            today + __import__('datetime').timedelta(days=i)
            for i in range((onboarding.exam_date - today).days)
        ]
        if not remaining_days:
            return _plan_to_out(plan)

        from models import DailyTask as DT2
        existing_loads = {}
        for t in db.query(DT2).filter(DT2.plan_id == plan.id, DT2.date >= today).all():
            ds = t.date.isoformat()
            existing_loads[ds] = existing_loads.get(ds, 0.0) + t.estimated_hours

        overdue_dicts = [{"estimated_hours": t.estimated_hours, "subject": t.subject, "topic": t.topic} for t in overdue]
        additions = redistribute_overdue_tasks(overdue_dicts, remaining_days, plan.daily_available_hours, existing_loads)

        # Delete old overdue tasks
        for t in overdue:
            db.delete(t)
        db.commit()

        # Insert redistributed tasks
        new_tasks = []
        for date_str, tasks in additions.items():
            for task in tasks:
                new_tasks.append({
                    "date": date_type.fromisoformat(date_str),
                    "subject": task["subject"],
                    "topic": task["topic"],
                    "estimated_hours": task["estimated_hours"],
                    "priority": 3,
                })
        if new_tasks:
            bulk_create_tasks(db, plan.id, new_tasks)

        plan = get_plan_by_id(db, plan.id, user_id)
        return _plan_to_out(plan)


@api_router.get("/study-plan/progress", response_model=List[SubjectProgressOut])
def get_progress(
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Returns per-subject progress metrics."""
    progress = get_subject_progress(db, current_user["user_id"])
    return [
        SubjectProgressOut(
            subject=p["subject"],
            weightage_score=p["weightage_score"],
            mastery_level=p["mastery_level"],
            tasks_completed=p["tasks_completed"],
            tasks_total=p["tasks_total"],
        )
        for p in progress
    ]


# --- Include the router in the app ---
app.include_router(api_router)

# Root endpoint for health checks
# @app.get("/")
# def read_root(): 
#     return {"message": "AceTrack API is running!"}
# Change your existing @app.get("/") to this:
@app.api_route("/", methods=["GET", "HEAD"])
async def read_root(): 
    return {"message": "AceTrack API is running!"}