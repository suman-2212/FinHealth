import React, { useState, useEffect } from 'react';
import { useCompany } from '../../contexts/CompanyContext';
import axios from 'axios';
import { TrendingUp, AlertCircle, Activity, Target, Zap, Shield } from 'lucide-react';

const FinancialHealth = () => {
  const { selectedCompany } = useCompany();
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch financial health data
  useEffect(() => {
    const fetchHealthData = async () => {
      if (!selectedCompany) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await axios.get('/api/financial-health');
        setHealthData(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch financial health:', err);
        setError('Failed to load financial health data');
      } finally {
        setLoading(false);
      }
    };

    fetchHealthData();

    // Listen for refresh events after upload
    const handleRefresh = () => {
      fetchHealthData();
    };
    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('dataUploaded', handleRefresh);

    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('dataUploaded', handleRefresh);
    };
  }, [selectedCompany]);

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    if (score >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Excellent': return 'text-green-600';
      case 'Good': return 'text-blue-600';
      case 'Moderate': return 'text-yellow-600';
      case 'Weak': return 'text-orange-600';
      case 'Critical': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  const getProgressColor = (score) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  if (!selectedCompany) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">Please select a company to view financial health</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <div className="text-gray-500 mt-4">Loading financial health analysis...</div>
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

  if (!healthData || healthData.health_score === null) {
    return (
      <div className="text-center py-12">
        <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <div className="text-gray-500 text-lg">Upload financial data to generate health insights</div>
        <p className="text-gray-400 mt-2">We need at least 2 months of data to analyze your financial health</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Financial Health Analysis</h1>
        <p className="text-gray-600 mt-1">Comprehensive assessment of your company's financial stability</p>
      </div>

      {/* Main Score Display */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Overall Health Score</h2>
            <p className={`text-3xl font-bold mt-2 ${getCategoryColor(healthData.health_category)}`}>
              {healthData.health_score.toFixed(1)}/100
            </p>
            <p className={`text-sm font-medium mt-1 ${getCategoryColor(healthData.health_category)}`}>
              {healthData.health_category}
            </p>
          </div>

          {/* Circular Progress */}
          <div className="relative w-32 h-32">
            <svg className="transform -rotate-90 w-32 h-32">
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="12"
                fill="none"
                className="text-gray-200"
              />
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="12"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 56}`}
                strokeDashoffset={`${2 * Math.PI * 56 * (1 - healthData.health_score / 100)}`}
                className={`${getProgressColor(healthData.health_score).replace('bg-', 'text-')} transition-all duration-500`}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`text-2xl font-bold ${getCategoryColor(healthData.health_category)}`}>
                {healthData.health_score.toFixed(0)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Component Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-blue-500" />
              <span className="font-medium text-gray-900">Profitability</span>
            </div>
            {healthData.component_scores.profitability !== null && (
              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getScoreColor(healthData.component_scores.profitability)}`}>
                {healthData.component_scores.profitability.toFixed(0)}
              </span>
            )}
          </div>
          <div className="text-sm text-gray-600">
            Net Margin: {healthData.component_details.net_margin ? (healthData.component_details.net_margin * 100).toFixed(1) + '%' : 'N/A'}
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(healthData.component_scores.profitability || 0)}`}
              style={{ width: `${healthData.component_scores.profitability || 0}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-green-500" />
              <span className="font-medium text-gray-900">Liquidity</span>
            </div>
            {healthData.component_scores.liquidity !== null && (
              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getScoreColor(healthData.component_scores.liquidity)}`}>
                {healthData.component_scores.liquidity.toFixed(0)}
              </span>
            )}
          </div>
          <div className="text-sm text-gray-600">
            Current Ratio: {healthData.component_details.current_ratio?.toFixed(2) || 'N/A'}
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(healthData.component_scores.liquidity || 0)}`}
              style={{ width: `${healthData.component_scores.liquidity || 0}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <span className="font-medium text-gray-900">Leverage</span>
            </div>
            {healthData.component_scores.leverage !== null && (
              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getScoreColor(healthData.component_scores.leverage)}`}>
                {healthData.component_scores.leverage.toFixed(0)}
              </span>
            )}
          </div>
          <div className="text-sm text-gray-600">
            Debt to Equity: {healthData.component_details.debt_to_equity?.toFixed(2) || 'N/A'}
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(healthData.component_scores.leverage || 0)}`}
              style={{ width: `${healthData.component_scores.leverage || 0}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-purple-500" />
              <span className="font-medium text-gray-900">Cash Flow</span>
            </div>
            {healthData.component_scores.cash_flow !== null && (
              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getScoreColor(healthData.component_scores.cash_flow)}`}>
                {healthData.component_scores.cash_flow.toFixed(0)}
              </span>
            )}
          </div>
          <div className="text-sm text-gray-600">
            Stability: {healthData.component_details.cash_flow_stability ? 'Low' : 'High'} Volatility
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(healthData.component_scores.cash_flow || 0)}`}
              style={{ width: `${healthData.component_scores.cash_flow || 0}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-emerald-500" />
              <span className="font-medium text-gray-900">Growth</span>
            </div>
            {healthData.component_scores.growth !== null && (
              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getScoreColor(healthData.component_scores.growth)}`}>
                {healthData.component_scores.growth.toFixed(0)}
              </span>
            )}
          </div>
          <div className="text-sm text-gray-600">
            Growth Rate: {healthData.component_details.revenue_growth_rate ? (healthData.component_details.revenue_growth_rate * 100).toFixed(1) + '%' : 'N/A'}
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(healthData.component_scores.growth || 0)}`}
              style={{ width: `${healthData.component_scores.growth || 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Improvement Recommendations */}
      {healthData.improvement_recommendations && healthData.improvement_recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Improvement Recommendations</h3>
          <div className="space-y-3">
            {healthData.improvement_recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <Zap className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-700">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Last Updated */}
      {healthData.last_updated && (
        <div className="text-center text-sm text-gray-500">
          Last updated: {new Date(healthData.last_updated).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default FinancialHealth;
