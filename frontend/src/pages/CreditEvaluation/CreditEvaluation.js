import React, { useState, useEffect } from 'react';
import { useCompany } from '../../contexts/CompanyContext';
import axios from 'axios';
import { TrendingUp, AlertTriangle, CheckCircle, AlertCircle, Target, Shield, Activity, Zap } from 'lucide-react';

const CreditEvaluation = () => {
  const { selectedCompany } = useCompany();
  const [creditData, setCreditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch credit evaluation data
  useEffect(() => {
    const fetchCreditData = async () => {
      if (!selectedCompany) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await axios.get('/api/credit-evaluation');
        setCreditData(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch credit evaluation:', err);
        setError('Failed to load credit evaluation data');
      } finally {
        setLoading(false);
      }
    };

    fetchCreditData();

    // Listen for refresh events after upload
    const handleRefresh = () => {
      fetchCreditData();
    };
    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('dataUploaded', handleRefresh);

    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('dataUploaded', handleRefresh);
    };
  }, [selectedCompany]);

  const getRatingColor = (rating) => {
    switch (rating) {
      case 'AAA': return 'text-green-600 bg-green-100 border-green-200';
      case 'AA': return 'text-emerald-600 bg-emerald-100 border-emerald-200';
      case 'A': return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'BBB': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'BB': return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'High Risk': return 'text-red-600 bg-red-100 border-red-200';
      default: return 'text-gray-500 bg-gray-100 border-gray-200';
    }
  };

  const getEligibilityColor = (status) => {
    switch (status) {
      case 'Eligible': return 'text-green-600 bg-green-100';
      case 'Conditional': return 'text-yellow-600 bg-yellow-100';
      case 'Not Eligible': return 'text-red-600 bg-red-100';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 800) return 'bg-green-500';
    if (score >= 700) return 'bg-emerald-500';
    if (score >= 600) return 'bg-blue-500';
    if (score >= 500) return 'bg-yellow-500';
    if (score >= 400) return 'bg-orange-500';
    return 'bg-red-500';
  };

  if (!selectedCompany) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">Please select a company to view credit evaluation</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <div className="text-gray-500 mt-4">Loading credit evaluation...</div>
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

  if (!creditData || creditData.credit_score === null) {
    return (
      <div className="text-center py-12">
        <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <div className="text-gray-500 text-lg">Upload financial data to generate credit score</div>
        <p className="text-gray-400 mt-2">We need at least 2 months of data to evaluate creditworthiness</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Credit Evaluation</h1>
        <p className="text-gray-600 mt-1">Comprehensive credit scoring and loan readiness assessment</p>
      </div>

      {/* Credit Score Display */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Credit Score</h2>
            <div className="flex items-center space-x-3 mt-2">
              <span className="text-4xl font-bold text-gray-900">
                {creditData.credit_score.toFixed(0)}
              </span>
              <span className="text-sm text-gray-500">/ 900</span>
            </div>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mt-2 ${getRatingColor(creditData.credit_rating)}`}>
              {creditData.credit_rating}
            </div>
          </div>
          
          {/* Score Progress Bar */}
          <div className="flex-1 ml-8">
            <div className="text-sm text-gray-600 mb-2">Score Progress</div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className={`h-4 rounded-full transition-all duration-500 ${getScoreColor(creditData.credit_score)}`}
                style={{ width: `${(creditData.credit_score / 900) * 100}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0</span>
              <span>450</span>
              <span>900</span>
            </div>
          </div>
        </div>
      </div>

      {/* Loan Eligibility */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Loan Eligibility</h3>
        <div className="flex items-center justify-between">
          <div>
            <div className={`inline-flex items-center px-4 py-2 rounded-lg font-semibold ${getEligibilityColor(creditData.loan_eligibility_status)}`}>
              {creditData.loan_eligibility_status}
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Repayment Capacity: {creditData.repayment_capacity_ratio ? (creditData.repayment_capacity_ratio * 100).toFixed(1) + '%' : 'N/A'}
            </p>
          </div>
          {creditData.loan_eligibility_status === 'Eligible' && (
            <CheckCircle className="w-12 h-12 text-green-500" />
          )}
          {creditData.loan_eligibility_status === 'Conditional' && (
            <AlertCircle className="w-12 h-12 text-yellow-500" />
          )}
          {creditData.loan_eligibility_status === 'Not Eligible' && (
            <AlertTriangle className="w-12 h-12 text-red-500" />
          )}
        </div>
      </div>

      {/* Component Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              <span className="font-medium text-gray-900">Profitability</span>
            </div>
            <span className="text-sm font-bold text-gray-900">
              {creditData.component_scores.profitability?.toFixed(0) || 'N/A'}/200
            </span>
          </div>
          <div className="text-sm text-gray-600">
            Net Margin: {creditData.component_details.net_margin ? (creditData.component_details.net_margin * 100).toFixed(1) + '%' : 'N/A'}
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-blue-500 transition-all duration-500"
              style={{ width: `${(creditData.component_scores.profitability || 0) / 2}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-green-500" />
              <span className="font-medium text-gray-900">Liquidity</span>
            </div>
            <span className="text-sm font-bold text-gray-900">
              {creditData.component_scores.liquidity?.toFixed(0) || 'N/A'}/200
            </span>
          </div>
          <div className="text-sm text-gray-600">
            Current Ratio: {creditData.component_details.current_ratio?.toFixed(2) || 'N/A'}
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-green-500 transition-all duration-500"
              style={{ width: `${(creditData.component_scores.liquidity || 0) / 2}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <span className="font-medium text-gray-900">Leverage</span>
            </div>
            <span className="text-sm font-bold text-gray-900">
              {creditData.component_scores.leverage?.toFixed(0) || 'N/A'}/200
            </span>
          </div>
          <div className="text-sm text-gray-600">
            D/E Ratio: {creditData.component_details.debt_to_equity?.toFixed(2) || 'N/A'}
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-red-500 transition-all duration-500"
              style={{ width: `${(creditData.component_scores.leverage || 0) / 2}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-purple-500" />
              <span className="font-medium text-gray-900">Cash Flow</span>
            </div>
            <span className="text-sm font-bold text-gray-900">
              {creditData.component_scores.cash_flow?.toFixed(0) || 'N/A'}/200
            </span>
          </div>
          <div className="text-sm text-gray-600">
            Stability: {creditData.component_details.cash_flow_stability ? 'Low' : 'High'} Volatility
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-purple-500 transition-all duration-500"
              style={{ width: `${(creditData.component_scores.cash_flow || 0) / 2}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-emerald-500" />
              <span className="font-medium text-gray-900">Growth</span>
            </div>
            <span className="text-sm font-bold text-gray-900">
              {creditData.component_scores.growth?.toFixed(0) || 'N/A'}/100
            </span>
          </div>
          <div className="text-sm text-gray-600">
            Growth Rate: {creditData.component_details.revenue_growth_rate ? (creditData.component_details.revenue_growth_rate * 100).toFixed(1) + '%' : 'N/A'}
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-emerald-500 transition-all duration-500"
              style={{ width: `${creditData.component_scores.growth || 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Risk Flags */}
      {creditData.risk_flags && creditData.risk_flags.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Flags</h3>
          <div className="space-y-2">
            {creditData.risk_flags.map((flag, index) => (
              <div key={index} className="flex items-center space-x-2 p-2 bg-red-50 rounded-lg border border-red-200">
                <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
                <span className="text-sm text-red-700">{flag}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Improvement Recommendations */}
      {creditData.improvement_recommendations && creditData.improvement_recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Improvement Recommendations</h3>
          <div className="space-y-3">
            {creditData.improvement_recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <Zap className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-700">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Last Updated */}
      {creditData.last_updated && (
        <div className="text-center text-sm text-gray-500">
          Last updated: {new Date(creditData.last_updated).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default CreditEvaluation;
