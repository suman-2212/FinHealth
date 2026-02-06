import React, { useState, useEffect } from 'react';
import { useCompany } from '../../contexts/CompanyContext';
import axios from 'axios';
import { TrendingUp, TrendingDown, Activity, AlertTriangle, BarChart3 } from 'lucide-react';

const Forecasting = () => {
  const { selectedCompany } = useCompany();
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [forecastType, setForecastType] = useState('Base');
  const [monthsAhead, setMonthsAhead] = useState(6);

  // Fetch forecast data
  useEffect(() => {
    const fetchForecastData = async () => {
      if (!selectedCompany) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await axios.get('/api/forecast', {
          params: { months_ahead: monthsAhead, forecast_type: forecastType }
        });
        setForecastData(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch forecast:', err);
        setError('Failed to load forecast data');
      } finally {
        setLoading(false);
      }
    };

    fetchForecastData();

    // Listen for refresh events after upload
    const handleRefresh = () => {
      fetchForecastData();
    };
    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('dataUploaded', handleRefresh);

    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('dataUploaded', handleRefresh);
    };
  }, [selectedCompany, monthsAhead, forecastType]);

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    if (score >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getRunwayColor = (months) => {
    if (months >= 12) return 'text-green-600';
    if (months >= 6) return 'text-yellow-600';
    if (months >= 3) return 'text-orange-600';
    return 'text-red-600';
  };

  if (!selectedCompany) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">Please select a company to view forecasts</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <div className="text-gray-500 mt-4">Loading forecast...</div>
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

  if (!forecastData || !forecastData.projections || forecastData.projections.length === 0) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <div className="text-gray-500 text-lg">Upload at least 3 months of financial data to generate projections</div>
        <p className="text-gray-400 mt-2">We need historical data to create accurate forecasts</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Financial Forecasting</h1>
        <p className="text-gray-600 mt-1">6-month projections and cash runway estimates</p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Forecast Type</label>
              <select
                value={forecastType}
                onChange={(e) => setForecastType(e.target.value)}
                className="ml-2 block w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="Base">Base</option>
                <option value="Optimistic">Optimistic</option>
                <option value="Conservative">Conservative</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Months Ahead</label>
              <select
                value={monthsAhead}
                onChange={(e) => setMonthsAhead(parseInt(e.target.value))}
                className="ml-2 block w-20 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              >
                <option value={6}>6</option>
                <option value={12}>12</option>
              </select>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Confidence:</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(forecastData.confidence_score)}`}>
              {forecastData.confidence_score?.toFixed(0) || 'N/A'}%
            </span>
          </div>
        </div>
      </div>

      {/* Cash Runway */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cash Runway</h3>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-3xl font-bold text-gray-900">
              {forecastData.runway_months !== null && forecastData.runway_months < 999
                ? `${forecastData.runway_months.toFixed(1)} months`
                : 'Infinite'}
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Estimated runway based on cash flow projections
            </p>
          </div>
          <div className={`text-2xl font-bold ${getRunwayColor(forecastData.runway_months)}`}>
            {forecastData.runway_months !== null && forecastData.runway_months < 999
              ? forecastData.runway_months >= 12 ? '✓' : '⚠'
              : '✓'}
          </div>
        </div>
      </div>

      {/* Revenue Projection Chart */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Projection</h3>
        <div className="space-y-3">
          {/* Historical + Projected Revenue */}
          <div className="space-y-2">
            {forecastData.historical_data && forecastData.historical_data.months &&
              forecastData.historical_data.months.slice(-3).map((month, index) => (
                <div key={month} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">{month}</span>
                  <span className="text-sm font-medium">
                    ${forecastData.historical_data.revenues[index + forecastData.historical_data.months.length - 3].toLocaleString()}
                  </span>
                </div>
              ))}
            {forecastData.projections && forecastData.projections.map((proj, index) => (
              <div key={proj.projection_month} className="flex items-center justify-between p-2 bg-blue-50 rounded border border-blue-200">
                <span className="text-sm text-blue-700">{proj.projection_month}</span>
                <span className="text-sm font-medium text-blue-700">
                  ${proj.projected_revenue.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Cash Flow Projection */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cash Flow Projection</h3>
        <div className="space-y-3">
          {forecastData.projections.map((proj) => (
            <div key={proj.projection_month} className="flex items-center justify-between p-3 rounded-lg border">
              <div className="flex items-center space-x-3">
                <Activity className={`w-5 h-5 ${proj.projected_cash_flow >= 0 ? 'text-green-500' : 'text-red-500'}`} />
                <span className="text-sm font-medium">{proj.projection_month}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`text-sm font-bold ${proj.projected_cash_flow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ${proj.projected_cash_flow.toLocaleString()}
                </span>
                {proj.projected_cash_flow >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Growth Rates */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Growth Assumptions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Revenue Growth Rate</p>
            <p className="text-lg font-semibold text-gray-900">
              {forecastData.revenue_growth_rate ? (forecastData.revenue_growth_rate * 100).toFixed(1) + '%' : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Expense Growth Rate</p>
            <p className="text-lg font-semibold text-gray-900">
              {forecastData.expense_growth_rate ? (forecastData.expense_growth_rate * 100).toFixed(1) + '%' : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Last Updated */}
      {forecastData.last_updated && (
        <div className="text-center text-sm text-gray-500">
          Last updated: {new Date(forecastData.last_updated).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default Forecasting;
