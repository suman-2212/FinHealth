import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Configure axios defaults and add response interceptor
  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('Setting up axios with token:', token ? 'exists' : 'none');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }

    // Add response interceptor to handle 401 errors
    const interceptor = axios.interceptors.response.use(
      (response) => response, // Return successful responses as-is
      (error) => {
        // If we get a 401 error, automatically logout the user
        if (error.response?.status === 401) {
          // Only log out if not on the login page
          if (window.location.pathname !== '/login') {
            console.error('Token expired or invalid - logging out user');
            localStorage.removeItem('token');
            localStorage.removeItem('currentCompanyId');
            delete axios.defaults.headers.common['Authorization'];
            setUser(null);
            toast.error('Session expired. Please login again.');
          }
        }
        return Promise.reject(error);
      }
    );

    // Cleanup interceptor on unmount
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Clear any existing tokens first to ensure fresh start
        localStorage.removeItem('token');
        localStorage.removeItem('currentCompanyId');
        delete axios.defaults.headers.common['Authorization'];
        
        console.log('Auth check: Starting fresh (cleared existing tokens)');
        setLoading(false);
      } catch (error) {
        console.error('Auth setup error:', error);
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (userData) => {
    try {
      console.log('AuthContext: Sending login request:', { email: userData.email, password: '***' });
      const response = await axios.post('/api/auth/login', userData);
      console.log('AuthContext: Login response:', response.status, response.data);
      
      // Check if response data has expected structure
      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid response format from server');
      }
      
      const { access_token, user, companies, default_company_id } = response.data;
      
      // Validate required fields
      if (!access_token || !user) {
        console.error('Missing required fields in response:', { access_token: !!access_token, user: !!user });
        throw new Error('Invalid response: missing required authentication data');
      }
      
      // Store token
      localStorage.setItem('token', access_token);
      
      // Set axios default header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      if (default_company_id) {
        localStorage.setItem('currentCompanyId', default_company_id);
      }
      
      // Set user state with correct data
      setUser({ 
        id: user.id,
        email: user.email,
        full_name: user.full_name,
        companies: companies,
        default_company_id: default_company_id
      });
      
      toast.success('Login successful!');
      return { success: true, companies, default_company_id };
    } catch (error) {
      console.error('AuthContext: Login error details:', error.response?.status, error.response?.data);
      const message = error.response?.data?.detail || 'Login failed';
      
      // Check if it's a token validation error (401) or authentication error (403)
      if (error.response?.status === 401) {
        toast.error('Invalid or expired token. Please log in again.');
        return { success: false, error: 'Invalid or expired token. Please log in again.' };
      }
      
      if (error.response?.status === 403) {
        toast.error('Access denied. Please check your credentials.');
        return { success: false, error: 'Access denied. Please check your credentials.' };
      }
      
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const register = async (userData) => {
    try {
      await axios.post('/api/auth/register', userData);
      toast.success('Registration successful! Please login.');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('currentCompanyId');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    toast.success('Logged out successfully');
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
