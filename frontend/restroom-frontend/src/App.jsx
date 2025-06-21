// src/App.jsx
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { auth } from './utils/auth';

// Page components
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import RestroomDetailPage from './pages/RestroomDetailPage';
import ProfilePage from './pages/ProfilePage';

// Common components
import Navbar from './components/Navbar';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    // Check login status
    if (auth.isLoggedIn()) {
      setIsLoggedIn(true);
      setCurrentUser(auth.getCurrentUser());
    }
  }, []);

  const handleLogin = (token, user) => {
    auth.saveLoginData(token, user);
    setIsLoggedIn(true);
    setCurrentUser(user);
  };

  const handleLogout = () => {
    auth.clearLoginData();
    setIsLoggedIn(false);
    setCurrentUser(null);
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Show navbar only when logged in */}
        {isLoggedIn && (
          <Navbar 
            currentUser={currentUser} 
            onLogout={handleLogout} 
          />
        )}

        <Routes>
          {/* Public routes */}
          <Route 
            path="/login" 
            element={
              isLoggedIn ? 
              <Navigate to="/" /> : 
              <LoginPage onLogin={handleLogin} />
            } 
          />
          <Route 
            path="/register" 
            element={
              isLoggedIn ? 
              <Navigate to="/" /> : 
              <RegisterPage onLogin={handleLogin} />
            } 
          />

          {/* Protected routes */}
          <Route 
            path="/" 
            element={
              isLoggedIn ? 
              <HomePage /> : 
              <Navigate to="/login" />
            } 
          />
          <Route 
            path="/restroom/:id" 
            element={
              isLoggedIn ? 
              <RestroomDetailPage /> : 
              <Navigate to="/login" />
            } 
          />
          <Route 
            path="/profile" 
            element={
              isLoggedIn ? 
              <ProfilePage currentUser={currentUser} /> : 
              <Navigate to="/login" />
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;