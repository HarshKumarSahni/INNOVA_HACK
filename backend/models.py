from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Date, JSON, ForeignKey, ARRAY, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    has_completed_onboarding = Column(Boolean, default=False)
    
    # Relationship with onboarding data
    onboarding = relationship("OnboardingData", back_populates="user", uselist=False)
    
    # --- NEW RELATIONSHIP ---
    # This links the User to their many syllabuses
    syllabuses = relationship("Syllabus", back_populates="owner", cascade="all, delete-orphan")
    
    is_authorized = Column(Boolean, default=True)
    
class OnboardingData(Base):
    __tablename__ = "onboarding_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)  # Added ForeignKey
    exam_name = Column(String, nullable=False)
    exam_date = Column(Date, nullable=False)
    current_preparation_level = Column(String, nullable=False)  # beginner, intermediate, advanced
    daily_study_hours = Column(Integer, nullable=False)
    preferred_study_time = Column(String, nullable=False)  # morning, afternoon, evening, night
    topics_covered = Column(JSON, nullable=True)  # List of topics already covered
    weak_subjects = Column(JSON, nullable=True)  # List of subjects they struggle with
    strong_subjects = Column(JSON, nullable=True)  # List of subjects they're good at
    additional_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship with user
    user = relationship("User", back_populates="onboarding")
    
class Syllabus(Base):
    __tablename__ = "syllabuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    
    # Store topics as an array of strings. This is much better than CSV.
    topics = Column(ARRAY(String), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign key to link this syllabus to a user
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="syllabuses")

# --- STUDY PLANNER MODELS ---

class SyllabusTopic(Base):
    __tablename__ = "syllabus_topics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    weightage = Column(Float, default=1.0, nullable=False)

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exam_name = Column(String, nullable=False)
    target_exam_date = Column(Date, nullable=False)
    daily_available_hours = Column(Float, nullable=False)
    status = Column(String, default="active", nullable=False)  # active, completed, archived
    excluded_topics = Column(JSON, nullable=True, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tasks = relationship("DailyTask", back_populates="plan", cascade="all, delete-orphan")

class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    estimated_hours = Column(Float, nullable=False)
    priority = Column(Integer, default=3, nullable=False)  # 1 (highest) to 5 (lowest)
    status = Column(String, default="pending", nullable=False)  # pending, done, skipped
    completed_at = Column(DateTime(timezone=True), nullable=True)

    plan = relationship("StudyPlan", back_populates="tasks")

class SubjectProgress(Base):
    __tablename__ = "subject_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String, nullable=False)
    weightage_score = Column(Float, default=1.0, nullable=False)
    mastery_level = Column(String, default="moderate", nullable=False)  # weak, moderate, strong
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())