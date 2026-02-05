import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const MetricCard = ({ title, value, icon, trend, format = 'number' }) => {
  const formatValue = (val) => {
    if (val === null || val === undefined) return 'N/A';
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          maximumFractionDigits: 0,
        }).format(val);
      
      case 'percentage':
        return `${(val * 100).toFixed(1)}%`;
      
      case 'ratio':
        return val.toFixed(2);
      
      default:
        return new Intl.NumberFormat('en-IN').format(val);
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-success-600" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-danger-600" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-success-600 bg-success-50';
      case 'down':
        return 'text-danger-600 bg-danger-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="metric-card">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            {icon}
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="metric-value">{formatValue(value)}</p>
          </div>
        </div>
        
        {trend && (
          <div className={`flex items-center px-2 py-1 rounded-full ${getTrendColor()}`}>
            {getTrendIcon()}
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;
