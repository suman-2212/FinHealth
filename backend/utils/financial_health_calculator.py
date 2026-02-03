import numpy as np
from typing import Dict, List, Tuple, Any
from sqlalchemy.orm import Session
from models import MonthlySummary

class FinancialHealthCalculator:
    """Deterministic financial health calculator with weighted component scoring"""
    
    # Weight configuration (sums to 100%)
    WEIGHTS = {
        'profitability': 0.30,
        'liquidity': 0.20,
        'leverage': 0.25,
        'cash_flow': 0.15,
        'growth': 0.10
    }
    
    # Thresholds for scoring
    THRESHOLDS = {
        'net_margin': {'excellent': 0.15, 'good': 0.08, 'moderate': 0.03, 'weak': 0},
        'current_ratio': {'excellent': 2.0, 'good': 1.5, 'moderate': 1.0, 'weak': 0.5},
        'debt_to_equity': {'excellent': 0.3, 'good': 0.7, 'moderate': 1.5, 'weak': 3.0},
        'cash_flow_stability': {'excellent': 0.2, 'good': 0.4, 'moderate': 0.6, 'weak': 0.8},
        'revenue_growth': {'excellent': 0.20, 'good': 0.10, 'moderate': 0.03, 'weak': 0}
    }
    
    def calculate_comprehensive_health(self, company_id: str, db: Session) -> Dict[str, Any]:
        """Calculate comprehensive financial health score with all components"""
        
        # Get last 12 months of data
        summaries = db.query(MonthlySummary).filter(
            MonthlySummary.company_id == company_id
        ).order_by(MonthlySummary.month.desc()).limit(12).all()
        
        if len(summaries) < 2:
            return self._empty_health_response()
        
        # Extract data arrays
        revenues = [float(s.revenue or 0) for s in reversed(summaries)]
        net_incomes = [float(s.net_income or 0) for s in reversed(summaries)]
        current_ratios = [float(s.current_ratio or 0) for s in reversed(summaries)]
        cash_flows = [float(s.operating_cash_flow or 0) for s in reversed(summaries)]
        
        # Get latest debt metrics
        latest = summaries[0]
        net_margin = float(latest.net_margin or 0) if latest.net_margin else (net_incomes[-1] / revenues[-1] if revenues[-1] > 0 else 0)
        current_ratio_val = current_ratios[-1]
        debt_to_equity_val = float(latest.debt_to_equity or 0)
        
        # Calculate component scores
        profitability_score = self._calculate_profitability_score(net_margin, revenues, net_incomes)
        liquidity_score = self._calculate_liquidity_score(current_ratio_val)
        leverage_score = self._calculate_leverage_score(debt_to_equity_val)
        cash_flow_score = self._calculate_cash_flow_score(cash_flows)
        growth_score = self._calculate_growth_score(revenues)
        
        # Weighted aggregation
        health_score = (
            profitability_score * self.WEIGHTS['profitability'] +
            liquidity_score * self.WEIGHTS['liquidity'] +
            leverage_score * self.WEIGHTS['leverage'] +
            cash_flow_score * self.WEIGHTS['cash_flow'] +
            growth_score * self.WEIGHTS['growth']
        )
        
        # Categorize health
        health_category = self._categorize_health(health_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations({
            'profitability': profitability_score,
            'liquidity': liquidity_score,
            'leverage': leverage_score,
            'cash_flow': cash_flow_score,
            'growth': growth_score
        }, {
            'net_margin': net_margin,
            'current_ratio': current_ratio_val,
            'debt_to_equity': debt_to_equity_val
        })
        
        return {
            'health_score': round(health_score, 2),
            'health_category': health_category,
            'component_scores': {
                'profitability': round(profitability_score, 2),
                'liquidity': round(liquidity_score, 2),
                'leverage': round(leverage_score, 2),
                'cash_flow': round(cash_flow_score, 2),
                'growth': round(growth_score, 2)
            },
            'component_details': {
                'net_margin': round(net_margin, 4),
                'current_ratio': round(current_ratio_val, 2),
                'debt_to_equity': round(debt_to_equity_val, 2),
                'cash_flow_stability': round(self._calculate_stability(cash_flows), 2),
                'revenue_growth_rate': round(self._calculate_growth_rate(revenues), 4)
            },
            'improvement_recommendations': recommendations
        }
    
    def _calculate_profitability_score(self, net_margin: float, revenues: List[float], net_incomes: List[float]) -> float:
        """Score based on net profit margin and stability"""
        if not revenues or revenues[-1] == 0:
            return 0
        
        # Base score from margin
        thresholds = self.THRESHOLDS['net_margin']
        if net_margin >= thresholds['excellent']:
            base_score = 100
        elif net_margin >= thresholds['good']:
            base_score = 80
        elif net_margin >= thresholds['moderate']:
            base_score = 60
        elif net_margin >= thresholds['weak']:
            base_score = 40
        else:
            base_score = 20
        
        # Adjust for stability (less volatility = higher score)
        if len(net_incomes) > 1:
            income_volatility = self._calculate_stability(net_incomes)
            stability_bonus = max(0, (0.5 - income_volatility) * 40)  # Up to 20 points bonus
            base_score = min(100, base_score + stability_bonus)
        
        return base_score
    
    def _calculate_liquidity_score(self, current_ratio: float) -> float:
        """Score based on current ratio"""
        thresholds = self.THRESHOLDS['current_ratio']
        if current_ratio >= thresholds['excellent']:
            return 100
        elif current_ratio >= thresholds['good']:
            return 80
        elif current_ratio >= thresholds['moderate']:
            return 60
        elif current_ratio >= thresholds['weak']:
            return 40
        else:
            return 20
    
    def _calculate_leverage_score(self, debt_to_equity: float) -> float:
        """Score based on debt-to-equity (inverse scoring - lower is better)"""
        thresholds = self.THRESHOLDS['debt_to_equity']
        if debt_to_equity <= thresholds['excellent']:
            return 100
        elif debt_to_equity <= thresholds['good']:
            return 80
        elif debt_to_equity <= thresholds['moderate']:
            return 60
        elif debt_to_equity <= thresholds['weak']:
            return 40
        else:
            return 20
    
    def _calculate_cash_flow_score(self, cash_flows: List[float]) -> float:
        """Score based on cash flow stability and positivity"""
        if not cash_flows:
            return 0
        
        # Check if cash flows are consistently positive
        positive_ratio = sum(1 for cf in cash_flows if cf > 0) / len(cash_flows)
        
        # Base score from positivity
        if positive_ratio >= 0.8:
            base_score = 80
        elif positive_ratio >= 0.6:
            base_score = 60
        elif positive_ratio >= 0.4:
            base_score = 40
        else:
            base_score = 20
        
        # Adjust for stability
        stability = self._calculate_stability(cash_flows)
        if stability < 0.3:
            base_score += 20
        elif stability < 0.5:
            base_score += 10
        
        return min(100, base_score)
    
    def _calculate_growth_score(self, revenues: List[float]) -> float:
        """Score based on revenue growth rate"""
        if len(revenues) < 2:
            return 50  # Neutral score if insufficient data
        
        growth_rate = self._calculate_growth_rate(revenues)
        thresholds = self.THRESHOLDS['revenue_growth']
        
        if growth_rate >= thresholds['excellent']:
            return 100
        elif growth_rate >= thresholds['good']:
            return 80
        elif growth_rate >= thresholds['moderate']:
            return 60
        elif growth_rate >= thresholds['weak']:
            return 40
        else:
            return 20
    
    def _calculate_stability(self, values: List[float]) -> float:
        """Calculate coefficient of variation (lower = more stable)"""
        if len(values) < 2 or not any(values):
            return 1.0
        
        values_array = np.array(values)
        mean = np.mean(values_array)
        if mean == 0:
            return 1.0
        
        std_dev = np.std(values_array)
        return std_dev / abs(mean)
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate compound monthly growth rate"""
        if len(values) < 2 or values[0] == 0:
            return 0
        
        start_value = values[0]
        end_value = values[-1]
        periods = len(values) - 1
        
        return (end_value / start_value) ** (1/periods) - 1
    
    def _categorize_health(self, score: float) -> str:
        """Categorize health score"""
        if score >= 85:
            return 'Excellent'
        elif score >= 70:
            return 'Good'
        elif score >= 50:
            return 'Moderate'
        elif score >= 30:
            return 'Weak'
        else:
            return 'Critical'
    
    def _generate_recommendations(self, scores: Dict[str, float], details: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations based on weak areas"""
        recommendations = []
        
        if scores['profitability'] < 60:
            if details['net_margin'] < 0.05:
                recommendations.append("Improve profitability by reducing costs or increasing prices")
            else:
                recommendations.append("Enhance profit margin through operational efficiency")
        
        if scores['liquidity'] < 60:
            if details['current_ratio'] < 1.0:
                recommendations.append("Improve liquidity by increasing current assets or reducing short-term liabilities")
            else:
                recommendations.append("Strengthen liquidity position to meet short-term obligations")
        
        if scores['leverage'] < 60:
            if details['debt_to_equity'] > 2.0:
                recommendations.append("Reduce leverage to strengthen balance sheet and lower financial risk")
            else:
                recommendations.append("Optimize debt structure to improve financial stability")
        
        if scores['cash_flow'] < 60:
            recommendations.append("Enhance cash flow management through better working capital control")
        
        if scores['growth'] < 60:
            recommendations.append("Develop growth strategies to expand revenue and market presence")
        
        return recommendations
    
    def _empty_health_response(self) -> Dict[str, Any]:
        """Return empty response when insufficient data"""
        return {
            'health_score': None,
            'health_category': 'No Data',
            'component_scores': {
                'profitability': None,
                'liquidity': None,
                'leverage': None,
                'cash_flow': None,
                'growth': None
            },
            'component_details': {
                'net_margin': None,
                'current_ratio': None,
                'debt_to_equity': None,
                'cash_flow_stability': None,
                'revenue_growth_rate': None
            },
            'improvement_recommendations': []
        }
