import React, { useState } from 'react';
import { Eye, EyeOff, BookOpen, Target, TrendingUp } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface LoginPageProps {
  onLogin: (userData: { id: number; email: string; token: string; hasCompletedOnboarding: boolean }) => void;
  onSwitchToSignup?: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin, onSwitchToSignup }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Store token in localStorage with consistent key
      localStorage.setItem('access_token', data.access_token);
      
      // Call onLogin with user data including onboarding status
      onLogin({
        id: data.user.id,
        email: data.user.email,
        token: data.access_token,
        hasCompletedOnboarding: data.user.has_completed_onboarding
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error when user starts typing
    if (error) setError('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-xl flex items-center justify-center shadow-lg">
              <Target className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">AceTrack</h1>
          </div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">Welcome to AceTrack</h2>
          <p className="text-gray-600 text-lg">Your personalized path to ace any exam</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm">
                {error}
              </div>
            )}

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                disabled={loading}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed"
                placeholder="Enter your email"
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  disabled={loading}
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={loading}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 transition-colors disabled:cursor-not-allowed"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-cyan-500 to-cyan-600 text-white py-3 px-6 rounded-xl font-medium hover:from-cyan-600 hover:to-cyan-700 transform hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>

            {/* Forgot Password */}
            <div className="text-center">
              <a href="#" className="text-cyan-500 hover:text-cyan-600 text-sm font-medium transition-colors">
                Forgot Password?
              </a>
            </div>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500 font-medium">OR</span>
              </div>
            </div>

            {/* Sign Up Link */}
            <div className="text-center">
              <p className="text-gray-600">
                New to AceTrack?{' '}
                <button
                  type="button"
                  onClick={onSwitchToSignup}
                  className="text-cyan-500 hover:text-cyan-600 font-medium transition-colors"
                >
                  Sign up
                </button>
              </p>
            </div>
          </form>
        </div>

        {/* Feature Highlights */}
        <div className="mt-12 grid grid-cols-3 gap-6 text-center">
          <div className="space-y-2">
            <div className="w-10 h-10 bg-cyan-100 rounded-lg flex items-center justify-center mx-auto">
              <BookOpen className="w-5 h-5 text-cyan-600" />
            </div>
            <p className="text-sm text-gray-600">Smart Study Plans</p>
          </div>
          <div className="space-y-2">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mx-auto">
              <Target className="w-5 h-5 text-purple-600" />
            </div>
            <p className="text-sm text-gray-600">Goal Tracking</p>
          </div>
          <div className="space-y-2">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mx-auto">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <p className="text-sm text-gray-600">Progress Analytics</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;