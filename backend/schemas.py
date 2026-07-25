from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List, Literal
from enum import Enum

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    credential: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    has_completed_onboarding: bool

    class Config:
        from_attributes = True

class PreparationLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class StudyTime(str, Enum):
    morning = "morning"
    afternoon = "afternoon"
    evening = "evening"
    night = "night"

class OnboardingCreate(BaseModel):
    exam_name: str
    exam_date: date
    current_preparation_level: PreparationLevel
    daily_study_hours: int
    preferred_study_time: StudyTime
    topics_covered: Optional[List[str]] = []
    weak_subjects: Optional[List[str]] = []
    strong_subjects: Optional[List[str]] = []
    additional_notes: Optional[str] = None

class OnboardingResponse(BaseModel):
    id: int
    user_id: int
    exam_name: str
    exam_date: date
    current_preparation_level: str
    daily_study_hours: int
    preferred_study_time: str
    topics_covered: Optional[List[str]] = []
    weak_subjects: Optional[List[str]] = []
    strong_subjects: Optional[List[str]] = []
    additional_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OnboardingUpdate(BaseModel):
    exam_name: Optional[str] = None
    exam_date: Optional[date] = None
    current_preparation_level: Optional[PreparationLevel] = None
    daily_study_hours: Optional[int] = None
    preferred_study_time: Optional[StudyTime] = None
    topics_covered: Optional[List[str]] = None
    weak_subjects: Optional[List[str]] = None
    strong_subjects: Optional[List[str]] = None
    additional_notes: Optional[str] = None

# --- STUDY PLANNER SCHEMAS ---

class StudyPlanCreateRequest(BaseModel):
    daily_available_hours: float
    weak_subjects: Optional[List[str]] = []

class DailyTaskOut(BaseModel):
    id: int
    date: date
    subject: str
    topic: str
    estimated_hours: float
    priority: int
    status: Literal["pending", "done", "skipped"]
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StudyPlanOut(BaseModel):
    id: int
    exam_name: str
    target_exam_date: date
    daily_available_hours: float
    status: str
    tasks: List[DailyTaskOut] = []

    class Config:
        from_attributes = True

class TaskUpdateRequest(BaseModel):
    status: Literal["pending", "done", "skipped"]

class RegeneratePlanRequest(BaseModel):
    force_full: bool = False

class SubjectProgressOut(BaseModel):
    subject: str
    weightage_score: float
    mastery_level: str
    tasks_completed: int
    tasks_total: int

    class Config:
        from_attributes = True