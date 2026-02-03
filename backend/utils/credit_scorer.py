import numpy as np
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from decimal import Decimal
from models import MonthlySummary, RiskSummary

class CreditScorer:
    """Deterministic credit scoring engine on 0-900 scale"""
    
    # Component weights (total 900 points)
    COMPONENT_WEIGHTS = {
        'profitability': 200,  # Max 200 points
        'liquidity': 200,      # Max 200 points
        'leverage': 200,       # Max 200 points
        'cash_flow': 200,      # Max 200 points
        'growth': 100          # Max 100 points
    }
    
    # Rating bands
    RATING_BANDS = {
        (800, 900): 'AAA',
        (700, 799): 'AA',
        (600, 699): 'A',
        (500, 599): 'BBB',
        (400, 499): 'BB',
        (0, 399): 'High Risk'
    }
    
    def calculate_credit_score(self, company_id: str, db: Session) -> Dict[str, Any]:
        """Calculate comprehensive credit score"""
        
        # Get latest financial and risk data
        latest_summary = db.query(MonthlySummary).filter(
            MonthlySummary.company_id == company_id
        ).order_by(MonthlySummary.month.desc()).first()
        
        risk_summary = db.query(RiskSummary).filter(
            RiskSummary.company_id == company_id
        ).first()
        
        if not latest_summary or len(db.query(MonthlySummary).filter(
            MonthlySummary.company_id == company_id
        ).all()) < 2:
            return self._empty_credit_response()
        
        # Get historical data for trend analysis
        summaries = db.query(MonthlySummary).filter(
            MonthlySummary.company_id == company_id
        ).order_by(MonthlySummary.month.desc()).limit(12).all()
        
        # Calculate component scores
        profitability_score = self._calculate_profitability_score(latest_summary, summaries)
        liquidity_score = self._calculate_liquidity_score(latest_summary)
        leverage_score = self._calculate_leverage_score(latest_summary, risk_summary)
        cash_flow_score = self._calculate_cash_flow_score(summaries)
        growth_score = self._calculate_growth_score(summaries)
        
        # Aggregate to total score (0-900)
        total_score = (
            profitability_score + 
            liquidity_score + 
            leverage_score + 
            cash_flow_score + 
            growth_score
        )
        
        # Determine rating
        credit_rating = self._get_rating(total_score)
        
        # Calculate repayment capacity
        repayment_capacity = self._calculate_repayment_capacity(latest_summary)
        
        # Determine loan eligibility
        eligibility_status = self._determine_eligibility(total_score, repayment_capacity)
        
        # Generate risk flags
        risk_flags = self._generate_risk_flags(
            profitability_score, liquidity_score, leverage_score, 
            cash_flow_score, growth_score, latest_summary
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            profitability_score, liquidity_score, leverage_score,
            cash_flow_score, growth_score, risk_flags
        )
        
        return {
            'credit_score': round(total_score, 2),
            'credit_rating': credit_rating,
            'component_scores': {
                'profitability': round(profitability_score, 2),
                'liquidity': round(liquidity_score, 2),
                'leverage': round(leverage_score, 2),
                'cash_flow': round(cash_flow_score, 2),
                'growth': round(growth_score, 2)
            },
            'repayment_capacity_ratio': round(repayment_capacity, 4),
            'loan_eligibility_status': eligibility_status,
            'risk_flags': risk_flags,
            'component_details': {
                'net_margin': float(latest_summary.net_margin) if latest_summary.net_margin else None,
                'current_ratio': float(latest_summary.current_ratio) if latest_summary.current_ratio else None,
                'quick_ratio': float(latest_summary.current_ratio * Decimal('0.6')) if latest_summary.current_ratio else None,
                'debt_to_equity': float(latest_summary.debt_to_equity) if latest_summary.debt_to_equity else None,
                'cash_flow_stability': self._calculate_stability([s.operating_cash_flow for s in summaries]),
                'revenue_growth_rate': self._calculate_growth_rate([s.revenue for s in summaries])
            },
            'improvement_recommendations': recommendations
        }
    
    def _calculate_profitability_score(self, latest: MonthlySummary, summaries: List) -> float:
        """Calculate profitability score (max 200 points)"""
        net_income = float(latest.net_income or 0)
        revenue = float(latest.revenue or 0)
        net_margin = net_income / revenue if revenue > 0 else -1
        
        # Base score from margin
        if net_margin >= 0.15:
            base_score = 200
        elif net_margin >= 0.10:
            base_score = 170
        elif net_margin >= 0.05:
            base_score = 140
        elif net_margin >= 0:
            base_score = 100
        elif net_margin >= -0.05:
            base_score = 50
        else:
            base_score = 0
        
        # Adjust for consistency
        if len(summaries) > 1:
            margins = []
            for s in summaries:
                rev = float(s.revenue or 0)
                inc = float(s.net_income or 0)
                if rev > 0:
                    margins.append(inc / rev)
            
            if len(margins) > 1:
                margin_volatility = self._calculate_stability(margins)
                if margin_volatility < 0.3:
                    base_score = min(200, base_score + 20)
                elif margin_volatility > 0.7:
                    base_score = max(0, base_score - 30)
        
        return base_score
    
    def _calculate_liquidity_score(self, latest: MonthlySummary) -> float:
        """Calculate liquidity score (max 200 points)"""
        current_ratio = float(latest.current_ratio or 0)
        quick_ratio = current_ratio * 0.6 if current_ratio > 0 else 0
        
        # Score based on current ratio
        if current_ratio >= 2.0:
            current_score = 100
        elif current_ratio >= 1.5:
            current_score = 85
        elif current_ratio >= 1.0:
            current_score = 70
        elif current_ratio >= 0.5:
            current_score = 40
        else:
            current_score = 0
        
        # Score based on quick ratio
        if quick_ratio >= 1.5:
            quick_score = 100
        elif quick_ratio >= 1.0:
            quick_score = 85
        elif quick_ratio >= 0.7:
            quick_score = 70
        elif quick_ratio >= 0.4:
            quick_score = 40
        else:
            quick_score = 0
        
        return (current_score + quick_score) / 2 * 2  # Scale to max 200
    
    def _calculate_leverage_score(self, latest: MonthlySummary, risk_summary: RiskSummary) -> float:
        """Calculate leverage score (max 200 points)"""
        debt_to_equity = float(latest.debt_to_equity or 0)
        
        # Base score from debt-to-equity
        if debt_to_equity <= 0.3:
            base_score = 200
        elif debt_to_equity <= 0.7:
            base_score = 170
        elif debt_to_equity <= 1.5:
            base_score = 140
        elif debt_to_equity <= 3.0:
            base_score = 100
        elif debt_to_equity <= 5.0:
            base_score = 50
        else:
            base_score = 0
        
        # Adjust for risk level if available
        if risk_summary and risk_summary.leverage_risk_level:
            if risk_summary.leverage_risk_level == 'Critical':
                base_score = max(0, base_score - 50)
            elif risk_summary.leverage_risk_level == 'High':
                base_score = max(0, base_score - 30)
            elif risk_summary.leverage_risk_level == 'Low':
                base_score = min(200, base_score + 20)
        
        return base_score
    
    def _calculate_cash_flow_score(self, summaries: List) -> float:
        """Calculate cash flow score (max 200 points)"""
        cash_flows = [float(s.operating_cash_flow or 0) for s in summaries]
        
        if not cash_flows:
            return 0
        
        # Check for positive cash flows
        positive_months = sum(1 for cf in cash_flows if cf > 0)
        positive_ratio = positive_months / len(cash_flows)
        
        # Base score from positivity
        if positive_ratio >= 0.8:
            base_score = 100
        elif positive_ratio >= 0.6:
            base_score = 80
        elif positive_ratio >= 0.4:
            base_score = 60
        elif positive_ratio >= 0.2:
            base_score = 40
        else:
            base_score = 0
        
        # Adjust for stability
        stability = self._calculate_stability(cash_flows)
        if stability < 0.3:
            base_score = min(100, base_score + 20)
        elif stability > 0.7:
            base_score = max(0, base_score - 30)
        
        # Check for consistency (trend)
        if len(cash_flows) > 1:
            trend_positive = sum(1 for i in range(1, len(cash_flows)) if cash_flows[i] >= cash_flows[i-1])
            trend_ratio = trend_positive / (len(cash_flows) - 1)
            if trend_ratio >= 0.7:
                base_score = min(100, base_score + 20)
            elif trend_ratio <= 0.3:
                base_score = max(0, base_score - 20)
        
        return base_score * 2  # Scale to max 200
    
    def _calculate_growth_score(self, summaries: List) -> float:
        """Calculate growth score (max 100 points)"""
        revenues = [float(s.revenue or 0) for s in summaries]
        
        if len(revenues) < 2:
            return 50  # Neutral score
        
        growth_rate = self._calculate_growth_rate(revenues)
        
        # Score based on growth rate
        if growth_rate >= 0.20:
            base_score = 100
        elif growth_rate >= 0.15:
            base_score = 85
        elif growth_rate >= 0.10:
            base_score = 70
        elif growth_rate >= 0.05:
            base_score = 55
        elif growth_rate >= 0:
            base_score = 40
        elif growth_rate >= -0.05:
            base_score = 25
        else:
            base_score = 0
        
        # Adjust for consistency
        if len(revenues) > 2:
            growth_consistency = self._calculate_growth_consistency(revenues)
            if growth_consistency >= 0.8:
                base_score = min(100, base_score + 10)
            elif growth_consistency <= 0.4:
                base_score = max(0, base_score - 15)
        
        return base_score
    
    def _calculate_repayment_capacity(self, latest: MonthlySummary) -> float:
        """Calculate repayment capacity ratio"""
        net_income = float(latest.net_income or 0)
        # Use current_liabilities as proxy for total debt obligations
        total_debt = float(latest.current_liabilities or 0)
        
        # Estimate annual debt service (10% of total debt)
        annual_debt_service = total_debt * 0.1
        
        if annual_debt_service == 0:
            return 1.0 if net_income > 0 else 0.0
        
        return net_income / annual_debt_service
    
    def _determine_eligibility(self, credit_score: float, repayment_capacity: float) -> str:
        """Determine loan eligibility status"""
        if credit_score >= 600 and repayment_capacity >= 1.5:
            return 'Eligible'
        elif credit_score >= 500 and repayment_capacity >= 1.0:
            return 'Conditional'
        else:
            return 'Not Eligible'
    
    def _generate_risk_flags(self, profit: float, liquid: float, lever: float, 
                            cash: float, growth: float, latest: MonthlySummary) -> List[str]:
        """Generate risk flags based on component scores"""
        flags = []
        
        if profit < 100:
            flags.append('Weak Profitability')
        if liquid < 100:
            flags.append('Poor Liquidity')
        if lever < 100:
            flags.append('High Leverage')
        if cash < 100:
            flags.append('Cash Flow Issues')
        if growth < 50:
            flags.append('Low Growth')
        
        # Specific metric flags
        if latest.net_income and float(latest.net_income) < 0:
            flags.append('Negative Profitability')
        if latest.current_ratio and float(latest.current_ratio) < 1.0:
            flags.append('Current Ratio < 1.0')
        if latest.debt_to_equity and float(latest.debt_to_equity) > 3.0:
            flags.append('Debt to Equity > 3.0')
        
        return flags
    
    def _generate_recommendations(self, profit: float, liquid: float, lever: float,
                               cash: float, growth: float, flags: List[str]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if profit < 100:
            recommendations.append('Improve operating margins through cost optimization')
        if liquid < 100:
            recommendations.append('Enhance liquidity by improving working capital management')
        if lever < 100:
            recommendations.append('Reduce debt levels to improve leverage ratios')
        if cash < 100:
            recommendations.append('Strengthen cash flow generation through operational improvements')
        if growth < 50:
            recommendations.append('Focus on revenue growth strategies and market expansion')
        
        # Specific flag-based recommendations
        if 'Negative Profitability' in flags:
            recommendations.append('Address negative profitability immediately through cost reduction')
        if 'Current Ratio < 1.0' in flags:
            recommendations.append('Increase current assets or reduce short-term liabilities')
        if 'Debt to Equity > 3.0' in flags:
            recommendations.append('Consider equity infusion to reduce leverage')
        
        return recommendations
    
    def _get_rating(self, score: float) -> str:
        """Get credit rating based on score"""
        for (min_score, max_score), rating in self.RATING_BANDS.items():
            if min_score <= score <= max_score:
                return rating
        return 'High Risk'
    
    def _calculate_stability(self, values: List[float]) -> float:
        """Calculate coefficient of variation"""
        if len(values) < 2 or not any(values):
            return 1.0
        
        values_array = np.array([float(v) for v in values])
        mean = np.mean(values_array)
        if mean == 0:
            return 1.0
        
        std_dev = np.std(values_array)
        return std_dev / abs(mean)
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate compound growth rate"""
        if len(values) < 2 or values[0] == 0:
            return 0
        
        start_value = float(values[0])
        end_value = float(values[-1])
        periods = len(values) - 1
        
        return (end_value / start_value) ** (1/periods) - 1
    
    def _calculate_growth_consistency(self, revenues: List[float]) -> float:
        """Calculate growth consistency (positive growth periods ratio)"""
        if len(revenues) < 2:
            return 0
        
        positive_growth = 0
        for i in range(1, len(revenues)):
            if revenues[i] > revenues[i-1]:
                positive_growth += 1
        
        return positive_growth / (len(revenues) - 1)
    
    def _empty_credit_response(self) -> Dict[str, Any]:
        """Return empty response when insufficient data"""
        return {
            'credit_score': None,
            'credit_rating': 'No Data',
            'component_scores': {
                'profitability': None,
                'liquidity': None,
                'leverage': None,
                'cash_flow': None,
                'growth': None
            },
            'repayment_capacity_ratio': None,
            'loan_eligibility_status': 'No Data',
            'risk_flags': [],
            'component_details': {
                'net_margin': None,
                'current_ratio': None,
                'quick_ratio': None,
                'debt_to_equity': None,
                'cash_flow_stability': None,
                'revenue_growth_rate': None
            },
            'improvement_recommendations': []
        }
