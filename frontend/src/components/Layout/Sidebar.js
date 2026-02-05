import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  HeartPulse, 
  AlertTriangle, 
  TrendingUp, 
  BarChart3, 
  Target, 
  FileText, 
  Settings,
  User,
  X,
  Upload
} from 'lucide-react';
import { useCompany } from '../../contexts/CompanyContext';

const Sidebar = ({ isOpen, setIsOpen }) => {
  const location = useLocation();
  const { selectedCompany } = useCompany();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Financial Health', href: '/financial-health', icon: HeartPulse },
    { name: 'Risk Analysis', href: '/risk-analysis', icon: AlertTriangle },
    { name: 'Credit Evaluation', href: '/credit-evaluation', icon: TrendingUp },
    { name: 'Forecasting', href: '/forecasting', icon: BarChart3 },
    { name: 'Benchmarking', href: '/benchmarking', icon: Target },
    { name: 'Reports', href: '/reports', icon: FileText },
    { name: 'Data Upload', href: '/data-upload', icon: Upload },
    { name: 'Settings', href: '/settings', icon: Settings },
    { name: 'Profile', href: '/profile', icon: User },
  ];

  const isActive = (href) => location.pathname === href;

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo and close button */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <HeartPulse className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-3">
                <h1 className="text-lg font-semibold text-gray-900">FinHealth</h1>
                <p className="text-xs text-gray-500">SME Intelligence</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Company selector */}
          {selectedCompany && (
            <div className="px-4 py-3 border-b border-gray-200">
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                Current Company
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="font-medium text-gray-900 text-sm truncate">
                  {selectedCompany.name}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {selectedCompany.industry}
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200
                    ${isActive(item.href)
                      ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                  onClick={() => setIsOpen(false)}
                >
                  <Icon className={`
                    mr-3 h-5 w-5 flex-shrink-0
                    ${isActive(item.href) ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500'}
                  `} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="px-4 py-4 border-t border-gray-200">
            <div className="text-xs text-gray-500 text-center">
              © 2024 FinHealth Platform
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
