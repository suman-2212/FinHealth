import React, { createContext, useContext, useReducer, useCallback } from 'react';
import axios from 'axios';

// Initial state
const initialState = {
  // Loading states
  loading: false,
  initialLoading: true, // For first load
  
  // Financial data
  dashboardSummary: null,
  financialHealth: null,
  riskAnalysis: null,
  creditEvaluation: null,
  forecasting: null,
  benchmarking: null,
  monthlyData: [],
  
  // Company info
  selectedCompany: null,
  companies: [],
  
  // Error state
  error: null,
  
  // Last updated timestamp
  lastUpdated: null,
};

// Action types
const ACTIONS = {
  SET_INITIAL_LOADING: 'SET_INITIAL_LOADING',
  SET_LOADING: 'SET_LOADING',
  SET_SELECTED_COMPANY: 'SET_SELECTED_COMPANY',
  SET_COMPANIES: 'SET_COMPANIES',
  SET_DASHBOARD_SUMMARY: 'SET_DASHBOARD_SUMMARY',
  SET_FINANCIAL_HEALTH: 'SET_FINANCIAL_HEALTH',
  SET_RISK_ANALYSIS: 'SET_RISK_ANALYSIS',
  SET_CREDIT_EVALUATION: 'SET_CREDIT_EVALUATION',
  SET_FORECASTING: 'SET_FORECASTING',
  SET_BENCHMARKING: 'SET_BENCHMARKING',
  SET_MONTHLY_DATA: 'SET_MONTHLY_DATA',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  REFRESH_ALL_DATA: 'REFRESH_ALL_DATA',
  UPDATE_AFTER_UPLOAD: 'UPDATE_AFTER_UPLOAD',
};

// Reducer
const financialDataReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.SET_INITIAL_LOADING:
      return {
        ...state,
        initialLoading: action.payload,
      };
    
    case ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    
    case ACTIONS.SET_SELECTED_COMPANY:
      return {
        ...state,
        selectedCompany: action.payload,
      };
    
    case ACTIONS.SET_COMPANIES:
      return {
        ...state,
        companies: action.payload,
      };
    
    case ACTIONS.SET_DASHBOARD_SUMMARY:
      return {
        ...state,
        dashboardSummary: action.payload,
        lastUpdated: new Date().toISOString(),
      };
    
    case ACTIONS.SET_FINANCIAL_HEALTH:
      return {
        ...state,
        financialHealth: action.payload,
        lastUpdated: new Date().toISOString(),
      };
    
    case ACTIONS.SET_RISK_ANALYSIS:
      return {
        ...state,
        riskAnalysis: action.payload,
        lastUpdated: new Date().toISOString(),
      };
    
    case ACTIONS.SET_CREDIT_EVALUATION:
      return {
        ...state,
        creditEvaluation: action.payload,
        lastUpdated: new Date().toISOString(),
      };
    
    case ACTIONS.SET_FORECASTING:
      return {
        ...state,
        forecasting: action.payload,
        lastUpdated: new Date().toISOString(),
      };
    
    case ACTIONS.SET_BENCHMARKING:
      return {
        ...state,
        benchmarking: action.payload,
        lastUpdated: new Date().toISOString(),
      };
    
    case ACTIONS.SET_MONTHLY_DATA:
      return {
        ...state,
        monthlyData: action.payload,
        lastUpdated: new Date().toISOString(),
      };
    
    case ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false,
        initialLoading: false,
      };
    
    case ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };
    
    case ACTIONS.REFRESH_ALL_DATA:
      return {
        ...state,
        loading: true,
        error: null,
      };
    
    case ACTIONS.UPDATE_AFTER_UPLOAD:
      return {
        ...state,
        lastUpdated: new Date().toISOString(),
      };
    
    default:
      return state;
  }
};

// Create context
const FinancialDataContext = createContext();

