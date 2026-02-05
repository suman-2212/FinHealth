import React from 'react';
import { Lightbulb, TrendingUp, AlertTriangle, Target } from 'lucide-react';

const AIInsights = () => {
  const insights = [
    {
      type: 'positive',
      icon: TrendingUp,
      title: 'Revenue Growth',
      description: 'Your revenue has increased by 15% compared to the previous quarter, indicating strong business performance.',
      action: 'Continue focusing on high-performing product lines'
    },
    {
      type: 'warning',
      icon: AlertTriangle,
      title: 'Cash Flow Concern',
      description: 'Operating cash flow has decreased by 20% this month. Monitor accounts receivable collection.',
      action: 'Review payment terms and follow up on overdue invoices'
    },
    {
      type: 'recommendation',
      icon: Target,
      title: 'Cost Optimization Opportunity',
      description: 'Administrative expenses are 8% higher than industry average. Consider process automation.',
      action: 'Implement digital tools to reduce manual overhead'
    }
  ];

  const getInsightColor = (type) => {
    switch (type) {
      case 'positive':
        return 'text-success-600 bg-success-50 border-success-200';
      case 'warning':
        return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'recommendation':
        return 'text-primary-600 bg-primary-50 border-primary-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getIconColor = (type) => {
    switch (type) {
      case 'positive':
        return 'text-success-600';
      case 'warning':
        return 'text-warning-600';
      case 'recommendation':
        return 'text-primary-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-header">
        <div className="flex items-center space-x-2">
          <Lightbulb className="w-5 h-5 text-primary-600" />
          <h3 className="chart-title">AI-Powered Insights</h3>
        </div>
        <button className="btn btn-sm btn-outline">View All</button>
      </div>
      
      <div className="space-y-4">
        {insights.map((insight, index) => {
          const Icon = insight.icon;
          return (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getInsightColor(insight.type)}`}
            >
              <div className="flex items-start space-x-3">
                <div className={`flex-shrink-0 ${getIconColor(insight.type)}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">
                    {insight.title}
                  </h4>
                  <p className="text-sm text-gray-600 mb-2">
                    {insight.description}
                  </p>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-medium text-gray-500">
                      Recommended Action:
                    </span>
                    <span className="text-xs font-medium">
                      {insight.action}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Last updated: 2 hours ago
          </div>
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            Refresh Insights
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIInsights;
