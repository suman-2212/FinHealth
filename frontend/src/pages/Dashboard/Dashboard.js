import React, { useEffect } from 'react';
import { useCompany } from '../../contexts/CompanyContext';
import { useFinancialData } from '../../contexts/FinancialDataContext';
import { 
  TrendingUp, 
  DollarSign, 
  Target,
  Activity,
  BarChart3
} from 'lucide-react';
import MetricCard from '../../components/Dashboard/MetricCard';
import RevenueChart from '../../components/Dashboard/RevenueChart';
import CashFlowChart from '../../components/Dashboard/CashFlowChart';
import RiskGauge from '../../components/Dashboard/RiskGauge';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Dashboard = () => {
  const { selectedCompany } = useCompany();
  const { dashboardSummary, loading, fetchAllFinancialData } = useFinancialData();

  useEffect(() => {
    if (selectedCompany) {
      fetchAllFinancialData(selectedCompany.id);
    }
  }, [selectedCompany, fetchAllFinancialData]);

  if (!selectedCompany) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">Please select a company to view the dashboard</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const metrics = dashboardSummary || {};
  const trends = {
    revenue_change: dashboardSummary?.revenue_trend?.length > 1 ? 
      dashboardSummary.revenue_trend[dashboardSummary.revenue_trend.length - 1][1] - dashboardSummary.revenue_trend[dashboardSummary.revenue_trend.length - 2][1] : 0,
    net_income_change: dashboardSummary?.cash_flow_trend?.length > 1 ? 
      dashboardSummary.cash_flow_trend[dashboardSummary.cash_flow_trend.length - 1][1] - dashboardSummary.cash_flow_trend[dashboardSummary.cash_flow_trend.length - 2][1] : 0,
    assets_change: 0, // No assets trend data available
    health_score_change: dashboardSummary?.health_trend?.length > 1 ? 
      dashboardSummary.health_trend[dashboardSummary.health_trend.length - 1][1] - dashboardSummary.health_trend[dashboardSummary.health_trend.length - 2][1] : 0,
    current_ratio: dashboardSummary?.current_ratio || 0,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Financial Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Overview of your company's financial health and performance metrics
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Revenue"
          value={metrics.revenue}
          change={trends.revenue_change}
          icon={<DollarSign className="w-6 h-6" />}
          format="currency"
        />
        <MetricCard
          title="Net Income"
          value={metrics.net_income}
          change={trends.net_income_change}
          icon={<TrendingUp className="w-6 h-6" />}
          format="currency"
        />
        <MetricCard
          title="Total Assets"
          value={metrics.total_assets}
          change={trends.assets_change}
          icon={<Activity className="w-6 h-6" />}
          format="currency"
        />
        <MetricCard
          title="Current Ratio"
          value={trends.current_ratio}
          icon={<BarChart3 className="w-6 h-6" />}
          format="ratio"
        />
        <MetricCard
          title="Health Score"
          value={metrics.financial_health_score}
          change={trends.health_score_change}
          icon={<Target className="w-6 h-6" />}
          format="number"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Revenue Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Revenue Trend</h2>
          <RevenueChart data={dashboardSummary?.revenue_trend?.map(([month, value]) => ({ month, revenue: value })) || []} />
        </div>

        {/* Cash Flow Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Cash Flow Analysis</h2>
          <CashFlowChart data={dashboardSummary?.cash_flow_trend?.map(([month, value]) => ({ month, cash_flow: value })) || []} />
        </div>
      </div>

      {/* Risk & AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Debt Risk Level */}
          <div className="bg-white p-6 rounded-lg shadow-md flex flex-col items-center justify-center">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Debt Risk Level</h2>
            <RiskGauge 
              value={metrics.debt_to_equity || 0} // Use debt-to-equity ratio for risk gauge
            />
          </div>

          {/* Financial Health Score */}
          <div className="bg-white p-6 rounded-lg shadow-md flex flex-col items-center justify-center">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Health Score</h2>
            <div className={`text-5xl font-bold ${metrics.financial_health_score >= 80 ? 'text-green-600' : metrics.financial_health_score >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
              {metrics.financial_health_score ? metrics.financial_health_score.toFixed(0) : 'N/A'}
            </div>
            <p className="text-sm text-gray-500 mt-2">Out of 100</p>
          </div>

          {/* Key Ratios */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Ratios</h2>
            <ul className="space-y-2">
              <li className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Net Profit Margin:</span>
                <span className="font-medium text-gray-900">{metrics.net_profit_margin ? (metrics.net_profit_margin * 100).toFixed(2) + '%' : 'N/A'}</span>
              </li>
              <li className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Return on Assets:</span>
                <span className="font-medium text-gray-900">{metrics.return_on_assets ? (metrics.return_on_assets * 100).toFixed(2) + '%' : 'N/A'}</span>
              </li>
              <li className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Debt to Equity Ratio:</span>
                <span className="font-medium text-gray-900">{metrics.debt_to_equity ? metrics.debt_to_equity.toFixed(2) : 'N/A'}</span>
              </li>
            </ul>
          </div>
        </div>

      {/* AI-Powered Insights */}
      <div className="bg-white p-8 rounded-lg shadow-lg mb-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-gray-900">AI-Powered Insights</h2>
          </div>
          <button className="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            View All
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Revenue Growth Insight */}
          <div className="bg-green-50 p-4 rounded-lg border border-green-200 hover:shadow-md transition-all hover:-translate-y-1 cursor-pointer">
            <div className="flex items-center mb-3">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mr-2">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900">Revenue Growth</h3>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Your revenue has increased by 12% compared to the previous quarter, indicating strong market performance and effective sales strategies.
            </p>
            <div className="text-sm font-medium text-green-700">
              Recommended Action: Consider expanding sales team to capitalize on growth momentum
            </div>
          </div>

          {/* Cash Flow Concern */}
          <div className="bg-amber-50 p-4 rounded-lg border border-amber-200 hover:shadow-md transition-all hover:-translate-y-1 cursor-pointer">
            <div className="flex items-center mb-3">
              <div className="w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center mr-2">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900">Cash Flow Concern</h3>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Operating cash flow has decreased by 8% this month, potentially affecting your ability to meet short-term obligations.
            </p>
            <div className="text-sm font-medium text-amber-700">
              Recommended Action: Review accounts receivable and accelerate collection processes
            </div>
          </div>

          {/* Cost Optimization */}
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 hover:shadow-md transition-all hover:-translate-y-1 cursor-pointer">
            <div className="flex items-center mb-3">
              <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center mr-2">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900">Cost Optimization</h3>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Analysis reveals potential 15% cost reduction opportunities in operational expenses without impacting service quality.
            </p>
            <div className="text-sm font-medium text-blue-700">
              Recommended Action: Conduct operational efficiency audit and implement automation
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
