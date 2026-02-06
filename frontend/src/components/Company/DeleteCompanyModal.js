import React, { useState } from 'react';
import { Trash2, AlertTriangle, X } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useCompany } from '../../contexts/CompanyContext';
import { useAuth } from '../../contexts/AuthContext';

const DeleteCompanyModal = ({ isOpen, onClose, company }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const { selectedCompany, fetchCompanies } = useCompany();

  if (!isOpen || !company) return null;

  const handleDelete = async () => {
    if (confirmText !== company.name) {
      toast.error('Please type the company name exactly to confirm deletion');
      return;
    }

    setIsDeleting(true);
    
    try {
      await axios.delete(`/api/company/${company.id}`);
      
      toast.success(`Company "${company.name}" and all associated data deleted successfully`);
      
      // Clear current company if it was the deleted one
      if (selectedCompany?.id === company.id) {
        localStorage.removeItem('currentCompanyId');
      }
      
      // Refresh companies list
      await fetchCompanies();
      
      // Redirect to dashboard if this was the current company
      if (selectedCompany?.id === company.id) {
        window.location.href = '/dashboard';
      }
      
      onClose();
      
    } catch (error) {
      console.error('Delete company error:', error);
      
      if (error.response?.status === 400) {
        toast.error(error.response.data.detail || 'Cannot delete company');
      } else if (error.response?.status === 404) {
        toast.error('Company not found');
      } else if (error.response?.status === 403) {
        toast.error('You do not have permission to delete this company');
      } else {
        toast.error('Failed to delete company. Please try again.');
      }
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <Trash2 className="w-5 h-5 text-red-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Delete Company</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
            disabled={isDeleting}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Warning Alert */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-medium text-red-800">This action cannot be undone</h3>
                <p className="text-sm text-red-700 mt-1">
                  Deleting "{company.name}" will permanently remove all associated data:
                </p>
                <ul className="text-xs text-red-600 mt-2 space-y-1">
                  <li>• Financial statements and metrics</li>
                  <li>• Risk assessments and credit scores</li>
                  <li>• Forecasting data and analytics</li>
                  <li>• Uploaded documents and files</li>
                  <li>• Benchmarking data</li>
                  <li>• Reports and insights</li>
                  <li>• Audit logs and history</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Company Info */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{company.name}</p>
                <p className="text-sm text-gray-500">{company.industry}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500">Company ID</p>
                <p className="text-xs font-mono text-gray-400">{company.id}</p>
              </div>
            </div>
          </div>

          {/* Confirmation Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type the company name to confirm deletion:
            </label>
            <input
              type="text"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              placeholder={company.name}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
              disabled={isDeleting}
            />
          </div>

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              disabled={isDeleting}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting || confirmText !== company.name}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isDeleting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Deleting...</span>
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4" />
                  <span>Delete Company</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeleteCompanyModal;
