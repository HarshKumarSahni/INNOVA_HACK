import React, { useState, useEffect } from 'react';
import LoginPage from './components/LoginPage';
import SignupPage from './components/SignupPage';
import OnboardingPage from './components/OnboardingPage';
import Dashboard from './components/Dashboard';
import { API_BASE_URL } from './config';

// Types for user data
interface User {
  id: number;
  email: string;
  token?: string;
  hasCompletedOnboarding?: boolean;
}

interface OnboardingData {
  examName: string;
  examDate: string;
  topicsCovered: string[];
  studyHours: string;
  studyDays: string;
}

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [showSignup, setShowSignup] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Check if user is already logged in when app loads
  useEffect(() => {
    const checkExistingAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        // Verify token with backend and get user info
        const response = await fetch(`${API_BASE_URL}/api/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const userData = await response.json();
          const userWithToken: User = {
            id: userData.id,
            email: userData.email,
            token,
            hasCompletedOnboarding: userData.has_completed_onboarding
          };
          
          setUser(userWithToken);
          
          // Store user data in localStorage (without token for security)
          localStorage.setItem('user_data', JSON.stringify({
            id: userData.id,
            email: userData.email,
            hasCompletedOnboarding: userData.has_completed_onboarding
          }));
          
          // Determine if we need to show onboarding
          if (!userData.has_completed_onboarding) {
            setShowOnboarding(true);
          }
        } else {
          // Token is invalid, clear everything
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_data');
          localStorage.removeItem('onboarding_data');
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
        // Clear potentially invalid data
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('onboarding_data');
      } finally {
        setLoading(false);
      }
    };

    checkExistingAuth();
  }, []);

  // Handle successful login
  const handleLogin = (userData: { id: number; email: string; token: string; hasCompletedOnboarding: boolean }) => {
    const user: User = {
      id: userData.id,
      email: userData.email,
      token: userData.token,
      hasCompletedOnboarding: userData.hasCompletedOnboarding
    };
    
    setUser(user);
    
    // Store user data in localStorage (without token for security)
    localStorage.setItem('user_data', JSON.stringify({
      id: user.id,
      email: user.email,
      hasCompletedOnboarding: user.hasCompletedOnboarding
    }));
    
    // Check if user needs onboarding
    if (!userData.hasCompletedOnboarding) {
      setShowOnboarding(true);
    }
  };

  // Handle successful signup
  const handleSignup = (userData: { id: number; email: string; token?: string; hasCompletedOnboarding?: boolean }) => {
    // If signup came with a token (e.g., Google OAuth), log the user in directly
    if (userData.token) {
      const newUser: User = {
        id: userData.id,
        email: userData.email,
        token: userData.token,
        hasCompletedOnboarding: userData.hasCompletedOnboarding ?? false
      };
      localStorage.setItem('access_token', userData.token);
      localStorage.setItem('user_data', JSON.stringify({
        id: userData.id,
        email: userData.email,
        hasCompletedOnboarding: userData.hasCompletedOnboarding ?? false
      }));
      setUser(newUser);
      if (!userData.hasCompletedOnboarding) {
        setShowOnboarding(true);
      }
    } else {
      // Standard email/password signup — just go to login page
      console.log('User account created:', userData);
      setShowSignup(false);
    }
  };

  // Handle onboarding completion
  const handleOnboardingComplete = async (onboardingData: OnboardingData) => {
    try {
      // The onboarding data is already saved to backend by OnboardingPage component
      // Just update the local state and storage
      
      // Store onboarding data locally as well
      localStorage.setItem('onboarding_data', JSON.stringify({
        ...onboardingData,
        completedAt: new Date().toISOString()
      }));

      // Mark onboarding as complete
      setShowOnboarding(false);
      
      // Update user state
      if (user) {
        const updatedUser = { ...user, hasCompletedOnboarding: true };
        setUser(updatedUser);
        
        // Update localStorage
        localStorage.setItem('user_data', JSON.stringify({
          id: updatedUser.id,
          email: updatedUser.email,
          hasCompletedOnboarding: true
        }));
      }

      console.log('Onboarding completed with data:', onboardingData);
    } catch (error) {
      console.error('Error completing onboarding:', error);
      // Still proceed to dashboard since the backend already saved the data
      setShowOnboarding(false);
      
      if (user) {
        setUser({ ...user, hasCompletedOnboarding: true });
      }
    }
  };

  // Handle logout
  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('onboarding_data');
    setShowSignup(false);
    setShowOnboarding(false);
  };

  // Handle going back from onboarding
  const handleOnboardingBack = () => {
    // Skip onboarding for now - user can complete it later
    setShowOnboarding(false);
  };

  // Handle switching between login and signup
  const switchToSignup = () => setShowSignup(true);
  const switchToLogin = () => setShowSignup(false);

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-cyan-50 via-white to-purple-50">
        <div className="text-center">
          <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="text-gray-600">Loading AceTrack...</p>
        </div>
      </div>
    );
  }

  // If user is logged in but needs onboarding
  if (user && showOnboarding) {
    return (
      <div className="bg-gradient-to-br from-cyan-50 via-white to-purple-50 min-h-screen">
        <OnboardingPage 
          onBack={handleOnboardingBack}
          onComplete={handleOnboardingComplete}
        />
      </div>
    );
  }

  // If user is logged in and has completed onboarding, show dashboard
  if (user && !showOnboarding) {
    return <Dashboard user={user} onLogout={handleLogout} />;
  }

  // If user is not logged in, show login or signup page
  return (
    <div className="bg-gradient-to-br from-cyan-50 via-white to-purple-50 min-h-screen">
      {showSignup ? (
        <SignupPage 
          onSignup={handleSignup}
          onSwitchToLogin={switchToLogin}
        />
      ) : (
        <LoginPage 
          onLogin={handleLogin}
          onSwitchToSignup={switchToSignup}
        />
      )}
    </div>
  );
};

export default App;