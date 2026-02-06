import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Menu, Bell, Globe, User, ChevronDown, LogOut, Settings, Plus } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useCompany } from '../../contexts/CompanyContext';
import { useFinancialData } from '../../contexts/FinancialDataContext';
import CreateCompanyModal from '../Company/CreateCompanyModal';

const Header = ({ sidebarOpen, setSidebarOpen }) => {
  const { user, logout } = useAuth();
  const { selectedCompany, companies, selectCompany } = useCompany();
  const { dashboardSummary, refreshAfterUpload } = useFinancialData();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showCompanySelector, setShowCompanySelector] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const { currentLanguage, t } = useLanguage();

  // Listen for refresh events after upload
  useEffect(() => {
    const handleRefresh = () => {
      refreshAfterUpload();
    };
    window.addEventListener('dataUploaded', handleRefresh);
    window.addEventListener('refreshDashboard', handleRefresh);

    return () => {
      window.removeEventListener('dataUploaded', handleRefresh);
      window.removeEventListener('refreshDashboard', handleRefresh);
    };
  }, [refreshAfterUpload]);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी' }
  ];

  const getHealthScoreColor = (score) => {
    if (score >= 80) return 'text-success-600 bg-success-100';
    if (score >= 60) return 'text-warning-600 bg-warning-100';
    return 'text-danger-600 bg-danger-100';
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left side */}
          <div className="flex items-center">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 lg:hidden"
            >
              <Menu className="w-6 h-6" />
            </button>

            {/* Company selector */}
            <div className="relative ml-4">
              <button
                onClick={() => setShowCompanySelector(!showCompanySelector)}
                className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div>
                  <div className="text-sm font-medium text-gray-900">
                    {selectedCompany ? selectedCompany.name : 'Select Company'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {selectedCompany ? selectedCompany.industry : 'No company selected'}
                  </div>
                </div>
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </button>

              {/* Company dropdown */}
              {showCompanySelector && (
                <div className="absolute left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="p-2">
                    {companies.length > 0 ? (
                      <>
                        {companies.map((company) => (
                          <button
                            key={company.id}
                            onClick={() => {
                              selectCompany(company);
                              setShowCompanySelector(false);
                            }}
                            className={`
                              w-full text-left px-3 py-2 rounded-md text-sm transition-colors duration-200
                              ${selectedCompany?.id === company.id
                                ? 'bg-primary-100 text-primary-700'
                                : 'text-gray-700 hover:bg-gray-50'
                              }
                            `}
                          >
                            <div className="font-medium">{company.name}</div>
                            <div className="text-xs text-gray-500">{company.industry}</div>
                          </button>
                        ))}
                        <button
                          onClick={() => {
                            setShowCreateModal(true);
                            setShowCompanySelector(false);
                          }}
                          className="w-full text-left px-3 py-2 rounded-md text-sm text-primary-600 hover:bg-primary-50 transition-colors duration-200 flex items-center gap-2"
                        >
                          <Plus className="w-4 h-4" />
                          Create New Company
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => {
                          setShowCreateModal(true);
                          setShowCompanySelector(false);
                        }}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-primary-600 hover:bg-primary-50 transition-colors duration-200 flex items-center gap-2"
                      >
                        <Plus className="w-4 h-4" />
                        Create Your First Company
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Health score badge */}
            {selectedCompany && dashboardSummary && (
              <div className="ml-6">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Health Score:</span>
                  <div className={`px-2 py-1 rounded-full text-xs font-semibold ${getHealthScoreColor(dashboardSummary.financial_health_score || 0)}`}>
                    {dashboardSummary.financial_health_score !== null ? dashboardSummary.financial_health_score.toFixed(0) : 'N/A'}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Language selector */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-1 p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 transition-colors duration-200"
              >
                <Globe className="w-5 h-5" />
                <span className="text-sm font-medium text-gray-700">
                  {languages.find(l => l.code === currentLanguage)?.name}
                </span>
              </button>
            </div>

            {/* Notifications */}
            <Link to="/notifications" className="relative p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 transition-colors duration-200">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full"></span>
            </Link>

            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-3 p-2 rounded-md hover:bg-gray-100 transition-colors duration-200"
              >
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div className="hidden md:block">
                  <div className="text-sm font-medium text-gray-900">{user?.full_name}</div>
                  <div className="text-xs text-gray-500">{user?.email}</div>
                </div>
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </button>

              {/* User dropdown */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="py-1">
                    <Link
                      to="/profile"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <User className="w-4 h-4 mr-3" />
                      Profile
                    </Link>
                    <Link
                      to="/settings"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <Settings className="w-4 h-4 mr-3" />
                      Settings
                    </Link>
                    <button
                      onClick={logout}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full"
                    >
                      <LogOut className="w-4 h-4 mr-3" />
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      <CreateCompanyModal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} />
    </header>
  );
};

export default Header;
