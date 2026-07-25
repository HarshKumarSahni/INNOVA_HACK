import React, { useState, useEffect, useCallback } from 'react';
import {
  Calendar, Plus, RefreshCw, CheckCircle2, Clock,
  AlertCircle, Loader2, ChevronLeft, ChevronRight,
  BookOpen, Flame, Target, SkipForward, RotateCcw
} from 'lucide-react';
import { API_BASE_URL } from '../config';
import type {
  StudyPlan, DailyTask, SubjectProgress,
  StudyPlanCreateRequest, TaskStatus, MasteryLevel
} from '../types/studyPlan';

// ─── helpers ────────────────────────────────────────────────

const SUBJECT_COLORS: Record<string, string> = {
  Physics: 'bg-blue-100 text-blue-800 border-blue-200',
  Chemistry: 'bg-green-100 text-green-800 border-green-200',
  Maths: 'bg-purple-100 text-purple-800 border-purple-200',
  Mathematics: 'bg-purple-100 text-purple-800 border-purple-200',
  Biology: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  History: 'bg-amber-100 text-amber-800 border-amber-200',
  Geography: 'bg-cyan-100 text-cyan-800 border-cyan-200',
  'General Studies': 'bg-orange-100 text-orange-800 border-orange-200',
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

// ─── sub-components ─────────────────────────────────────────

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

// ─── generate form ───────────────────────────────────────────

interface GenerateFormProps {
  onGenerate: (req: StudyPlanCreateRequest) => void;
  loading: boolean;
}

const GenerateForm: React.FC<GenerateFormProps> = ({ onGenerate, loading }) => {
  const [hours, setHours] = useState(4);
  const [weakInput, setWeakInput] = useState('');
  const [weakSubjects, setWeakSubjects] = useState<string[]>([]);

  const addWeak = () => {
    const trimmed = weakInput.trim();
    if (trimmed && !weakSubjects.includes(trimmed)) {
      setWeakSubjects(prev => [...prev, trimmed]);
    }
    setWeakInput('');
  };

  const removeWeak = (s: string) => setWeakSubjects(prev => prev.filter(x => x !== s));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate({ daily_available_hours: hours, weak_subjects: weakSubjects });
  };

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-indigo-100 p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl">
            <Calendar className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Generate Study Plan</h2>
            <p className="text-sm text-gray-500">AI will create your day-by-day schedule</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Daily hours */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Daily Study Hours
            </label>
            <input
              type="number"
              min={1} max={16} step={0.5}
              value={hours}
              onChange={e => setHours(parseFloat(e.target.value))}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
              required
            />
          </div>

          {/* Weak subjects */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Weak Subjects <span className="text-gray-400 font-normal">(optional — gets extra time)</span>
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={weakInput}
                onChange={e => setWeakInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addWeak())}
                placeholder="e.g. Organic Chemistry"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
              <button
                type="button"
                onClick={addWeak}
                className="px-3 py-2 bg-indigo-100 text-indigo-700 rounded-xl hover:bg-indigo-200 transition-colors"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            {weakSubjects.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {weakSubjects.map(s => (
                  <span key={s} className="inline-flex items-center gap-1 px-2.5 py-1 bg-red-50 text-red-700 text-xs rounded-full border border-red-200">
                    {s}
                    <button type="button" onClick={() => removeWeak(s)} className="hover:text-red-900">×</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800">
            <strong>Note:</strong> Generation uses your uploaded syllabus + your exam date from onboarding. Make sure both are set before generating.
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-semibold text-base disabled:opacity-60 disabled:cursor-not-allowed hover:opacity-90 transition-opacity"
          >
            {loading ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Generating with AI…</>
            ) : (
              <><Plus className="w-5 h-5" /> Generate My Plan</>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

// ─── main component ──────────────────────────────────────────

interface StudyPlanPageProps {
  token: string;
}

const StudyPlanPage: React.FC<StudyPlanPageProps> = ({ token }) => {
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
  const [activeTab, setActiveTab] = useState<'calendar' | 'today' | 'progress'>('today');

  const authHeaders = { Authorization: `Bearer ${token}` };

  // ── fetch active plan ──
  const fetchPlan = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/study-plan/active`, { headers: authHeaders });
      if (res.status === 404) { setPlan(null); return; }
      if (!res.ok) throw new Error(await res.text());
      const data: StudyPlan = await res.json();
      setPlan(data);
    } catch (e: any) {
      setError(e.message ?? 'Failed to load plan');
    } finally {
      setLoading(false);
    }
  }, [token]);

  // ── fetch progress ──
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

  // ── generate plan ──
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
      fetchProgress();
      setActiveTab('today');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setGenerating(false);
    }
  };

  // ── update task status ──
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
      setPlan(prev => prev ? {
        ...prev,
        tasks: prev.tasks.map(t => t.id === taskId ? updatedTask : t),
      } : prev);
      fetchProgress();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUpdatingTaskId(null);
    }
  };

  // ── regenerate ──
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
      fetchProgress();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setRegenerating(false);
    }
  };

  // ── derived data ──
  const tasksByDate = plan ? groupTasksByDate(plan.tasks) : {};
  const todayStr = today();
  const todayTasks = tasksByDate[todayStr] ?? [];
  const selectedTasks = tasksByDate[selectedDate] ?? [];

  const overallDone = plan?.tasks.filter(t => t.status === 'done').length ?? 0;
  const overallTotal = plan?.tasks.length ?? 0;
  const progressPct = overallTotal > 0 ? Math.round((overallDone / overallTotal) * 100) : 0;

  // Calendar days for current view month
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

  // ── loading / error states ──
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
        <GenerateForm onGenerate={handleGenerate} loading={generating} />
      </>
    );
  }

  return (
    <div className="space-y-6">
      {/* ── Header bar ── */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-indigo-500" />
            Study Plan
          </h2>
          <p className="text-sm text-gray-500 mt-0.5">
            {plan.exam_name} · Target: {new Date(plan.target_exam_date + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleRegenerate(false)}
            disabled={regenerating}
            title="Redistribute overdue tasks"
            className="flex items-center gap-1.5 px-3 py-2 text-sm bg-amber-50 text-amber-700 border border-amber-200 rounded-xl hover:bg-amber-100 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
            Rebalance
          </button>
          <button
            onClick={() => handleRegenerate(true)}
            disabled={regenerating}
            title="Full AI regeneration"
            className="flex items-center gap-1.5 px-3 py-2 text-sm bg-red-50 text-red-700 border border-red-200 rounded-xl hover:bg-red-100 transition-colors disabled:opacity-50"
          >
            <RotateCcw className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
            Full Regen
          </button>
        </div>
      </div>

      {/* ── Overall progress bar ── */}
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

      {/* ── Error banner ── */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex gap-2">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" /> {error}
        </div>
      )}

      {/* ── Tabs ── */}
      <div className="flex border-b border-gray-200 gap-4">
        {(['today', 'calendar', 'progress'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 text-sm font-semibold capitalize border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'today' && <span className="flex items-center gap-1.5"><Flame className="w-4 h-4" />Today</span>}
            {tab === 'calendar' && <span className="flex items-center gap-1.5"><Calendar className="w-4 h-4" />Calendar</span>}
            {tab === 'progress' && <span className="flex items-center gap-1.5"><Target className="w-4 h-4" />Progress</span>}
          </button>
        ))}
      </div>

      {/* ── TODAY TAB ── */}
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

      {/* ── CALENDAR TAB ── */}
      {activeTab === 'calendar' && (
        <div className="space-y-4">
          {/* Month nav */}
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

          {/* Day headers */}
          <div className="grid grid-cols-7 text-center">
            {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(d => (
              <div key={d} className="py-1 text-xs font-semibold text-gray-400">{d}</div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7 gap-1">
            {calDays.map((dateStr, i) => {
              if (!dateStr) return <div key={i} />;
              const dayTasks = tasksByDate[dateStr] ?? [];
              const doneCount = dayTasks.filter(t => t.status === 'done').length;
              const isToday = dateStr === todayStr;
              const isSelected = dateStr === selectedDate;
              const hasTasks = dayTasks.length > 0;
              const allDone = hasTasks && doneCount === dayTasks.length;

              return (
                <button
                  key={dateStr}
                  onClick={() => { setSelectedDate(dateStr); }}
                  className={`relative aspect-square rounded-xl flex flex-col items-center justify-center text-sm transition-all
                    ${isSelected ? 'ring-2 ring-indigo-500' : ''}
                    ${isToday ? 'bg-indigo-500 text-white font-bold' : ''}
                    ${!isToday && hasTasks ? 'bg-indigo-50 hover:bg-indigo-100' : ''}
                    ${!isToday && !hasTasks ? 'text-gray-400 hover:bg-gray-50' : ''}
                    ${allDone ? 'bg-green-50 text-green-700' : ''}
                  `}
                >
                  <span>{parseInt(dateStr.split('-')[2])}</span>
                  {hasTasks && (
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

          {/* Selected day tasks */}
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

      {/* ── PROGRESS TAB ── */}
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
    </div>
  );
};

export default StudyPlanPage;
