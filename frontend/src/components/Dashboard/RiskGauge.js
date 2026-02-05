import React from 'react';

const RiskGauge = ({ value }) => {
  // Normalize value to 0-100 scale (assuming debt-to-equity ratio)
  // Lower is better, higher is riskier
  const normalizedValue = Math.min(100, (value / 3) * 100); // 3.0 = 100% risk
  
  const getRiskLevel = (val) => {
    if (val < 33) return { level: 'Low', color: '#10b981', badgeColor: 'text-green-600', badgeBg: 'bg-green-100' };
    if (val < 66) return { level: 'Medium', color: '#f59e0b', badgeColor: 'text-yellow-600', badgeBg: 'bg-yellow-100' };
    return { level: 'High', color: '#ef4444', badgeColor: 'text-red-600', badgeBg: 'bg-red-100' };
  };

  const risk = getRiskLevel(normalizedValue);
  
  // Calculate needle angle (-90° to +90°)
  const needleAngle = (normalizedValue / 100) * 180 - 90;

  return (
    <div className="flex flex-col items-center">
      {/* Gauge SVG */}
      <div className="relative w-32 h-32">
        <svg 
          className="w-full h-full" 
          viewBox="0 0 36 20"
        >
          {/* Background track (light gray) */}
          <path
            d="M 2 18 A 16 16 0 0 1 34 18"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="3"
            strokeLinecap="round"
          />
          
          {/* Green zone (Low risk) - 0-60° */}
          <path
            d="M 2 18 A 16 16 0 0 1 10 4"
            fill="none"
            stroke="#10b981"
            strokeWidth="3"
            strokeLinecap="round"
          />
          
          {/* Yellow zone (Medium risk) - 60-120° */}
          <path
            d="M 10 4 A 16 16 0 0 1 26 4"
            fill="none"
            stroke="#f59e0b"
            strokeWidth="3"
            strokeLinecap="round"
          />
          
          {/* Red zone (High risk) - 120-180° */}
          <path
            d="M 26 4 A 16 16 0 0 1 34 18"
            fill="none"
            stroke="#ef4444"
            strokeWidth="3"
            strokeLinecap="round"
          />
          
          {/* Needle */}
          <line
            x1="18"
            y1="18"
            x2="18"
            y2="2"
            stroke="#374151"
            strokeWidth="2"
            transform={`rotate(${needleAngle} 18 18)`}
          />
          
          {/* Center hub */}
          <circle
            cx="18"
            cy="18"
            r="3"
            fill="#374151"
          />
        </svg>
      </div>
      
      {/* Risk Level Text */}
      <div className="mt-3 text-center">
        <div className="text-xs text-gray-500">Debt to Equity</div>
        <div className="text-lg font-bold text-gray-900">
          {value !== null && value !== undefined ? value.toFixed(2) : 'N/A'}
        </div>
      </div>
      
      {/* Risk Level Badge */}
      <div className="mt-2">
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${risk.badgeBg} ${risk.badgeColor}`}>
          {risk.level}
        </span>
      </div>
    </div>
  );
};

export default RiskGauge;
