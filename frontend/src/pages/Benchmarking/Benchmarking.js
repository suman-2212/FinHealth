import React, { useState, useEffect } from 'react';
import { useCompany } from '../../contexts/CompanyContext';
import axios from 'axios';
import { TrendingUp, BarChart3, PieChart, FileText, Download, Filter, Calendar } from 'lucide-react';

const Benchmarking = () => {
  const { selectedCompany } = useCompany();
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch benchmark data
  useEffect(() => {
    const fetchBenchmarkData = async () => {
      if (!selectedCompany) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await axios.get('/api/benchmark');
        setBenchmarkData(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch benchmark data:', err);
        setError('Failed to load benchmark data');
      } finally {
        setLoading(false);
      }
    };

    fetchBenchmarkData();

    // Listen for refresh events after upload
    const handleRefresh = () => {
      fetchBenchmarkData();
    };
    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('dataUploaded', handleRefresh);

    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('dataUploaded', handleRefresh);
    };
  }, [selectedCompany]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Top 25%': return 'text-green-600 bg-green-100';
      case 'Above Average': return 'text-emerald-600 bg-emerald-100';
      case 'Near Average': return 'text-yellow-600 bg-yellow-100';
      case 'Below Average': return 'text-orange-600 bg-orange-100';
      case 'Bottom 25%': return 'text-red-600 bg-red-100';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  const getPercentileColor = (percentile) => {
    if (percentile >= 75) return 'bg-green-500';
    if (percentile >= 60) return 'bg-emerald-500';
    if (percentile >= 40) return 'bg-yellow-500';
    if (percentile >= 25) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getDeviationIcon = (deviation) => {
    if (deviation > 5) return <ArrowUp className="w-4 h-4 text-green-500" />;
    if (deviation < -5) return <ArrowDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  const formatMetricValue = (metricName, value) => {
    if (value === null || value === undefined) return 'N/A';
    
    switch (metricName) {
      case 'net_profit_margin':
      case 'gross_margin':
      case 'operating_margin':
      case 'revenue_growth_rate':
        return (value * 100).toFixed(1) + '%';
      case 'current_ratio':
      case 'quick_ratio':
      case 'debt_to_equity':
        return value.toFixed(2);
      case 'cash_conversion_cycle':
        return Math.round(value) + ' days';
      default:
        return value.toFixed(2);
    }
  };

  const getMetricLabel = (metricName) => {
    const labels = {
      'net_profit_margin': 'Net Profit Margin',
      'gross_margin': 'Gross Margin',
      'operating_margin': 'Operating Margin',
      'current_ratio': 'Current Ratio',
      'quick_ratio': 'Quick Ratio',
      'debt_to_equity': 'Debt-to-Equity',
      'revenue_growth_rate': 'Revenue Growth Rate',
      'cash_conversion_cycle': 'Cash Conversion Cycle'
    };
    return labels[metricName] || metricName;
  };

  if (!selectedCompany) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">Please select a company to view benchmarking</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <div className="text-gray-500 mt-4">Loading benchmark data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  if (!benchmarkData || !benchmarkData.benchmark_results || Object.keys(benchmarkData.benchmark_results).length === 0) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <div className="text-gray-500 text-lg">Upload financial data to generate benchmarking analysis</div>
        <p className="text-gray-400 mt-2">We need financial data to compare against industry benchmarks</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Industry Benchmarking</h1>
        <p className="text-gray-600 mt-1">Compare your performance against industry standards</p>
      </div>

      {/* Industry Position Summary */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Industry Position Summary</h3>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-gray-600 mb-1">Industry</div>
            <div className="text-lg font-medium text-gray-900">{benchmarkData.industry_type}</div>
            <div className="text-sm text-gray-500">{benchmarkData.industry_description}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-1">Overall Percentile</div>
            <div className="text-3xl font-bold text-gray-900">
              {benchmarkData.overall_summary.overall_percentile.toFixed(0)}th
            </div>
            <div className="text-sm text-gray-500 mt-1">
              {benchmarkData.overall_summary.metrics_above_avg} of {benchmarkData.overall_summary.total_metrics} metrics above average
            </div>
          </div>
        </div>
        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-700">{benchmarkData.overall_summary.summary_text}</p>
        </div>
      </div>

      {/* Benchmark Comparison Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Comparison</h3>
        <div className="space-y-4">
          {Object.entries(benchmarkData.benchmark_results).map(([metricName, result]) => (
            <div key={metricName} className="border-b border-gray-200 pb-4 last:border-0">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-900">{getMetricLabel(metricName)}</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(result.status)}`}>
                  {result.status}
                </span>
              </div>
              
              {/* Comparison Values */}
              <div className="grid grid-cols-3 gap-4 mb-2">
                <div>
                  <div className="text-xs text-gray-500">Your Value</div>
                  <div className="text-sm font-semibold text-gray-900">
                    {formatMetricValue(metricName, result.value)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Industry Avg</div>
                  <div className="text-sm font-medium text-gray-600">
                    {formatMetricValue(metricName, result.industry_avg)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Percentile</div>
                  <div className="text-sm font-medium text-gray-900">
                    {result.percentile.toFixed(0)}th
                  </div>
                </div>
              </div>
              
              {/* Progress Bar and Deviation */}
              <div className="flex items-center space-x-3">
                <div className="flex-1">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${getPercentileColor(result.percentile)}`}
                      style={{ width: `${result.percentile}%` }}
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  {getDeviationIcon(result.deviation_percent)}
                  <span className={`text-xs font-medium ${
                    result.deviation_percent > 0 ? 'text-green-600' : 
                    result.deviation_percent < 0 ? 'text-red-600' : 'text-gray-500'
                  }`}>
                    {result.deviation_percent > 0 ? '+' : ''}{result.deviation_percent.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Last Updated */}
      {benchmarkData.last_updated && (
        <div className="text-center text-sm text-gray-500">
          Last updated: {new Date(benchmarkData.last_updated).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default Benchmarking;
