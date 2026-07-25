import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import {
  Home,
  FileText,
  BookOpen,
  Flame,
  CheckCircle2,
  Calendar,
  Clock,
  Target,
  LogOut,
  User,
  Plus,
  Settings,
  Download,
  Loader2,
  AlertCircle,
  CheckCircle,
  X,
  ChevronLeft,
  ChevronRight,
  BookMarked // <-- NEW ICON
} from 'lucide-react';
import { SyllabusPage } from './SyllabusPage'; // <-- IMPORT NEW PAGE
import StudyPlanPage from './StudyPlanPage'; // <-- STUDY PLANNER

// --- INTERFACES ---
interface User {
  id: number;
  email: string;
  token?: string;
}

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

interface QuestionType {
  name: string;
  description: string;
}

// --- MODIFIED: Added syllabus_id ---
interface QuestionGenerationRequest {
  question_plan: { [key: string]: number };
  testing_mode: boolean;
  exam_name: string;
  output_format: 'pdf' | 'docx';
  questions_per_chunk: number;
  syllabus_id: number; // <-- ADDED
}

// --- NEW INTERFACE ---
interface Syllabus {
  id: number;
  name: string;
  created_at: string;
  topic_count: number;
}

// --- HELPER FUNCTIONS ---
const formatFilenameForDisplay = (filename: string): string => {
  if (filename.toLowerCase().includes('questions')) return 'Questions';
  if (filename.toLowerCase().includes('verifications')) return 'Verifications';
  if (filename.toLowerCase().includes('skipped')) return 'Skipped';
  return 'Download File';
};

const handleFileDownload = async (filename: string) => {
  if (filename.startsWith('http://') || filename.startsWith('https://')) {
    window.open(filename, '_blank');
  } else {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/download-questions/${filename}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading file:', err);
      alert('Failed to download file.');
    }
  }
};

const numQuestionsChunk = 3;
// const numQuestionsChunk = 5;

