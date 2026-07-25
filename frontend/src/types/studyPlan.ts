// frontend/src/types/studyPlan.ts
// TypeScript interfaces mirroring backend Pydantic schemas

export type TaskStatus = 'pending' | 'done' | 'skipped';
export type MasteryLevel = 'weak' | 'moderate' | 'strong';
export type PlanStatus = 'active' | 'completed' | 'archived';

export interface DailyTask {
  id: number;
  date: string; // ISO date string "YYYY-MM-DD"
  subject: string;
  topic: string;
  estimated_hours: number;
  priority: number;
  status: TaskStatus;
  completed_at: string | null;
}

export interface ExcludedTopic {
  subject: string;
  topic: string;
  reason: string;
}

export interface StudyPlan {
  id: number;
  exam_name: string;
  target_exam_date: string;
  daily_available_hours: number;
  status: PlanStatus;
  tasks: DailyTask[];
  excluded_topics?: ExcludedTopic[];
}

export interface StudyPlanCreateRequest {
  exam_name: string;
  topics_already_done?: string[];
  exam_date: string; // ISO date string "YYYY-MM-DD"
  daily_available_hours: number;
  days_per_week_available: number;
  weak_subjects?: string[];
}

export interface TaskUpdateRequest {
  status: TaskStatus;
}

export interface SubjectProgress {
  subject: string;
  weightage_score: number;
  mastery_level: MasteryLevel;
  tasks_completed: number;
  tasks_total: number;
}

export interface RegeneratePlanRequest {
  force_full: boolean;
}
