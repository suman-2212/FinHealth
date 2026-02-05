import React, { useState, useEffect } from 'react';
import { useCompany } from '../../contexts/CompanyContext';
import axios from 'axios';
import { AlertTriangle, Shield, TrendingDown, Activity, Target, CheckCircle, AlertCircle } from 'lucide-react';

const RiskAnalysis = () => {
  const { selectedCompany } = useCompany();
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch risk analysis data
  useEffect(() => {
    const fetchRiskData = async () => {
      if (!selectedCompany) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await axios.get('/api/risk-analysis');
        setRiskData(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch risk analysis:', err);
        setError('Failed to load risk analysis data');
      } finally {
        setLoading(false);
      }
    };

    fetchRiskData();

    // Listen for refresh events after upload
    const handleRefresh = () => {
      fetchRiskData();
    };
    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('dataUploaded', handleRefresh);

    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('dataUploaded', handleRefresh);
    };
  }, [selectedCompany]);

  const getRiskColor = (level) => {
    switch (level) {
      case 'Low': return 'text-green-600 bg-green-100 border-green-200';
      case 'Moderate': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'High': return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'Critical': return 'text-red-600 bg-red-100 border-red-200';
      default: return 'text-gray-500 bg-gray-100 border-gray-200';
    }
  };

  const getRiskIcon = (level) => {
    switch (level) {
      case 'Low': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'Moderate': return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'High': return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      case 'Critical': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default: return <Activity className="w-5 h-5 text-gray-400" />;
    }
  };

  const getScoreColor = (score) => {
    if (score <= 30) return 'bg-green-500';
    if (score <= 50) return 'bg-yellow-500';
    if (score <= 70) return 'bg-orange-500';
    return 'bg-red-500';
  };

  if (!selectedCompany) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">Please select a company to view risk analysis</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <div className="text-gray-500 mt-4">Loading risk analysis...</div>
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

  if (!riskData || riskData.overall_risk_score === null) {
    return (
      <div className="text-center py-12">
        <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <div className="text-gray-500 text-lg">No financial data available</div>
        <p className="text-gray-400 mt-2">Upload financial data to generate risk analysis</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Risk Analysis</h1>
        <p className="text-gray-600 mt-1">Comprehensive assessment of financial risk factors</p>
      </div>

      {/* Overall Risk Badge */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Overall Risk Level</h2>
            <div className="flex items-center space-x-3 mt-2">
              {getRiskIcon(riskData.overall_risk_level)}
              <span className={`text-2xl font-bold ${getRiskColor(riskData.overall_risk_level).split(' ')[0]}`}>
                {riskData.overall_risk_level}
              </span>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Risk Score: {riskData.overall_risk_score.toFixed(1)}/100
            </p>
          </div>
          
          {/* Risk Score Visualization */}
          <div className="w-32">
            <div className="text-center mb-2">
              <span className="text-3xl font-bold text-gray-900">
                {riskData.overall_risk_score.toFixed(0)}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${getScoreColor(riskData.overall_risk_score)}`}
                style={{ width: `${riskData.overall_risk_score}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Component Risk Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Leverage Risk */}
        <div className={`bg-white rounded-lg shadow-sm border p-4 ${getRiskColor(riskData.component_breakdown.leverage.level)}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Target className="w-5 h-5" />
              <span className="font-medium text-gray-900">Leverage Risk</span>
            </div>
            {getRiskIcon(riskData.component_breakdown.leverage.level)}
          </div>
          <div className="text-sm text-gray-600 mb-2">
            D/E Ratio: {riskData.component_breakdown.leverage.details.debt_to_equity?.toFixed(2) || 'N/A'}
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium">{riskData.component_breakdown.leverage.level}</span>
            <span className="text-xs font-bold">{riskData.component_breakdown.leverage.score?.toFixed(0) || 'N/A'}</span>
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getScoreColor(riskData.component_breakdown.leverage.score || 0)}`}
              style={{ width: `${riskData.component_breakdown.leverage.score || 0}%` }}
            />
          </div>
        </div>

        {/* Liquidity Risk */}
        <div className={`bg-white rounded-lg shadow-sm border p-4 ${getRiskColor(riskData.component_breakdown.liquidity.level)}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span className="font-medium text-gray-900">Liquidity Risk</span>
            </div>
            {getRiskIcon(riskData.component_breakdown.liquidity.level)}
          </div>
          <div className="text-sm text-gray-600 mb-2">
            Current Ratio: {riskData.component_breakdown.liquidity.details.current_ratio?.toFixed(2) || 'N/A'}
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium">{riskData.component_breakdown.liquidity.level}</span>
            <span className="text-xs font-bold">{riskData.component_breakdown.liquidity.score?.toFixed(0) || 'N/A'}</span>
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getScoreColor(riskData.component_breakdown.liquidity.score || 0)}`}
              style={{ width: `${riskData.component_breakdown.liquidity.score || 0}%` }}
            />
          </div>
        </div>

        {/* Profitability Risk */}
        <div className={`bg-white rounded-lg shadow-sm border p-4 ${getRiskColor(riskData.component_breakdown.profitability.level)}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <TrendingDown className="w-5 h-5" />
              <span className="font-medium text-gray-900">Profitability Risk</span>
            </div>
            {getRiskIcon(riskData.component_breakdown.profitability.level)}
          </div>
          <div className="text-sm text-gray-600 mb-2">
            Net Margin: {riskData.component_breakdown.profitability.details.net_margin ? (riskData.component_breakdown.profitability.details.net_margin * 100).toFixed(1) + '%' : 'N/A'}
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium">{riskData.component_breakdown.profitability.level}</span>
            <span className="text-xs font-bold">{riskData.component_breakdown.profitability.score?.toFixed(0) || 'N/A'}</span>
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getScoreColor(riskData.component_breakdown.profitability.score || 0)}`}
              style={{ width: `${riskData.component_breakdown.profitability.score || 0}%` }}
            />
          </div>
        </div>

        {/* Cash Flow Risk */}
        <div className={`bg-white rounded-lg shadow-sm border p-4 ${getRiskColor(riskData.component_breakdown.cash_flow.level)}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span className="font-medium text-gray-900">Cash Flow Risk</span>
            </div>
            {getRiskIcon(riskData.component_breakdown.cash_flow.level)}
          </div>
          <div className="text-sm text-gray-600 mb-2">
            Negative CF Months: {riskData.component_breakdown.cash_flow.details.negative_cash_flow_months || 0}
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium">{riskData.component_breakdown.cash_flow.level}</span>
            <span className="text-xs font-bold">{riskData.component_breakdown.cash_flow.score?.toFixed(0) || 'N/A'}</span>
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getScoreColor(riskData.component_breakdown.cash_flow.score || 0)}`}
              style={{ width: `${riskData.component_breakdown.cash_flow.score || 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Mitigation Actions */}
      {riskData.mitigation_actions && riskData.mitigation_actions.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Mitigation Actions</h3>
          <div className="space-y-3">
            {riskData.mitigation_actions.map((action, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-amber-50 rounded-lg border border-amber-200">
                <AlertTriangle className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-700">{action}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Last Updated */}
      {riskData.last_updated && (
        <div className="text-center text-sm text-gray-500">
          Last updated: {new Date(riskData.last_updated).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default RiskAnalysis;