// --- MAIN COMPONENT ---
const Dashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  // --- STATE MANAGEMENT ---
  const [activeTab, setActiveTab] = useState<'mockTest' | 'studyPlan'>('mockTest');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [onboardingData, setOnboardingData] = useState<any>(null);

  // --- NEW: View routing state ---
  const [currentView, setCurrentView] = useState<'dashboard' | 'syllabus'>('dashboard');

  // Generator State
  const [questionTypes, setQuestionTypes] = useState<QuestionType[]>([]);
  const [questionPlan, setQuestionPlan] = useState<{ [key: string]: number }>({});
  const [testingMode, setTestingMode] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [outputFormat, setOutputFormat] = useState<'pdf' | 'docx'>('pdf');
  const [generationResult, setGenerationResult] = useState<{
    success: boolean;
    message: string;
    files?: { [key: string]: string };
  } | null>(null);

  // --- NEW: Syllabus state ---
  const [syllabuses, setSyllabuses] = useState<Syllabus[]>([]);
  const [selectedSyllabusId, setSelectedSyllabusId] = useState<number | null>(null);
  const [isSyllabusLoading, setIsSyllabusLoading] = useState(true);

  // --- NEW: Syllabus subjects state ---
  const [availableSubjects, setAvailableSubjects] = useState<string[]>([]);
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);

  // Calendar State
  const [currentDate, setCurrentDate] = useState(new Date());

  // --- EFFECTS ---
  useEffect(() => {
    loadQuestionTypes();
    loadOnboardingData();
    fetchSyllabuses(); // <-- Load syllabuses on init
    fetchSyllabusSubjects();
  }, []);

  const fetchSyllabusSubjects = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/syllabus-subjects`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const subjects = await response.json();
        setAvailableSubjects(subjects);
      }
    } catch (error) {
      console.error('Error fetching syllabus subjects:', error);
    }
  };

  // --- API CALLS ---
  const fetchSyllabuses = async () => {
    setIsSyllabusLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/syllabus`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch');

      const data: Syllabus[] = await response.json();
      setSyllabuses(data);

      if (data.length > 0) {
        // Default to the first syllabus in the list
        setSelectedSyllabusId(data[0].id);
        // If we have syllabuses, stay on dashboard
        setCurrentView('dashboard');
      } else {
        // --- GOAL 1: If no syllabus, force user to upload one ---
        setCurrentView('syllabus');
      }
    } catch (error) {
      console.error('Error fetching syllabuses:', error);
    } finally {
      setIsSyllabusLoading(false);
    }
  };

  const loadOnboardingData = async () => {
    // ... (this function is unchanged)
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/api/onboarding`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        const formattedData = {
          examName: data.exam_name,
          examDate: data.exam_date,
          topicsCovered: data.topics_covered || [],
          studyHours: data.daily_study_hours?.toString() || '',
          studyDays: data.additional_notes?.includes('Study Days per Week:')
            ? data.additional_notes.split('Study Days per Week: ')[1]
            : '',
          currentPreparationLevel: data.current_preparation_level,
          preferredStudyTime: data.preferred_study_time,
          weakSubjects: data.weak_subjects || [],
          strongSubjects: data.strong_subjects || []
        };
        setOnboardingData(formattedData);
        localStorage.setItem('onboarding_data', JSON.stringify(formattedData));
      } else if (response.status !== 404) {
        console.error('Failed to load onboarding data:', response.status);
      }
    } catch (error) {
      console.error('Error loading onboarding data:', error);
      const savedOnboardingData = localStorage.getItem('onboarding_data');
      if (savedOnboardingData) {
        try {
          setOnboardingData(JSON.parse(savedOnboardingData));
        } catch (parseError) {
          console.error('Error parsing saved onboarding data:', parseError);
        }
      }
    }
  };

  const loadQuestionTypes = async () => {
    // ... (this function is unchanged)
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/question-types`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const types = await response.json();
        setQuestionTypes(types);
      } else {
        console.error('Failed to load question types');
      }
    } catch (error) {
      console.error('Error loading question types:', error);
    }
  };

  const generateQuestions = async () => {
    // --- MODIFIED: Check for syllabus ---
    if (!selectedSyllabusId) {
      setGenerationResult({ success: false, message: 'Please select a syllabus first. Go to Syllabus Settings to upload one.' });
      return;
    }

    const totalQuestions = Object.values(questionPlan).reduce((sum, count) => sum + count, 0);
    if (totalQuestions === 0) {
      setGenerationResult({ success: false, message: 'Please select at least one question type.' });
      return;
    }

    const invalidCounts = Object.entries(questionPlan).filter(([_, count]) => count > 0 && count % numQuestionsChunk !== 0);
    if (invalidCounts.length > 0) {
      setGenerationResult({ success: false, message: `All question counts must be multiples of ${numQuestionsChunk}.` });
      return;
    }

    setIsGenerating(true);
    setGenerationResult(null);

    try {
      const token = localStorage.getItem('access_token');
      const examName = onboardingData?.examName || 'General Exam';

      const request: QuestionGenerationRequest = {
        question_plan: Object.fromEntries(Object.entries(questionPlan).filter(([_, count]) => count > 0)),
        testing_mode: testingMode,
        exam_name: examName,
        output_format: outputFormat,
        questions_per_chunk: numQuestionsChunk,
        syllabus_id: selectedSyllabusId, // <-- PASS THE ID
        subjects: selectedSubjects.length > 0 ? selectedSubjects : undefined
      };

      const response = await fetch(`${API_BASE_URL}/api/generate-questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(request)
      });

      const result = await response.json();
      if (response.status === 403) {
        setGenerationResult({
          success: false,
          message: result.detail // This will show your custom "Access Denied" message
        });
        return;
      }
      if (!response.ok) {
        setGenerationResult({ success: false, message: result.detail || 'An unknown server error occurred.' });
      } else {
        setGenerationResult(result);
      }
    } catch (error) {
      setGenerationResult({ success: false, message: `An unexpected error occurred: ${error}` });
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadFile = async (filename: string) => {
    // ... (this function is unchanged)
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/download-questions/${filename}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Failed to download file.');
      }
    } catch (error) {
      alert('An error occurred while downloading the file.');
    }
  };

  // --- EVENT HANDLERS ---
  const handleQuestionCountChange = (questionType: string, count: string) => {
    // ... (this function is unchanged)
    const numCount = parseInt(count) || 0;
    setQuestionPlan(prev => ({ ...prev, [questionType]: numCount }));
  };

  // --- UI HELPER DATA & FUNCTIONS ---
  // ... (getDaysUntilExam, getUserDisplayName remain unchanged) ...
  const getDaysUntilExam = () => {
    if (!onboardingData?.examDate) return null;
    const diffTime = new Date(onboardingData.examDate).getTime() - new Date().getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };
  const daysUntilExam = getDaysUntilExam();
  const getUserDisplayName = () => user?.email?.split('@')[0] || 'User';

  // --- MOCK DATA & CALENDAR LOGIC ---
  // ... (studyTasks, streakDaysData, getDaysInMonth, etc. remain unchanged) ...
  const studyTasks = {
    '2025-08-22': [{ task: 'Revise Math', duration: '2h', type: 'revision' }, { task: 'Practice PYQs', duration: '1h', type: 'practice' }],
    '2025-08-23': [{ task: 'Physics Chapter 3', duration: '3h', type: 'study' }, { task: 'Mock Test', duration: '2h', type: 'test' }],
    '2025-09-02': [{ task: 'Chemistry Ch. 1', duration: '2h', type: 'study' }],
  };
  const streakDaysData = ['2025-08-24', '2025-08-25', '2025-08-26', '2025-08-27', '2025-08-28'];

  const getDaysInMonth = (date: Date) => new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  const getFirstDayOfMonth = (date: Date) => new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  const formatDateKey = (year: number, month: number, day: number) => `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  const getTaskTypeColor = (type: string) => {
    switch (type) {
      case 'study': return 'bg-cyan-100 text-cyan-700 border-cyan-200';
      case 'practice': return 'bg-pink-100 text-pink-700 border-pink-200';
      case 'revision': return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'test': return 'bg-amber-100 text-amber-700 border-amber-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const renderStudyPlanCalendar = () => {
    // ... (this function is unchanged) ...
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);
    const days = [];
    const today = new Date();
    const isCurrentMonth = currentDate.getMonth() === today.getMonth() && currentDate.getFullYear() === today.getFullYear();

    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="h-28 border-t border-r border-gray-100"></div>);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const dateKey = formatDateKey(currentDate.getFullYear(), currentDate.getMonth(), day);
      const dayTasks = studyTasks[dateKey] || [];
      const isToday = isCurrentMonth && day === today.getDate();

      days.push(
        <div key={day} className={`h-28 border-t border-r border-gray-100 p-1.5 ${isToday ? 'bg-cyan-50' : 'bg-white'}`}>
          <div className={`text-sm font-medium ${isToday ? 'text-cyan-700' : 'text-gray-700'}`}>{day}</div>
          <div className="space-y-1 mt-1">
            {dayTasks.slice(0, 2).map((task, index) => (
              <div key={index} className={`text-xs px-1.5 py-0.5 rounded border ${getTaskTypeColor(task.type)} truncate`}>
                {task.task}
              </div>
            ))}
            {dayTasks.length > 2 && <div className="text-xs text-gray-500">+{dayTasks.length - 2} more</div>}
          </div>
        </div>
      );
    }
    return days;
  };

  const renderStreakCalendar = () => {
    // ... (this function is unchanged) ...
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);
    const days = [];
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`streak-empty-${i}`} className="h-8 w-8"></div>);
    }
    for (let day = 1; day <= daysInMonth; day++) {
      const dateKey = formatDateKey(currentDate.getFullYear(), currentDate.getMonth(), day);
      const hasStreak = streakDaysData.includes(dateKey);
      days.push(
        <div key={day} className="h-8 w-8 flex items-center justify-center text-xs relative">
          <span className={`relative z-10 ${hasStreak ? 'text-white font-semibold' : 'text-gray-600'}`}>{day}</span>
          {hasStreak && <div className="absolute inset-0 bg-gradient-to-r from-pink-600 to-cyan-300 rounded-full"></div>}
        </div>
      );
    }
    return days;
  };

  // --- RENDER LOGIC ---
  if (!user) {
    return <div className="min-h-screen flex items-center justify-center bg-gray-50"><Loader2 className="w-12 h-12 text-cyan-600 animate-spin" /></div>;
  }

  // --- Main Render Function ---
  return (
    <div className="min-h-screen bg-gray-50">
      {/* --- HEADER --- */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-lg flex items-center justify-center">
                <Target className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">AceTrack</h1>
            </div>

            {/* Exam Info */}
            {currentView === 'dashboard' && onboardingData?.examName && daysUntilExam !== null && (
              <div className="hidden md:flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-cyan-50 to-purple-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-cyan-600" />
                  <span className="font-semibold text-gray-800">{onboardingData.examName}</span>
                </div>
                <div className="w-px h-6 bg-gray-300"></div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-red-500" />
                  <span className="text-sm font-medium text-gray-700">{daysUntilExam} days left</span>
                </div>
              </div>
            )}

            {/* Navigation */}
            <div className="flex items-center gap-1">
              {/* --- MODIFIED: Hide tabs if on syllabus page --- */}
              {currentView === 'dashboard' && (
                <nav className="hidden md:flex items-center space-x-1">
                  <button onClick={() => setActiveTab('mockTest')} className={`flex items-center gap-2 px-3 py-2 rounded-lg font-medium ${activeTab === 'mockTest' ? 'bg-cyan-100 text-cyan-700' : 'text-gray-600 hover:bg-gray-100'}`}>
                    <FileText className="w-4 h-4" /> Mock Tests
                  </button>
                  <button onClick={() => setActiveTab('studyPlan')} className={`flex items-center gap-2 px-3 py-2 rounded-lg font-medium ${activeTab === 'studyPlan' ? 'bg-purple-100 text-purple-700' : 'text-gray-600 hover:bg-gray-100'}`}>
                    <Calendar className="w-4 h-4" /> Study Plan
                  </button>
                  <a href="#" className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100">
                    <BookOpen className="w-4 h-4" /> PYQs
                  </a>
                </nav>
              )}

              {/* --- NEW: Syllabus Settings Button --- */}
              <button
                onClick={() => setCurrentView(currentView === 'dashboard' ? 'syllabus' : 'dashboard')}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg font-medium ${currentView === 'syllabus' ? 'bg-purple-100 text-purple-700' : 'text-gray-600 hover:bg-gray-100'}`}
                title="Syllabus Settings"
              >
                <BookMarked className="w-4 h-4" />
                <span className="hidden md:inline">Syllabus</span>
              </button>

              {/* User Menu */}
              <div className="relative">
                <button onClick={() => setShowUserMenu(!showUserMenu)} className="flex items-center gap-2 p-2 rounded-full hover:bg-gray-100">
                  <User className="w-5 h-5 text-gray-600" />
                </button>
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    <div className="px-4 py-2 border-b">
                      <p className="text-sm font-medium text-gray-900">{getUserDisplayName()}</p>
                      <p className="text-xs text-gray-500 truncate">{user.email}</p>
                    </div>
                    <button onClick={onLogout} className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50">
                      <LogOut className="w-4 h-4" /> Logout
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Exam Info */}
        {currentView === 'dashboard' && onboardingData?.examName && daysUntilExam !== null && (
          <div className="md:hidden px-4 pb-3">
            {/* ... (this section is unchanged) ... */}
            <div className="flex items-center justify-center gap-3 px-4 py-2 bg-gradient-to-r from-cyan-50 to-purple-50 rounded-lg border border-gray-200">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-cyan-600" />
                <span className="font-semibold text-gray-800 text-sm">{onboardingData.examName}</span>
              </div>
              <div className="w-px h-4 bg-gray-300"></div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-red-500" />
                <span className="text-sm font-medium text-gray-700">{daysUntilExam} days left</span>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* --- MAIN CONTENT: Conditional Rendering --- */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'syllabus' ? (
          <SyllabusPage
            API_BASE_URL={API_BASE_URL}
            onBack={() => setCurrentView('dashboard')}
            onSyllabusUploaded={fetchSyllabuses} // Pass the refresh function
          />
        ) : (
          /* --- Dashboard View --- */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              {activeTab === 'mockTest' && (
                <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
                  <div className="flex items-center gap-4 mb-4">
                    <FileText className="w-8 h-8 text-cyan-600" />
                    <div>
                      <h2 className="text-2xl font-bold text-gray-800">Create a New Mock Test</h2>
                      <p className="text-gray-600">Generate a personalized test based on your syllabus.</p>
                    </div>
                  </div>

                  {/* --- NEW: Syllabus Selector --- */}
                  <div className="my-6">
                    <label htmlFor="syllabus-select" className="block text-sm font-medium text-gray-700 mb-1">
                      1. Select Syllabus
                    </label>
                    {isSyllabusLoading ? (
                      <div className="w-full p-3 bg-gray-100 rounded-lg animate-pulse">Loading syllabuses...</div>
                    ) : syllabuses.length === 0 ? (
                      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800">
                        <p className="font-medium">No syllabus found.</p>
                        <p className="text-sm">Please go to <button onClick={() => setCurrentView('syllabus')} className="font-bold underline">Syllabus Settings</button> to upload one first.</p>
                      </div>
                    ) : (
                      <select
                        id="syllabus-select"
                        value={selectedSyllabusId || ''}
                        onChange={(e) => setSelectedSyllabusId(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white"
                      >
                        <option value="" disabled>-- Select a syllabus --</option>
                        {syllabuses.map(s => (
                          <option key={s.id} value={s.id}>
                            {s.name} ({s.topic_count} topics)
                          </option>
                        ))}
                      </select>
                    )}
                  </div>

                  {/* --- NEW: Subject Selector --- */}
                  {availableSubjects.length > 0 && (
                    <div className="my-6">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Filter by Subjects (Optional)
                      </label>
                      <div className="flex flex-wrap gap-3">
                        {availableSubjects.map((subj) => (
                          <label key={subj} className="flex items-center gap-2 px-3 py-2 border rounded-lg cursor-pointer hover:bg-gray-50">
                            <input 
                              type="checkbox" 
                              checked={selectedSubjects.includes(subj)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedSubjects([...selectedSubjects, subj]);
                                } else {
                                  setSelectedSubjects(selectedSubjects.filter(s => s !== subj));
                                }
                              }}
                              className="w-4 h-4 text-cyan-600 rounded"
                            />
                            <span className="text-sm font-medium text-gray-800">{subj}</span>
                          </label>
                        ))}
                      </div>
                      <p className="text-xs text-gray-500 mt-2">If none selected, it uses all subjects in your syllabus.</p>
                    </div>
                  )}

                  {/* --- Other Options --- */}
                  <div className="my-6 space-y-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      2. Other Options
                    </label>
                    <label className="flex items-center gap-3 p-4 border-2 border-dashed border-gray-200 rounded-lg hover:border-cyan-400 transition-colors cursor-pointer">
                      {/* ... (Testing Mode checkbox is unchanged) ... */}
                      <input type="checkbox" checked={testingMode} onChange={(e) => setTestingMode(e.target.checked)} className="w-4 h-4 text-cyan-600 border-gray-300 rounded focus:ring-cyan-500" />
                      <div>
                        <h4 className="font-medium text-gray-800">Testing Mode</h4>
                        <p className="text-sm text-gray-600">Generate sample questions for testing (faster, uses mock data).</p>
                      </div>
                    </label>
                    <div className="p-4 border-2 border-dashed border-gray-200 rounded-lg">
                      {/* ... (Output Format radio is unchanged) ... */}
                      <h4 className="font-medium text-gray-800 mb-2">Output Format</h4>
                      <div className="flex gap-4">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input type="radio" name="outputFormat" value="pdf" checked={outputFormat === 'pdf'} onChange={() => setOutputFormat('pdf')} className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500" />
                          <span className="text-sm text-gray-700">PDF</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input type="radio" name="outputFormat" value="docx" checked={outputFormat === 'docx'} onChange={() => setOutputFormat('docx')} className="w-4 h-4 text-purple-600 border-gray-300 focus:ring-purple-500" />
                          <span className="text-sm text-gray-700">DOCX</span>
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* --- Question Plan --- */}
                  <div className="space-y-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      3. Select Question Counts
                    </label>
                    {questionTypes.length > 0 ? questionTypes.map((qtype) => (
                      <div key={qtype.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-800">{qtype.name}</h4>
                          <p className="text-sm text-gray-600">{qtype.description}</p>
                        </div>
                        <input type="number" min="0" step={numQuestionsChunk} placeholder="0" value={questionPlan[qtype.name] || ''} onChange={(e) => handleQuestionCountChange(qtype.name, e.target.value)} className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-center" />
                      </div>
                    )) : (
                      <div className="text-center py-8"><Loader2 className="w-6 h-6 text-gray-400 animate-spin mx-auto" /><p className="mt-2 text-gray-500">Loading...</p></div>
                    )}
                  </div>

                  {/* --- Generation Button & Results --- */}
                  <div className="mt-6 border-t pt-6 space-y-4">
                    {generationResult && (
                      <div className={`p-4 rounded-lg border ${generationResult.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                        {/* ... (result display is unchanged) ... */}
                        <div className="flex items-start gap-3">
                          {generationResult.success ? <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" /> : <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />}
                          <div>
                            <span className={`font-semibold ${generationResult.success ? 'text-green-800' : 'text-red-800'}`}>
                              {generationResult.success ? 'Generation Complete!' : 'Error'}
                            </span>
                            <p className={`text-sm ${generationResult.success ? 'text-green-700' : 'text-red-700'}`}>
                              {generationResult.message}
                            </p>
                            {generationResult.success && generationResult.files && (
                              <div className="mt-3 flex flex-wrap gap-2">
                                {Object.entries(generationResult.files).map(([key, filename]) => (
                                  <button key={key} onClick={() => handleFileDownload(filename)} className="flex items-center gap-2 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                                    <Download className="w-4 h-4" /> {formatFilenameForDisplay(filename)}
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                    <button
                      onClick={generateQuestions}
                      disabled={isGenerating || isSyllabusLoading || !selectedSyllabusId} // <-- MODIFIED disabled state
                      className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-lg font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isGenerating ? <><Loader2 className="w-6 h-6 animate-spin" /> Generating...</> : <><Plus className="w-6 h-6" /> Generate Test</>}
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'studyPlan' && (
                <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
                  <StudyPlanPage token={localStorage.getItem('access_token') || ''} />
                </div>
              )}
            </div>

            {/* --- RIGHT COLUMN: SIDEBAR WIDGETS --- */}
            <div className="space-y-6">
              {/* ... (Streak and Countdown widgets are unchanged) ... */}
              <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
                <div className="flex items-center gap-3 mb-4">
                  <Flame className="w-6 h-6 text-pink-500" />
                  <h3 className="text-lg font-bold text-gray-800">Study Streak</h3>
                </div>
                <div className="text-center mb-4">
                  <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-pink-300">
                    {streakDaysData.length}
                  </div>
                  <p className="text-sm text-gray-600">days in a row</p>
                </div>
                <div className="grid grid-cols-7 gap-1 mt-4">
                  {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map(day => (
                    <div key={day} className="text-center text-xs font-medium text-gray-500 mb-1">{day}</div>
                  ))}
                  {renderStreakCalendar()}
                </div>
              </div>

              {daysUntilExam !== null && (
                <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
                  <div className="flex items-center gap-3 mb-4">
                    <Clock className="w-6 h-6 text-red-500" />
                    <h3 className="text-lg font-bold text-gray-800">Countdown</h3>
                  </div>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-pink-300">
                      {daysUntilExam}
                    </div>
                    <p className="text-sm text-gray-600">days until {onboardingData?.examName || 'your exam'}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;