import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from './AuthContext';

const CompanyContext = createContext();

export const useCompany = () => {
  const context = useContext(CompanyContext);
  if (!context) {
    throw new Error('useCompany must be used within a CompanyProvider');
  }
  return context;
};

export const CompanyProvider = ({ children }) => {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  const fetchCompanies = useCallback(async () => {
    try {
      setLoading(true);
      console.log('Fetching companies from API...');
      const response = await axios.get('/api/company/');
      console.log('Companies fetched successfully:', response.data);
      setCompanies(response.data);
      
      // If no companies found, show a helpful message
      if (response.data.length === 0) {
        console.log('No companies found for this user');
        toast.error('No companies found. Please create a company first.');
      }
    } catch (error) {
      console.error('Failed to fetch companies:', error);
      // Only show error toast if it's not a 401 (unauthorized) error
      if (error.response?.status !== 401) {
        toast.error('Failed to load companies');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch companies when user is authenticated
  useEffect(() => {
    if (user) {
      console.log('User authenticated, fetching companies...');
      fetchCompanies();
    } else {
      console.log('No user, not fetching companies');
    }
  }, [user, fetchCompanies]);

  // Load selected company from localStorage (tenant-aware)
  useEffect(() => {
    const savedCompanyId = localStorage.getItem('currentCompanyId');
    console.log('Loading selected company from localStorage:', savedCompanyId);
    console.log('Available companies:', companies);
    
    if (savedCompanyId && companies.length > 0) {
      const company = companies.find(c => c.id === savedCompanyId);
      if (company) {
        console.log('Found selected company:', company);
        setSelectedCompany(company);
      } else {
        console.log('Saved company not found in companies list');
        // Clear invalid company ID
        localStorage.removeItem('currentCompanyId');
      }
    }
  }, [companies]);

  const createCompany = async (companyData) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/company/create', companyData);
      const newCompany = response.data;
      setCompanies(prev => [...prev, newCompany]);
      // Auto-select new company
      setSelectedCompany(newCompany);
      localStorage.setItem('currentCompanyId', newCompany.id);
      toast.success('Company created and selected!');
      return { success: true, company: newCompany };
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to create company';
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const updateCompany = async (companyId, companyData) => {
    try {
      setLoading(true);
      const response = await axios.put(`/api/company/${companyId}`, companyData);
      const updatedCompany = response.data;
      setCompanies(prev => 
        prev.map(company => 
          company.id === companyId ? updatedCompany : company
        )
      );
      
      if (selectedCompany?.id === companyId) {
        setSelectedCompany(updatedCompany);
      }
      
      toast.success('Company updated successfully!');
      return { success: true, company: updatedCompany };
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to update company';
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const selectCompany = async (company) => {
    setSelectedCompany(company);
    localStorage.setItem('currentCompanyId', company.id);
    // Notify backend of switch for audit
    try {
      await axios.post('/api/company/switch', { company_id: company.id });
    } catch (err) {
      console.error('Company switch audit failed', err);
    }
    // Trigger dashboard reload by emitting a custom event or state update
    window.dispatchEvent(new CustomEvent('companyChanged', { detail: company }));
  };

  const deleteCompany = async (companyId) => {
    try {
      setLoading(true);
      await axios.delete(`/api/company/${companyId}`);
      setCompanies(prev => prev.filter(company => company.id !== companyId));
      
      if (selectedCompany?.id === companyId) {
        setSelectedCompany(null);
        localStorage.removeItem('currentCompanyId');
      }
      
      toast.success('Company deleted successfully!');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to delete company';
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    companies,
    selectedCompany,
    loading,
    fetchCompanies,
    createCompany,
    updateCompany,
    selectCompany,
    deleteCompany
  };

  return (
    <CompanyContext.Provider value={value}>
      {children}
    </CompanyContext.Provider>
  );
};
