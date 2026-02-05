import React, { useState, useCallback } from 'react';
import { useCompany } from '../../contexts/CompanyContext';
import { useFinancialData } from '../../contexts/FinancialDataContext';
import { Upload, FileText, AlertCircle, CheckCircle, X } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const ALLOWED_TYPES = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/pdf'];
const ALLOWED_EXTS = ['.csv', '.xlsx', '.xls', '.pdf'];
const MAX_SIZE_MB = 10;

const DataUpload = () => {
  const { selectedCompany } = useCompany();
  const { refreshAfterUpload } = useFinancialData();
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState(null); // null | 'processing' | 'success' | 'error'
  const [message, setMessage] = useState('');

  const validateFile = (f) => {
    if (!ALLOWED_EXTS.some(ext => f.name.toLowerCase().endsWith(ext))) {
      toast.error('Only CSV, XLSX, and text-based PDF files are allowed');
      return false;
    }
    if (!ALLOWED_TYPES.includes(f.type) && !f.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Invalid file type');
      return false;
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      toast.error(`File size must be under ${MAX_SIZE_MB}MB`);
      return false;
    }
    return true;
  };

  const handleFile = (f) => {
    if (validateFile(f)) {
      setFile(f);
      setStatus(null);
      setMessage('');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleUpload = useCallback(async () => {
    if (!file || !selectedCompany) return;
    
    setUploading(true);
    setStatus('processing');
    setMessage('Uploading and processing your financial data...');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('company_id', selectedCompany.id);
      // Add default values for required fields
      formData.append('period', 'current');
      formData.append('data_type', 'financial_statements');
      
      const response = await axios.post('/api/data/upload', formData);
      
      setStatus('success');
      setMessage(response.data.message || 'File uploaded and processed successfully!');
      
      // Trigger centralized data refresh
      refreshAfterUpload();
      
      // Also trigger legacy events for backward compatibility
      window.dispatchEvent(new CustomEvent('dataUploaded', { detail: response.data }));
      window.dispatchEvent(new CustomEvent('refreshDashboard', { detail: response.data }));
    } catch (err) {
      console.error('Upload error:', err);
      setStatus('error');
      setMessage(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [file, selectedCompany, refreshAfterUpload]);

  const reset = () => {
    setFile(null);
    setStatus(null);
    setMessage('');
  };

  if (!selectedCompany) {
    return (
      <div className="text-center py-12">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 max-w-md mx-auto">
          <AlertCircle className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">No Company Selected</h3>
          <p className="text-yellow-700">Please select a company to upload financial data.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-sm p-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Financial Data</h2>
          <p className="text-gray-600">
            Upload your financial statements in CSV, Excel, or PDF format. 
            The system will automatically process and analyze your data.
          </p>
        </div>

        {/* Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive 
              ? 'border-blue-400 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          {!file && (
            <input
              type="file"
              accept=".csv,.xlsx,.xls,.pdf"
              onChange={handleChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={uploading}
            />
          )}
          
          {file ? (
            <div className="space-y-4">
              <FileText className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{file.name}</h3>
              <p className="text-sm text-gray-600 mb-4">
                {(file.size / 1024 / 1024).toFixed(2)} MB • {file.type || 'Unknown type'}
              </p>
              <div className="flex gap-3">
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Processing...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <Upload className="w-5 h-5 mr-2" />
                      Upload and Process
                    </div>
                  )}
                </button>
                <button
                  onClick={reset}
                  disabled={uploading}
                  className="px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Drop your file here</h3>
              <p className="text-gray-600 mb-4">
                or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supported formats: CSV, XLSX, XLS, PDF (Max {MAX_SIZE_MB}MB)
              </p>
            </div>
          )}
        </div>

        {/* Status Messages */}
        {status && (
          <div className={`mt-6 p-4 rounded-lg ${
            status === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-800'
              : status === 'error'
              ? 'bg-red-50 border border-red-200 text-red-800'
              : 'bg-blue-50 border border-blue-200 text-blue-800'
          }`}>
            <div className="flex items-center">
              {status === 'success' && <CheckCircle className="w-5 h-5 mr-3" />}
              {status === 'error' && <AlertCircle className="w-5 h-5 mr-3" />}
              {status === 'processing' && (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
              )}
              <div>
                <p className="font-medium">{typeof message === 'string' ? message : JSON.stringify(message)}</p>
                {status === 'success' && (
                  <p className="text-sm mt-1 text-green-700">
                    Your dashboard has been updated with the latest data.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Reset Button */}
        {file && !uploading && (
          <div className="mt-4 text-center">
            <button
              onClick={reset}
              className="text-blue-600 hover:text-blue-800 font-medium text-sm"
            >
              <X className="w-4 h-4 inline mr-2" />
              Clear File
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataUpload;
