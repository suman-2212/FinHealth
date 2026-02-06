import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { CompanyProvider, useCompany } from './contexts/CompanyContext';
import { FinancialDataProvider, useFinancialData, ACTIONS } from './contexts/FinancialDataContext';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import Dashboard from './pages/Dashboard/Dashboard';
import FinancialHealth from './pages/FinancialHealth/FinancialHealth';
import RiskAnalysis from './pages/RiskAnalysis/RiskAnalysis';
import CreditEvaluation from './pages/CreditEvaluation/CreditEvaluation';
import Forecasting from './pages/Forecasting/Forecasting';
import Benchmarking from './pages/Benchmarking/Benchmarking';
import Reports from './pages/Reports/Reports';
import Notifications from './pages/Notifications/Notifications';
import Settings from './pages/Settings/Settings';
import Profile from './pages/Profile/Profile';
import DataUpload from './pages/DataUpload/DataUpload';
import LoadingSpinner from './components/UI/LoadingSpinner';
import './index.css';
import './utils/axiosSetup'; // activates interceptor

function AppLayout() {
  const { user, loading: authLoading } = useAuth();
  const { selectedCompany, companies } = useCompany();
  const { initialLoading, fetchAllFinancialData, loadCachedData, dispatch } = useFinancialData();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  console.log('AppLayout state:', { 
    user: !!user, 
    authLoading, 
    initialLoading, 
    companiesCount: companies.length, 
    hasSelectedCompany: !!selectedCompany,
    companies: companies
  });

  // Set initialLoading to false if user is not authenticated
  useEffect(() => {
    if (!user && !authLoading) {
      dispatch({ type: ACTIONS.SET_INITIAL_LOADING, payload: false });
    }
  }, [user, authLoading, dispatch]);

  // Combined loading state - only show loading for auth, not for financial data when user is not logged in
  const loading = authLoading || (user && initialLoading);

  console.log('Combined loading state:', loading);

  // Fetch financial data when company changes
  useEffect(() => {
    if (selectedCompany && user) {
      // Try to load cached data first
      const cacheHit = loadCachedData(selectedCompany.id);
      
      // If no cache hit, fetch fresh data
      if (!cacheHit) {
        fetchAllFinancialData(selectedCompany.id);
      }
    }
  }, [selectedCompany, user, fetchAllFinancialData, loadCachedData]);

  // Set initialLoading to false when user is authenticated and companies are loaded
  useEffect(() => {
    if (user && companies.length > 0 && !selectedCompany) {
      // User is authenticated and companies are loaded, but no company selected
      // Set initialLoading to false to allow company selection screen to show
      dispatch({ type: ACTIONS.SET_INITIAL_LOADING, payload: false });
    }
  }, [user, companies, selectedCompany, dispatch]);

  if (loading) {
    console.log('Showing loading screen');
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading your financial data...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    console.log('Showing auth routes (no user)');
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  // User can access dashboard even without companies
  // Company creation can be done from within the dashboard

  // User can access dashboard without company selection
  // Company selection and creation can be handled within the dashboard

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      
      <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-0'}`}>
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
        
        <main className="p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/financial-health" element={<FinancialHealth />} />
            <Route path="/risk-analysis" element={<RiskAnalysis />} />
            <Route path="/credit-evaluation" element={<CreditEvaluation />} />
            <Route path="/forecasting" element={<Forecasting />} />
            <Route path="/benchmarking" element={<Benchmarking />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/data-upload" element={<DataUpload />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <CompanyProvider>
            <FinancialDataProvider>
              <AppLayout />
            </FinancialDataProvider>
          </CompanyProvider>
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#22c55e',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </Router>
    </AuthProvider>
  );
}

export default App;
