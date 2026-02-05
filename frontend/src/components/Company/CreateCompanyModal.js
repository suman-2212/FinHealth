import React, { useState } from 'react';
import { X, Building2, Calendar, FileText } from 'lucide-react';
import { useCompany } from '../../contexts/CompanyContext';
import toast from 'react-hot-toast';

const CreateCompanyModal = ({ isOpen, onClose }) => {
  const { createCompany } = useCompany();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: '',
    industry: '',
    registration_number: '',
    financial_year_start: ''
  });

  const industries = [
    'Software',
    'Manufacturing',
    'Retail',
    'Healthcare',
    'Construction',
    'Financial Services',
    'Education',
    'Logistics',
    'Real Estate',
    'Consulting',
    'Other'
  ];

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.industry) {
      toast.error('Company name and industry are required');
      return;
    }
    setLoading(true);
    const result = await createCompany(form);
    if (result.success) {
      setForm({ name: '', industry: '', registration_number: '', financial_year_start: '' });
      onClose();
    }
    setLoading(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Building2 className="w-5 h-5 text-primary-600" />
            Create New Company
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Company Name *</label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="e.g., Acme Pvt Ltd"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Industry *</label>
            <select
              name="industry"
              value={form.industry}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            >
              <option value="">Select industry</option>
              {industries.map(ind => (
                <option key={ind} value={ind}>{ind}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
              <FileText className="w-4 h-4" />
              GST / Registration Number
            </label>
            <input
              type="text"
              name="registration_number"
              value={form.registration_number}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Optional"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              Financial Year Start (MM-DD)
            </label>
            <input
              type="text"
              name="financial_year_start"
              value={form.financial_year_start}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="e.g., 04-01"
              pattern="[0-9]{2}-[0-9]{2}"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Company'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCompanyModal;
