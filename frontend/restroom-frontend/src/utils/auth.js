// src/utils/auth.js

export const auth = {
    // Check if user is logged in
    isLoggedIn: () => {
      return !!localStorage.getItem('token');
    },
  
    // Get current user info
    getCurrentUser: () => {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    },
  
    // Save login data
    saveLoginData: (token, user) => {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
    },
  
    // Clear login data
    clearLoginData: () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    },
  
    // Get token
    getToken: () => {
      return localStorage.getItem('token');
    }
  };