// Provider component
export const FinancialDataProvider = ({ children }) => {
  const [state, dispatch] = useReducer(financialDataReducer, initialState);

  // Fetch all financial data for a company
  const fetchAllFinancialData = useCallback(async (companyId) => {
    if (!companyId) return;
    
    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    dispatch({ type: ACTIONS.CLEAR_ERROR });
    
    try {
      // Only fetch endpoints that are working
      const [
        dashboardRes,
        healthRes,
        riskRes,
        creditRes
      ] = await Promise.allSettled([
        axios.get('/api/dashboard-summary'),
        axios.get('/api/financial-health'),
        axios.get('/api/risk-analysis'),
        axios.get('/api/credit-evaluation')
      ]);

      // Process results
      if (dashboardRes.status === 'fulfilled') {
        dispatch({ type: ACTIONS.SET_DASHBOARD_SUMMARY, payload: dashboardRes.value.data });
      }
      
      if (healthRes.status === 'fulfilled') {
        dispatch({ type: ACTIONS.SET_FINANCIAL_HEALTH, payload: healthRes.value.data });
      }
      
      if (riskRes.status === 'fulfilled') {
        dispatch({ type: ACTIONS.SET_RISK_ANALYSIS, payload: riskRes.value.data });
      }
      
      if (creditRes.status === 'fulfilled') {
        dispatch({ type: ACTIONS.SET_CREDIT_EVALUATION, payload: creditRes.value.data });
      }
      
    } catch (error) {
      console.error('Failed to fetch financial data:', error);
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: error.response?.data?.detail || 'Failed to fetch financial data' 
      });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
      dispatch({ type: ACTIONS.SET_INITIAL_LOADING, payload: false });
    }
  }, []);

  // Load cached data on company change
  const loadCachedData = useCallback((companyId) => {
    if (!companyId) return;
    
    try {
      const cached = localStorage.getItem(`financialData_${companyId}`);
      if (cached) {
        const { timestamp, data } = JSON.parse(cached);
        
        // Use cached data if it's less than 5 minutes old
        const cacheAge = new Date() - new Date(timestamp);
        if (cacheAge < 5 * 60 * 1000) { // 5 minutes
          dispatch({ type: ACTIONS.SET_DASHBOARD_SUMMARY, payload: data.dashboard });
          dispatch({ type: ACTIONS.SET_FINANCIAL_HEALTH, payload: data.health });
          dispatch({ type: ACTIONS.SET_RISK_ANALYSIS, payload: data.risk });
          dispatch({ type: ACTIONS.SET_CREDIT_EVALUATION, payload: data.credit });
          dispatch({ type: ACTIONS.SET_FORECASTING, payload: data.forecast });
          dispatch({ type: ACTIONS.SET_BENCHMARKING, payload: data.benchmark });
          dispatch({ type: ACTIONS.SET_MONTHLY_DATA, payload: data.monthly });
          dispatch({ type: ACTIONS.SET_INITIAL_LOADING, payload: false });
          return true; // Cache hit
        }
      }
    } catch (error) {
      console.error('Failed to load cached data:', error);
    }
    return false; // Cache miss
  }, []); // Empty dependency array to prevent infinite loops

  // Refresh data after upload
  const refreshAfterUpload = () => {
    if (state.selectedCompany) {
      // Clear cache to force fresh data fetch
      clearCache(state.selectedCompany.id);
      // Fetch fresh data
      fetchAllFinancialData(state.selectedCompany.id);
    }
  };

  // Clear cache for a company
  const clearCache = (companyId) => {
    localStorage.removeItem(`financialData_${companyId}`);
  };

  const value = {
    ...state,
    dispatch,
    fetchAllFinancialData,
    loadCachedData,
    refreshAfterUpload,
    clearCache,
  };

  return (
    <FinancialDataContext.Provider value={value}>
      {children}
    </FinancialDataContext.Provider>
  );
};

// Hook to use the context
export const useFinancialData = () => {
  const context = useContext(FinancialDataContext);
  if (!context) {
    throw new Error('useFinancialData must be used within a FinancialDataProvider');
  }
  return context;
};

export { ACTIONS };
