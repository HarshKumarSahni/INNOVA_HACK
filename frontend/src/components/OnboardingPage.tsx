import React, { useState } from 'react';
import { ChevronLeft, Calendar, Clock, BookOpen, Target, Sparkles } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface OnboardingData {
  examName: string;
  examDate: string;
  topicsCovered: string[];
  studyHours: string;
  studyDays: string;
}

interface OnboardingPageProps {
  onBack: () => void;
  onComplete: (data: OnboardingData) => void;
}

const OnboardingPage: React.FC<OnboardingPageProps> = ({ onBack, onComplete }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<OnboardingData>({
    examName: '',
    examDate: '',
    topicsCovered: [],
    studyHours: '',
    studyDays: '',
  });

  const exams = [
    'JEE (Joint Entrance Examination)',
    'UGC-NET (University Grants Commission - National Eligibility Test)',
    'NEET (National Eligibility cum Entrance Test)',
    'UPSC (Union Public Service Commission)',
    'GATE (Graduate Aptitude Test in Engineering)',
    'CAT (Common Admission Test)',
    'CLAT (Common Law Admission Test)',
    'NDA (National Defence Academy)',
    'SSC CGL (Staff Selection Commission)',
    'IBPS (Banking Exams)',
    'Other'
  ];

  const topics = [
    { category: 'Mathematics', items: ['Algebra', 'Calculus', 'Geometry', 'Statistics', 'Trigonometry'] },
    { category: 'Physics', items: ['Mechanics', 'Thermodynamics', 'Optics', 'Electromagnetism', 'Modern Physics'] },
    { category: 'Chemistry', items: ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry', 'Analytical Chemistry'] },
    { category: 'Biology', items: ['Cell Biology', 'Genetics', 'Ecology', 'Human Physiology', 'Plant Biology'] },
    { category: 'General Studies', items: ['History', 'Geography', 'Polity', 'Economics', 'Current Affairs'] },
  ];

  const submitOnboardingData = async (data: OnboardingData) => {
    const token = localStorage.getItem('access_token'); // Fixed: use 'access_token' consistently
    if (!token) {
      throw new Error('No authentication token found');
    }

    // Transform your form data to match the backend schema
    const backendData = {
      exam_name: data.examName,
      exam_date: data.examDate,
      current_preparation_level: 'intermediate', // Default value since you don't collect this
      daily_study_hours: parseInt(data.studyHours) || 4,
      preferred_study_time: 'morning', // Default value since you don't collect this
      topics_covered: data.topicsCovered,
      weak_subjects: [], // Empty array since you don't collect this
      strong_subjects: [], // Empty array since you don't collect this
      additional_notes: `Study Days per Week: ${data.studyDays}` // Store study days in notes
    };

    console.log('Sending onboarding data:', backendData); // Debug log

    const response = await fetch(`${API_BASE_URL}/api/onboarding`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` // Fixed: proper Bearer token format
      },
      body: JSON.stringify(backendData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Backend error:', errorData); // Debug log
      throw new Error(errorData.detail || 'Failed to save onboarding data');
    }

    return await response.json();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate form data
      if (!formData.examName || !formData.examDate || !formData.studyHours || !formData.studyDays) {
        throw new Error('Please fill in all required fields');
      }

      // Submit to backend
      const result = await submitOnboardingData(formData);
      console.log('Onboarding data saved successfully:', result);

      // Call the completion handler with form data
      onComplete(formData);
    } catch (error) {
      console.error('Error submitting onboarding:', error);
      setError(error instanceof Error ? error.message : 'An error occurred while saving your data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error when user starts changing form data
    if (error) setError(null);
  };

  const handleTopicToggle = (topic: string) => {
    setFormData(prev => ({
      ...prev,
      topicsCovered: prev.topicsCovered.includes(topic)
        ? prev.topicsCovered.filter(t => t !== topic)
        : [...prev.topicsCovered, topic]
    }));
    // Clear error when user starts changing form data
    if (error) setError(null);
  };

  const getMinDate = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const getDaysUntilExam = () => {
    if (!formData.examDate) return null;
    const today = new Date();
    const examDate = new Date(formData.examDate);
    const diffTime = examDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  const daysUntilExam = getDaysUntilExam();

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
            disabled={loading}
          >
            <ChevronLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span>Setup Your Profile</span>
            <div className="w-20 h-2 bg-gray-200 rounded-full">
              <div className="w-full h-full bg-gradient-to-r from-cyan-500 to-magenta-500 rounded-full"></div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          {/* Title Section */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-magenta-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Let's personalize your study journey</h2>
            <p className="text-gray-600">Answer a few quick questions so we can generate your ideal plan.</p>
            <div className="mt-4 p-3 bg-cyan-50 rounded-xl border border-cyan-100">
              <p className="text-sm text-cyan-700 font-medium">💡 The more accurate your inputs, the smarter your plan!</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Exam Name */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <Target className="w-4 h-4 text-cyan-600" />
                Exam Name *
              </label>
              <select
                name="examName"
                value={formData.examName}
                onChange={handleInputChange}
                required
                disabled={loading}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200 text-gray-900 disabled:bg-gray-50 disabled:cursor-not-allowed"
              >
                <option value="">Select your target exam</option>
                {exams.map(exam => (
                  <option key={exam} value={exam}>{exam}</option>
                ))}
              </select>
            </div>

            {/* Exam Date */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <Calendar className="w-4 h-4 text-magenta-600" />
                Exam Date *
              </label>
              <input
                type="date"
                name="examDate"
                value={formData.examDate}
                onChange={handleInputChange}
                required
                min={getMinDate()}
                disabled={loading}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-magenta-500 focus:border-transparent transition-all duration-200 text-gray-900 disabled:bg-gray-50 disabled:cursor-not-allowed"
              />
              {daysUntilExam !== null && (
                <p className="mt-2 text-sm text-gray-600">
                  📅 <span className="font-medium text-magenta-600">{daysUntilExam}</span> days until your exam
                </p>
              )}
            </div>

            {/* Topics Covered */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <BookOpen className="w-4 h-4 text-cyan-600" />
                Topics Already Covered
                <span className="text-xs text-gray-500">(optional)</span>
              </label>
              <p className="text-xs text-gray-500 mb-3">Select topics you've already studied to get a more accurate plan</p>
              <div className="max-h-64 overflow-y-auto border border-gray-300 rounded-xl p-4 space-y-4">
                {topics.map(category => (
                  <div key={category.category}>
                    <h4 className="font-medium text-gray-800 mb-2">{category.category}</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {category.items.map(item => (
                        <label
                          key={item}
                          className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition-all duration-200 ${
                            formData.topicsCovered.includes(item)
                              ? 'bg-cyan-50 border-cyan-200 text-cyan-700'
                              : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          <input
                            type="checkbox"
                            checked={formData.topicsCovered.includes(item)}
                            onChange={() => !loading && handleTopicToggle(item)}
                            disabled={loading}
                            className="w-4 h-4 text-cyan-600 rounded focus:ring-cyan-500"
                          />
                          <span className="text-xs">{item}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              {formData.topicsCovered.length > 0 && (
                <p className="mt-2 text-sm text-cyan-600">
                  ✅ {formData.topicsCovered.length} topics selected
                </p>
              )}
            </div>

            {/* Study Hours and Days */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                  <Clock className="w-4 h-4 text-magenta-600" />
                  Study Hours per Day *
                </label>
                <input
                  type="number"
                  name="studyHours"
                  value={formData.studyHours}
                  onChange={handleInputChange}
                  required
                  min="1"
                  max="16"
                  placeholder="e.g., 4"
                  disabled={loading}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-magenta-500 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed"
                />
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                  <Calendar className="w-4 h-4 text-cyan-600" />
                  Study Days per Week *
                </label>
                <input
                  type="number"
                  name="studyDays"
                  value={formData.studyDays}
                  onChange={handleInputChange}
                  required
                  min="1"
                  max="7"
                  placeholder="e.g., 6"
                  disabled={loading}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-6">
              <button
                type="button"
                onClick={onBack}
                disabled={loading}
                className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-600 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Skip for Now
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white py-3 px-6 rounded-xl font-medium hover:from-cyan-600 hover:to-cyan-700 transform hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Saving Your Data...
                  </span>
                ) : (
                  'Generate My Study Plan ✨'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default OnboardingPage;