import React, { useState, useEffect } from 'react';
import { useCompany } from '../../contexts/CompanyContext';
import axios from 'axios';
import { FileText, Download, Upload, RefreshCw, AlertCircle, CheckCircle, Clock, File, FileDown, Plus } from 'lucide-react';

const Reports = () => {
  const { selectedCompany } = useCompany();
  const [reports, setReports] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  // Fetch reports and documents
  const fetchData = async () => {
    if (!selectedCompany) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const [reportsResponse, documentsResponse] = await Promise.all([
        axios.get('/api/reports'),
        axios.get('/api/documents')
      ]);
      
      setReports(reportsResponse.data.reports || []);
      setDocuments(documentsResponse.data.documents || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch reports:', err);
      setError('Failed to load reports and documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // Listen for refresh events after upload
    const handleRefresh = () => {
      fetchData();
    };
    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('dataUploaded', handleRefresh);

    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('dataUploaded', handleRefresh);
    };
  }, [selectedCompany]);

  const generateReport = async (reportType = 'Full Report') => {
    try {
      setGenerating(true);
      const response = await axios.post('/api/reports/generate', null, {
        params: { report_type: reportType }
      });
      
      // Refresh reports after generation
      fetchData();
      
      // Show success message
      alert(`Report generated successfully! Version ${response.data.version_number}`);
    } catch (err) {
      console.error('Failed to generate report:', err);
      alert('Failed to generate report. Please ensure you have uploaded financial data.');
    } finally {
      setGenerating(false);
    }
  };

  const downloadReport = async (reportId, fileType) => {
    try {
      const response = await axios.get(`/api/reports/${reportId}/download/${fileType}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `report_${fileType}.${fileType}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download report:', err);
      alert('Failed to download report');
    }
  };

  const downloadDocument = async (documentId) => {
    try {
      const response = await axios.get(`/api/documents/${documentId}/download`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'uploaded_file';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download document:', err);
      alert('Failed to download document');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Processed': return 'text-green-600 bg-green-100';
      case 'Pending': return 'text-yellow-600 bg-yellow-100';
      case 'Failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Processed': return <CheckCircle className="w-4 h-4" />;
      case 'Pending': return <Clock className="w-4 h-4" />;
      case 'Failed': return <AlertCircle className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getScoreColor = (score, type) => {
    if (type === 'health') {
      if (score >= 80) return 'text-green-600';
      if (score >= 60) return 'text-yellow-600';
      if (score >= 40) return 'text-orange-600';
      return 'text-red-600';
    } else if (type === 'risk') {
      if (score <= 30) return 'text-green-600';
      if (score <= 60) return 'text-yellow-600';
      return 'text-red-600';
    } else if (type === 'credit') {
      if (score >= 700) return 'text-green-600';
      if (score >= 600) return 'text-yellow-600';
      return 'text-red-600';
    }
    return 'text-gray-600';
  };

  if (!selectedCompany) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">Please select a company to view reports</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <div className="text-gray-500 mt-4">Loading reports...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports & Documents</h1>
        <p className="text-gray-600 mt-1">Generate investor-ready reports and view document history</p>
      </div>

      {/* Generate New Report */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Generate New Report</h3>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => generateReport('Full Report')}
            disabled={generating}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="w-4 h-4" />
            <span>{generating ? 'Generating...' : 'Generate Full Report'}</span>
          </button>
          <button
            onClick={() => generateReport('Risk Only')}
            disabled={generating}
            className="flex items-center space-x-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <AlertCircle className="w-4 h-4" />
            <span>{generating ? 'Generating...' : 'Risk Report'}</span>
          </button>
          <button
            onClick={() => generateReport('Credit Only')}
            disabled={generating}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FileText className="w-4 h-4" />
            <span>{generating ? 'Generating...' : 'Credit Report'}</span>
          </button>
        </div>
      </div>

      {/* Report History */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Report History</h3>
        {reports.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <div className="text-gray-500">No reports generated yet</div>
            <p className="text-gray-400 text-sm mt-2">Generate your first report above</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Generated</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Health</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Credit</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Downloads</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reports.map((report) => (
                  <tr key={report.report_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      v{report.version_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(report.generated_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={getScoreColor(report.health_score, 'health')}>
                        {report.health_score?.toFixed(1) || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={getScoreColor(report.risk_score, 'risk')}>
                        {report.risk_score?.toFixed(1) || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div>
                        <span className={getScoreColor(report.credit_score, 'credit')}>
                          {report.credit_score?.toFixed(0) || 'N/A'}
                        </span>
                        {report.credit_rating && (
                          <span className="ml-2 text-xs text-gray-500">({report.credit_rating})</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => downloadReport(report.report_id, 'pdf')}
                          className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                        >
                          <FileDown className="w-4 h-4" />
                          <span>PDF</span>
                        </button>
                        <button
                          onClick={() => downloadReport(report.report_id, 'json')}
                          className="text-green-600 hover:text-green-800 flex items-center space-x-1"
                        >
                          <FileDown className="w-4 h-4" />
                          <span>JSON</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Uploaded Documents History */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Uploaded Documents History</h3>
        {documents.length === 0 ? (
          <div className="text-center py-8">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <div className="text-gray-500">No documents uploaded yet</div>
            <p className="text-gray-400 text-sm mt-2">Upload financial data to get started</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Upload Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.document_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {doc.file_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doc.file_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(doc.upload_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(doc.processing_status)}`}>
                        {getStatusIcon(doc.processing_status)}
                        <span className="ml-1">{doc.processing_status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button
                        onClick={() => downloadDocument(doc.document_id)}
                        className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                      >
                        <Download className="w-4 h-4" />
                        <span>Download</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;
