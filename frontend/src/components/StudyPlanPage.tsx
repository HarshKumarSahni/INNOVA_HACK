import React, { useState, useEffect, useCallback } from 'react';
import {
  Calendar, Plus, RefreshCw, CheckCircle2, Clock,
  AlertCircle, Loader2, ChevronLeft, ChevronRight,
  BookOpen, Flame, Target, SkipForward, RotateCcw, X, AlertTriangle
} from 'lucide-react';
import { API_BASE_URL } from '../config';
import type {
  StudyPlan, DailyTask, SubjectProgress,
  StudyPlanCreateRequest, TaskStatus, MasteryLevel, ExcludedTopic
} from '../types/studyPlan';

// ─── helpers ────────────────────────────────────────────────

const SUBJECT_COLORS: Record<string, string> = {
  Physics: 'bg-blue-100 text-blue-800 border-blue-200',
  Chemistry: 'bg-green-100 text-green-800 border-green-200',
  Maths: 'bg-purple-100 text-purple-800 border-purple-200',
  Mathematics: 'bg-purple-100 text-purple-800 border-purple-200',
  Biology: 'bg-emerald-100 text-emerald-800 border-emerald-200',
};

const getSubjectColor = (subject: string) =>
  SUBJECT_COLORS[subject] ?? 'bg-gray-100 text-gray-800 border-gray-200';

const masteryColor: Record<MasteryLevel, string> = {
  weak: 'text-red-600 bg-red-50 border-red-200',
  moderate: 'text-amber-600 bg-amber-50 border-amber-200',
  strong: 'text-green-600 bg-green-50 border-green-200',
};

const masteryIcon: Record<MasteryLevel, string> = {
  weak: '⚠️',
  moderate: '📊',
  strong: '✅',
};

function groupTasksByDate(tasks: DailyTask[]): Record<string, DailyTask[]> {
  return tasks.reduce((acc, task) => {
    if (!acc[task.date]) acc[task.date] = [];
    acc[task.date].push(task);
    return acc;
  }, {} as Record<string, DailyTask[]>);
}

function isoToDisplay(dateStr: string) {
  const [y, m, d] = dateStr.split('-');
  return new Date(Number(y), Number(m) - 1, Number(d)).toLocaleDateString('en-IN', {
    weekday: 'short', day: 'numeric', month: 'short',
  });
}

function today() {
  return new Date().toISOString().split('T')[0];
}

function defaultExamDate() {
  const d = new Date();
  d.setDate(d.getDate() + 60);
  return d.toISOString().split('T')[0];
}

function formatTopicTitle(topicStr: string) {
  if (!topicStr) return '';
  const firstLine = topicStr.split('\n')[0].trim();
  if (firstLine.length > 50) return firstLine.substring(0, 47) + '...';
  return firstLine;
}

// ─── Task Card Sub-component ─────────────────────────────────

interface TaskCardProps {
  task: DailyTask;
  onStatusChange: (taskId: number, status: TaskStatus) => void;
  updating: boolean;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onStatusChange, updating }) => (
  <div
    className={`flex items-start gap-3 p-3 rounded-xl border transition-all duration-200
      ${task.status === 'done' ? 'bg-green-50 border-green-200 opacity-75' : ''}
      ${task.status === 'skipped' ? 'bg-gray-50 border-gray-200 opacity-60' : ''}
      ${task.status === 'pending' ? 'bg-white border-gray-200 hover:border-indigo-300 hover:shadow-sm' : ''}
    `}
  >
    {/* Checkbox */}
    <button
      disabled={updating}
      onClick={() => onStatusChange(task.id, task.status === 'done' ? 'pending' : 'done')}
      className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors
        ${task.status === 'done' ? 'bg-green-500 border-green-500' : 'border-gray-300 hover:border-green-500'}`}
    >
      {task.status === 'done' && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
    </button>

    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-2 flex-wrap">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${getSubjectColor(task.subject)}`}>
          {task.subject}
        </span>
        <span className="text-xs text-gray-400 flex items-center gap-1">
          <Clock className="w-3 h-3" /> {task.estimated_hours}h
        </span>
      </div>
      <p className={`mt-1 text-sm font-medium ${task.status === 'done' ? 'line-through text-gray-400' : 'text-gray-800'}`}>
        {task.topic}
      </p>
    </div>

    {/* Skip button */}
    {task.status === 'pending' && (
      <button
        disabled={updating}
        onClick={() => onStatusChange(task.id, 'skipped')}
        title="Skip"
        className="text-gray-300 hover:text-gray-500 transition-colors"
      >
        <SkipForward className="w-4 h-4" />
      </button>
    )}
    {task.status === 'skipped' && (
      <button
        disabled={updating}
        onClick={() => onStatusChange(task.id, 'pending')}
        title="Restore"
        className="text-gray-300 hover:text-amber-500 transition-colors"
      >
        <RotateCcw className="w-4 h-4" />
      </button>
    )}
  </div>
);

// ─── Generate Form Component ─────────────────────────────────

interface GenerateFormProps {
  onGenerate: (req: StudyPlanCreateRequest) => void;
  loading: boolean;
  token: string;
}

const GenerateForm: React.FC<GenerateFormProps> = ({ onGenerate, loading, token }) => {
  // Form States (In order of fields required)
  const [examName, setExamName] = useState('JEE');
  const [topicsBySubject, setTopicsBySubject] = useState<{ [key: string]: string[] }>({});
  const [topicsAlreadyDone, setTopicsAlreadyDone] = useState<string[]>([]);
  const [examDate, setExamDate] = useState(defaultExamDate());
  const [dailyHours, setDailyHours] = useState(4);
  const [daysPerWeek, setDaysPerWeek] = useState(6);
  const [weakSubjects, setWeakSubjects] = useState<string[]>([]);

  // Fetch subject-wise topics for "Topics Already Done" selector
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/syllabus-topics-by-subject`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setTopicsBySubject(data);
        }
      } catch (e) {
        console.error('Error fetching syllabus topics:', e);
      }
    };
    fetchTopics();
  }, [token]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate({
      exam_name: examName,
      topics_already_done: topicsAlreadyDone,
      exam_date: examDate,
      daily_available_hours: dailyHours,
      days_per_week_available: daysPerWeek,
      weak_subjects: weakSubjects,
    });
  };

  return (
    <div className="flex flex-col items-center justify-center py-10 px-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-xl border border-indigo-100 p-8">
        <div className="flex items-center gap-3 mb-6 border-b pb-4">
          <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-md">
            <Calendar className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Generate Study Plan</h2>
            <p className="text-sm text-gray-500">Configure your parameters to generate your personalized schedule</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* FIELD 1: Exam Name Dropdown */}
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1.5">
              1. Exam Name
            </label>
            <select
              value={examName}
              onChange={e => setExamName(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium text-gray-800"
            >
              <option value="JEE">JEE</option>
            </select>
          </div>

          {/* FIELD 2: Topics Already Done (Subject-wise multi-select dropdowns & chips) */}
          <div className="space-y-3 bg-gray-50/70 p-4 rounded-xl border border-gray-200">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-semibold text-gray-800">
                2. Topics Already Done <span className="text-xs font-normal text-gray-500">(Optional — excluded from your plan)</span>
              </label>
              {topicsAlreadyDone.length > 0 && (
                <button
                  type="button"
                  onClick={() => setTopicsAlreadyDone([])}
                  className="text-xs text-red-600 hover:text-red-800 font-medium hover:underline"
                >
                  Clear Done Topics ({topicsAlreadyDone.length})
                </button>
              )}
            </div>

            {Object.keys(topicsBySubject).length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {Object.entries(topicsBySubject).map(([subj, topics]) => {
                  const unselectedTopics = topics.filter(t => !topicsAlreadyDone.includes(t));
                  const selectedSubjDone = topics.filter(t => topicsAlreadyDone.includes(t));

                  const themeStyles: { [key: string]: { border: string; headerBg: string; badgeBg: string; text: string } } = {
                    Physics: { border: 'border-indigo-200', headerBg: 'bg-indigo-50', badgeBg: 'bg-indigo-100 text-indigo-800 border-indigo-200', text: 'text-indigo-900' },
                    Chemistry: { border: 'border-emerald-200', headerBg: 'bg-emerald-50', badgeBg: 'bg-emerald-100 text-emerald-800 border-emerald-200', text: 'text-emerald-900' },
                    Maths: { border: 'border-amber-200', headerBg: 'bg-amber-50', badgeBg: 'bg-amber-100 text-amber-800 border-amber-200', text: 'text-amber-900' }
                  };
                  const style = themeStyles[subj] || { border: 'border-cyan-200', headerBg: 'bg-cyan-50', badgeBg: 'bg-cyan-100 text-cyan-800 border-cyan-200', text: 'text-cyan-900' };

                  return (
                    <div key={subj} className={`border ${style.border} rounded-xl p-3 bg-white shadow-xs flex flex-col justify-between space-y-2`}>
                      <div>
                        <div className={`flex items-center justify-between px-2.5 py-1 ${style.headerBg} rounded-md mb-2`}>
                          <span className={`font-semibold text-xs ${style.text}`}>{subj}</span>
                          <span className="text-[10px] font-medium text-gray-500">{selectedSubjDone.length} done</span>
                        </div>
                        <select
                          value=""
                          onChange={(e) => {
                            const val = e.target.value;
                            if (val && !topicsAlreadyDone.includes(val)) {
                              setTopicsAlreadyDone(prev => [...prev, val]);
                            }
                          }}
                          className="w-full px-2.5 py-1.5 text-xs border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
                        >
                          <option value="" disabled>-- Select Done {subj} Topic --</option>
                          {unselectedTopics.map((t) => (
                            <option key={t} value={t}>{formatTopicTitle(t)}</option>
                          ))}
                        </select>
                      </div>

                      {/* Selected Done Chips */}
                      {selectedSubjDone.length > 0 && (
                        <div className="pt-1.5 border-t border-gray-100 flex flex-wrap gap-1 max-h-28 overflow-y-auto">
                          {selectedSubjDone.map((t) => (
                            <div key={t} className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium border ${style.badgeBg}`} title={t}>
                              <span className="truncate max-w-[110px]">{formatTopicTitle(t)}</span>
                              <button
                                type="button"
                                onClick={() => setTopicsAlreadyDone(topicsAlreadyDone.filter(item => item !== t))}
                                className="p-0.5 hover:bg-black/10 rounded-full"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-xs text-gray-400">Loading syllabus topics...</p>
            )}
          </div>

          {/* FIELD 3: Exam Date */}
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1.5">
              3. Exam Date
            </label>
            <input
              type="date"
              value={examDate}
              min={today()}
              onChange={e => setExamDate(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-800 font-medium"
              required
            />
          </div>

          {/* FIELD 4 & 5: Daily Study Hours & Days Per Week */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-1.5">
                4. Daily Study Hours
              </label>
              <input
                type="number"
                min={1} max={16} step={0.5}
                value={dailyHours}
                onChange={e => setDailyHours(parseFloat(e.target.value) || 1)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-800 font-medium"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-1.5">
                5. Days Per Week Available
              </label>
              <select
                value={daysPerWeek}
                onChange={e => setDaysPerWeek(parseInt(e.target.value))}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium text-gray-800"
              >
                <option value={7}>7 Days / week (No rest day)</option>
                <option value={6}>6 Days / week (1 rest day)</option>
                <option value={5}>5 Days / week (2 rest days)</option>
                <option value={4}>4 Days / week</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold text-lg disabled:opacity-60 disabled:cursor-not-allowed hover:shadow-lg transition-all shadow-md mt-4"
          >
            {loading ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Generating AI Schedule…</>
            ) : (
              <><Plus className="w-5 h-5" /> Generate My Plan</>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

// ─── Main Study Plan Page Component ─────────────────────────────

interface StudyPlanPageProps {
  token: string;
  onPlanUpdated?: (plan?: StudyPlan | null) => void;
}

const StudyPlanPage: React.FC<StudyPlanPageProps> = ({ token, onPlanUpdated }) => {
  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [progress, setProgress] = useState<SubjectProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [updatingTaskId, setUpdatingTaskId] = useState<number | null>(null);

  // Calendar navigation
  const [viewMonth, setViewMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<string>(today());
  const [activeTab, setActiveTab] = useState<'calendar' | 'today' | 'progress' | 'leftout'>('today');

  const authHeaders = { Authorization: `Bearer ${token}` };

  // Fetch active plan
  const fetchPlan = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/study-plan/active`, { headers: authHeaders });
      if (res.status === 404) {
        setPlan(null);
        onPlanUpdated?.(null);
        return;
      }
      if (!res.ok) throw new Error(await res.text());
      const data: StudyPlan = await res.json();
      setPlan(data);
      onPlanUpdated?.(data);
    } catch (e: any) {
      setError(e.message ?? 'Failed to load plan');
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Fetch progress
  const fetchProgress = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/study-plan/progress`, { headers: authHeaders });
      if (res.ok) setProgress(await res.json());
    } catch { /* silent */ }
  }, [token]);

  useEffect(() => {
    fetchPlan();
    fetchProgress();
  }, [fetchPlan, fetchProgress]);

  // Generate plan
  const handleGenerate = async (req: StudyPlanCreateRequest) => {
    setGenerating(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/study-plan/generate`, {
        method: 'POST',
        headers: { ...authHeaders, 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? 'Generation failed');
      }
      const data: StudyPlan = await res.json();
      setPlan(data);
      onPlanUpdated?.(data);
      fetchProgress();
      setActiveTab('today');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setGenerating(false);
    }
  };

  // Update task status
  const handleTaskStatus = async (taskId: number, status: TaskStatus) => {
    if (!plan) return;
    setUpdatingTaskId(taskId);
    try {
      const res = await fetch(`${API_BASE_URL}/api/study-plan/task/${taskId}`, {
        method: 'PATCH',
        headers: { ...authHeaders, 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error('Update failed');
      const updatedTask: DailyTask = await res.json();
      setPlan(prev => {
        if (!prev) return prev;
        const newPlan = {
          ...prev,
          tasks: prev.tasks.map(t => t.id === taskId ? updatedTask : t),
        };
        onPlanUpdated?.(newPlan);
        return newPlan;
      });
      fetchProgress();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUpdatingTaskId(null);
    }
  };

  // Regenerate
  const handleRegenerate = async (forceFullRegen: boolean) => {
    if (!window.confirm(forceFullRegen
      ? 'This will archive your current plan and create a new one from scratch. Continue?'
      : 'Redistribute overdue tasks to future days?')) return;
    setRegenerating(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/study-plan/regenerate`, {
        method: 'POST',
        headers: { ...authHeaders, 'Content-Type': 'application/json' },
        body: JSON.stringify({ force_full: forceFullRegen }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? 'Regeneration failed');
      }
      const data: StudyPlan = await res.json();
      setPlan(data);
      onPlanUpdated?.(data);
      fetchProgress();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setRegenerating(false);
    }
  };

  const tasksByDate = plan ? groupTasksByDate(plan.tasks) : {};
  const todayStr = today();
  const todayTasks = tasksByDate[todayStr] ?? [];
  const selectedTasks = tasksByDate[selectedDate] ?? [];

  const overallDone = plan?.tasks.filter(t => t.status === 'done').length ?? 0;
  const overallTotal = plan?.tasks.length ?? 0;
  const progressPct = overallTotal > 0 ? Math.round((overallDone / overallTotal) * 100) : 0;

  const calDays = (() => {
    const year = viewMonth.getFullYear();
    const month = viewMonth.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const cells: (null | string)[] = Array(firstDay).fill(null);
    for (let d = 1; d <= daysInMonth; d++) {
      const mm = String(month + 1).padStart(2, '0');
      const dd = String(d).padStart(2, '0');
      cells.push(`${year}-${mm}-${dd}`);
    }
    return cells;
  })();

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-gray-500 font-medium">Loading your study plan…</p>
      </div>
    );
  }

  if (!plan) {
    return (
      <>
        {error && (
          <div className="mx-4 mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" /> {error}
          </div>
        )}
        <GenerateForm onGenerate={handleGenerate} loading={generating} token={token} />
      </>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-indigo-500" />
            Study Plan ({plan.exam_name})
          </h2>
          <p className="text-sm text-gray-500 mt-0.5">
            Target Exam Date: {new Date(plan.target_exam_date + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleRegenerate(false)}
            disabled={regenerating}
            title="Redistribute overdue tasks"
            className="flex items-center gap-1.5 px-3 py-2 text-sm bg-amber-50 text-amber-700 border border-amber-200 rounded-xl hover:bg-amber-100 transition-colors disabled:opacity-50 font-medium"
          >
            <RefreshCw className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
            Rebalance
          </button>
          <button
            onClick={() => handleRegenerate(true)}
            disabled={regenerating}
            title="Full AI regeneration"
            className="flex items-center gap-1.5 px-3 py-2 text-sm bg-red-50 text-red-700 border border-red-200 rounded-xl hover:bg-red-100 transition-colors disabled:opacity-50 font-medium"
          >
            <RotateCcw className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
            Full Regen
          </button>
        </div>
      </div>

      {/* Excluded Topics Alert (if any were skipped due to time constraints) */}
      {plan.excluded_topics && plan.excluded_topics.length > 0 && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl shadow-xs">
          <div className="flex items-start gap-2.5">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-amber-900">
                {plan.excluded_topics.length} lower-priority topic(s) were excluded from this schedule
              </h4>
              <p className="text-xs text-amber-800 mt-0.5">
                Due to limited time budget before your exam date, the highest-weightage topics were prioritized.
              </p>
              <details className="mt-2 text-xs">
                <summary className="cursor-pointer text-amber-900 font-semibold hover:underline">
                  View excluded topics ({plan.excluded_topics.length})
                </summary>
                <div className="mt-2 space-y-1 max-h-36 overflow-y-auto pr-1">
                  {plan.excluded_topics.map((t, idx) => (
                    <div key={idx} className="flex items-center justify-between px-2.5 py-1 bg-amber-100/60 rounded text-amber-900">
                      <span className="font-medium">{t.subject}: {formatTopicTitle(t.topic)}</span>
                      <span className="text-[10px] text-amber-700 font-normal">{t.reason}</span>
                    </div>
                  ))}
                </div>
              </details>
            </div>
          </div>
        </div>
      )}

      {/* Overall progress bar */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-gray-700">Overall Progress</span>
          <span className="text-sm font-bold text-indigo-600">{overallDone}/{overallTotal} tasks · {progressPct}%</span>
        </div>
        <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-700"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex gap-2">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" /> {error}
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-gray-200 gap-4 overflow-x-auto">
        {(['today', 'calendar', 'progress', 'leftout'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 text-sm font-semibold capitalize border-b-2 transition-colors shrink-0 ${
              activeTab === tab
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'today' && <span className="flex items-center gap-1.5"><Flame className="w-4 h-4" />Today</span>}
            {tab === 'calendar' && <span className="flex items-center gap-1.5"><Calendar className="w-4 h-4" />Calendar</span>}
            {tab === 'progress' && <span className="flex items-center gap-1.5"><Target className="w-4 h-4" />Progress</span>}
            {tab === 'leftout' && (
              <span className="flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                Left-out Topics ({plan.excluded_topics?.length || 0})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* TODAY TAB */}
      {activeTab === 'today' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-800">
              Today — {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
            </h3>
            <span className="text-xs text-gray-500">
              {todayTasks.filter(t => t.status === 'done').length}/{todayTasks.length} done
            </span>
          </div>
          {todayTasks.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <CheckCircle2 className="w-10 h-10 mx-auto mb-2 text-green-300" />
              <p className="font-medium">No tasks scheduled for today!</p>
              <p className="text-sm mt-1">Enjoy the rest day or check the Calendar for upcoming tasks.</p>
            </div>
          ) : (
            todayTasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onStatusChange={handleTaskStatus}
                updating={updatingTaskId === task.id}
              />
            ))
          )}
        </div>
      )}

      {/* CALENDAR TAB */}
      {activeTab === 'calendar' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <button onClick={() => setViewMonth(prev => new Date(prev.getFullYear(), prev.getMonth() - 1))} className="p-2 hover:bg-gray-100 rounded-lg">
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <span className="font-semibold text-gray-800">
              {viewMonth.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}
            </span>
            <button onClick={() => setViewMonth(prev => new Date(prev.getFullYear(), prev.getMonth() + 1))} className="p-2 hover:bg-gray-100 rounded-lg">
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          <div className="grid grid-cols-7 text-center">
            {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(d => (
              <div key={d} className="py-1 text-xs font-semibold text-gray-400">{d}</div>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-1">
            {calDays.map((dateStr, i) => {
              if (!dateStr) return <div key={i} />;
              const dayTasks = tasksByDate[dateStr] ?? [];
              const doneCount = dayTasks.filter(t => t.status === 'done').length;
              const isToday = dateStr === todayStr;
              const isSelected = dateStr === selectedDate;
              const hasTasks = dayTasks.length > 0;
              const allDone = hasTasks && doneCount === dayTasks.length;
              const isExamDay = dateStr === plan.target_exam_date;

              return (
                <button
                  key={dateStr}
                  onClick={() => { setSelectedDate(dateStr); }}
                  className={`relative aspect-square rounded-xl flex flex-col items-center justify-center text-sm transition-all
                    ${isSelected ? 'ring-2 ring-indigo-500' : ''}
                    ${isExamDay ? 'bg-red-50 border-2 border-red-400 font-bold' : ''}
                    ${!isExamDay && isToday ? 'bg-indigo-500 text-white font-bold' : ''}
                    ${!isExamDay && !isToday && hasTasks ? 'bg-indigo-50 hover:bg-indigo-100' : ''}
                    ${!isExamDay && !isToday && !hasTasks ? 'text-gray-400 hover:bg-gray-50' : ''}
                    ${!isExamDay && allDone ? 'bg-green-50 text-green-700' : ''}
                  `}
                >
                  <span>{parseInt(dateStr.split('-')[2])}</span>
                  {isExamDay ? (
                    <span className="text-[9px] font-extrabold text-red-600 bg-red-100 px-1 py-0.5 rounded border border-red-200 leading-none mt-0.5 truncate max-w-full">
                      Exam Day
                    </span>
                  ) : hasTasks && (
                    <div className="flex gap-0.5 mt-0.5">
                      {Array(Math.min(dayTasks.length, 4)).fill(0).map((_, idx) => (
                        <div
                          key={idx}
                          className={`w-1 h-1 rounded-full ${
                            idx < doneCount ? 'bg-green-400' : isToday ? 'bg-white/60' : 'bg-indigo-400'
                          }`}
                        />
                      ))}
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {selectedDate && (
            <div className="mt-4 space-y-2">
              <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-indigo-500" />
                {isoToDisplay(selectedDate)}
                <span className="text-xs text-gray-400 font-normal ml-1">
                  {selectedTasks.filter(t => t.status === 'done').length}/{selectedTasks.length} done
                </span>
              </h3>
              {selectedTasks.length === 0 ? (
                <p className="text-sm text-gray-400 py-4 text-center">No tasks on this day.</p>
              ) : (
                selectedTasks.map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onStatusChange={handleTaskStatus}
                    updating={updatingTaskId === task.id}
                  />
                ))
              )}
            </div>
          )}
        </div>
      )}

      {/* PROGRESS TAB */}
      {activeTab === 'progress' && (
        <div className="space-y-3">
          {progress.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-8">No progress data yet. Start completing tasks!</p>
          ) : (
            progress.map(p => {
              const pct = p.tasks_total > 0 ? Math.round((p.tasks_completed / p.tasks_total) * 100) : 0;
              return (
                <div key={p.subject} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${getSubjectColor(p.subject)}`}>
                        {p.subject}
                      </span>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${masteryColor[p.mastery_level]}`}>
                        {masteryIcon[p.mastery_level]} {p.mastery_level}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {p.tasks_completed}/{p.tasks_total} tasks · {pct}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${
                        p.mastery_level === 'strong' ? 'bg-green-400' :
                        p.mastery_level === 'moderate' ? 'bg-amber-400' : 'bg-red-400'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* LEFT-OUT TOPICS TAB */}
      {activeTab === 'leftout' && (
        <div className="space-y-4">
          <div className="bg-amber-50/70 border border-amber-200 p-4 rounded-2xl">
            <h3 className="font-bold text-amber-900 text-base flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              Left-Out Topics ({plan.excluded_topics?.length || 0})
            </h3>
            <p className="text-xs text-amber-800 mt-1">
              These topics could not fit in your schedule before target exam date ({plan.target_exam_date}). Higher-weightage topics were prioritized first within your time budget.
            </p>
          </div>

          {!plan.excluded_topics || plan.excluded_topics.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-2xl border border-gray-100 shadow-xs text-gray-400">
              <CheckCircle2 className="w-10 h-10 mx-auto mb-2 text-green-500" />
              <p className="font-semibold text-gray-700">All Syllabus Topics Are Covered!</p>
              <p className="text-sm mt-1">Your study plan includes every single topic from your syllabus without exclusions.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {plan.excluded_topics.map((t, idx) => (
                <div key={idx} className="bg-white rounded-xl border border-gray-200 p-3.5 shadow-xs flex flex-col justify-between space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${getSubjectColor(t.subject)}`}>
                      {t.subject}
                    </span>
                    <span className="text-[11px] font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-200">
                      Excluded
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-gray-800">
                    {formatTopicTitle(t.topic)}
                  </p>
                  <p className="text-xs text-gray-500">
                    {t.reason}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StudyPlanPage;
