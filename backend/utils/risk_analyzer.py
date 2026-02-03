import numpy as np
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from models import MonthlySummary

class RiskAnalyzer:
    """Deterministic risk analyzer with component-based scoring"""
    
    # Risk weights (sums to 100%)
    WEIGHTS = {
        'leverage': 0.30,
        'liquidity': 0.25,
        'profitability': 0.25,
        'cash_flow': 0.20
    }
    
    # Risk thresholds
    THRESHOLDS = {
        'debt_to_equity': {
            'low': {'max': 1.0, 'score': 20},
            'moderate': {'max': 2.0, 'score': 40},
            'high': {'max': 3.0, 'score': 70},
            'critical': {'max': float('inf'), 'score': 100}
        },
        'current_ratio': {
            'low': {'min': 1.5, 'score': 20},
            'moderate': {'min': 1.0, 'max': 1.5, 'score': 40},
            'high': {'min': 0.5, 'max': 1.0, 'score': 70},
            'critical': {'max': 0.5, 'score': 100}
        },
        'quick_ratio': {
            'low': {'min': 1.0, 'score': 20},
            'moderate': {'min': 0.7, 'max': 1.0, 'score': 40},
            'high': {'min': 0.4, 'max': 0.7, 'score': 70},
            'critical': {'max': 0.4, 'score': 100}
        },
        'net_margin': {
            'low': {'min': 0.05, 'score': 20},
            'moderate': {'min': 0, 'max': 0.05, 'score': 40},
            'high': {'max': 0, 'score': 70},
            'critical': {'max': -0.05, 'score': 100}
        },
        'cash_flow_stability': {
            'low': {'max': 0.3, 'score': 20},
            'moderate': {'max': 0.5, 'score': 40},
            'high': {'max': 0.7, 'score': 70},
            'critical': {'max': float('inf'), 'score': 100}
        }
    }
    
    def analyze_comprehensive_risk(self, company_id: str, db: Session) -> Dict[str, Any]:
        """Analyze comprehensive risk with all components"""
        
        # Get last 12 months of data
        summaries = db.query(MonthlySummary).filter(
            MonthlySummary.company_id == company_id
        ).order_by(MonthlySummary.month.desc()).limit(12).all()
        
        if len(summaries) < 2:
            return self._empty_risk_response()
        
        # Extract latest data
        latest = summaries[0]
        
        # Calculate component risks
        leverage_risk = self._calculate_leverage_risk(latest)
        liquidity_risk = self._calculate_liquidity_risk(latest)
        profitability_risk = self._calculate_profitability_risk(latest)
        cash_flow_risk = self._calculate_cash_flow_risk(summaries)
        
        # Weighted aggregation for overall risk
        overall_risk_score = (
            leverage_risk['score'] * self.WEIGHTS['leverage'] +
            liquidity_risk['score'] * self.WEIGHTS['liquidity'] +
            profitability_risk['score'] * self.WEIGHTS['profitability'] +
            cash_flow_risk['score'] * self.WEIGHTS['cash_flow']
        )
        
        overall_risk_level = self._categorize_risk_level(overall_risk_score)
        
        # Generate mitigation actions
        mitigation_actions = self._generate_mitigation_actions({
            'leverage': leverage_risk,
            'liquidity': liquidity_risk,
            'profitability': profitability_risk,
            'cash_flow': cash_flow_risk
        })
        
        return {
            'overall_risk_score': round(overall_risk_score, 2),
            'overall_risk_level': overall_risk_level,
            'component_breakdown': {
                'leverage': {
                    'score': round(leverage_risk['score'], 2),
                    'level': leverage_risk['level'],
                    'details': leverage_risk['details']
                },
                'liquidity': {
                    'score': round(liquidity_risk['score'], 2),
                    'level': liquidity_risk['level'],
                    'details': liquidity_risk['details']
                },
                'profitability': {
                    'score': round(profitability_risk['score'], 2),
                    'level': profitability_risk['level'],
                    'details': profitability_risk['details']
                },
                'cash_flow': {
                    'score': round(cash_flow_risk['score'], 2),
                    'level': cash_flow_risk['level'],
                    'details': cash_flow_risk['details']
                }
            },
            'mitigation_actions': mitigation_actions
        }
    
    def _calculate_leverage_risk(self, latest_summary) -> Dict[str, Any]:
        """Calculate leverage risk based on debt-to-equity"""
        debt_to_equity = float(latest_summary.debt_to_equity or 0)
        
        # Determine risk level and score
        thresholds = self.THRESHOLDS['debt_to_equity']
        if debt_to_equity <= thresholds['low']['max']:
            level = 'Low'
            score = thresholds['low']['score']
        elif debt_to_equity <= thresholds['moderate']['max']:
            level = 'Moderate'
            score = thresholds['moderate']['score']
        elif debt_to_equity <= thresholds['high']['max']:
            level = 'High'
            score = thresholds['high']['score']
        else:
            level = 'Critical'
            score = thresholds['critical']['score']
        
        return {
            'score': score,
            'level': level,
            'details': {
                'debt_to_equity': round(debt_to_equity, 2)
            }
        }
    
    def _calculate_liquidity_risk(self, latest_summary) -> Dict[str, Any]:
        """Calculate liquidity risk based on current and quick ratios"""
        current_ratio = float(latest_summary.current_ratio or 0)
        
        # Estimate quick ratio (assuming 60% of current assets are quick assets)
        quick_ratio = current_ratio * 0.6 if current_ratio > 0 else 0
        
        # Use the worse of the two ratios for risk assessment
        effective_ratio = min(current_ratio, quick_ratio)
        
        # Determine risk level and score
        thresholds = self.THRESHOLDS['current_ratio']
        if effective_ratio >= thresholds['low']['min']:
            level = 'Low'
            score = thresholds['low']['score']
        elif effective_ratio >= thresholds['moderate']['min']:
            level = 'Moderate'
            score = thresholds['moderate']['score']
        elif effective_ratio >= thresholds['high']['min']:
            level = 'High'
            score = thresholds['high']['score']
        else:
            level = 'Critical'
            score = thresholds['critical']['score']
        
        return {
            'score': score,
            'level': level,
            'details': {
                'current_ratio': round(current_ratio, 2),
                'quick_ratio': round(quick_ratio, 2)
            }
        }
    
    def _calculate_profitability_risk(self, latest_summary) -> Dict[str, Any]:
        """Calculate profitability risk based on net margin and income"""
        net_income = float(latest_summary.net_income or 0)
        revenue = float(latest_summary.revenue or 0)
        net_margin = net_income / revenue if revenue > 0 else -1
        
        # Determine risk level and score
        thresholds = self.THRESHOLDS['net_margin']
        if net_margin >= thresholds['low']['min']:
            level = 'Low'
            score = thresholds['low']['score']
        elif net_margin >= thresholds['moderate']['min']:
            level = 'Moderate'
            score = thresholds['moderate']['score']
        elif net_margin >= thresholds['high']['max']:
            level = 'High'
            score = thresholds['high']['score']
        else:
            level = 'Critical'
            score = thresholds['critical']['score']
        
        return {
            'score': score,
            'level': level,
            'details': {
                'net_margin': round(net_margin, 4),
                'net_income': round(net_income, 2)
            }
        }
    
    def _calculate_cash_flow_risk(self, summaries: List) -> Dict[str, Any]:
        """Calculate cash flow risk based on stability and negative flow frequency"""
        cash_flows = [float(s.operating_cash_flow or 0) for s in reversed(summaries)]
        
        # Calculate stability (coefficient of variation)
        if len(cash_flows) > 1 and any(cash_flows):
            cash_flows_array = np.array(cash_flows)
            mean = np.mean(cash_flows_array)
            if mean != 0:
                std_dev = np.std(cash_flows_array)
                stability = std_dev / abs(mean)
            else:
                stability = 1.0
        else:
            stability = 1.0
        
        # Count negative cash flow months
        negative_months = sum(1 for cf in cash_flows if cf < 0)
        negative_ratio = negative_months / len(cash_flows)
        
        # Base score from stability
        thresholds = self.THRESHOLDS['cash_flow_stability']
        if stability <= thresholds['low']['max']:
            base_score = thresholds['low']['score']
        elif stability <= thresholds['moderate']['max']:
            base_score = thresholds['moderate']['score']
        elif stability <= thresholds['high']['max']:
            base_score = thresholds['high']['score']
        else:
            base_score = thresholds['critical']['score']
        
        # Adjust for negative cash flow frequency
        if negative_ratio > 0.5:
            base_score = min(100, base_score + 30)
        elif negative_ratio > 0.25:
            base_score = min(100, base_score + 15)
        
        # Determine final level
        if base_score <= 30:
            level = 'Low'
        elif base_score <= 50:
            level = 'Moderate'
        elif base_score <= 70:
            level = 'High'
        else:
            level = 'Critical'
        
        return {
            'score': base_score,
            'level': level,
            'details': {
                'cash_flow_stability': round(stability, 2),
                'negative_cash_flow_months': negative_months,
                'total_months': len(cash_flows)
            }
        }
    
    def _categorize_risk_level(self, score: float) -> str:
        """Categorize risk score to level"""
        if score <= 30:
            return 'Low'
        elif score <= 50:
            return 'Moderate'
        elif score <= 70:
            return 'High'
        else:
            return 'Critical'
    
    def _generate_mitigation_actions(self, component_risks: Dict[str, Dict]) -> List[str]:
        """Generate specific mitigation actions based on risk components"""
        actions = []
        
        # Leverage risk actions
        if component_risks['leverage']['score'] > 50:
            if component_risks['leverage']['details']['debt_to_equity'] > 3:
                actions.append("Reduce debt exposure through debt restructuring or equity infusion")
            else:
                actions.append("Optimize capital structure to lower debt-to-equity ratio")
        
        # Liquidity risk actions
        if component_risks['liquidity']['score'] > 50:
            if component_risks['liquidity']['details']['current_ratio'] < 1:
                actions.append("Improve liquidity by increasing current assets or reducing short-term liabilities")
            else:
                actions.append("Strengthen working capital management to improve liquidity ratios")
        
        # Profitability risk actions
        if component_risks['profitability']['score'] > 50:
            if component_risks['profitability']['details']['net_margin'] < 0:
                actions.append("Address negative profitability by reducing costs or increasing prices")
            else:
                actions.append("Enhance profit margins through operational efficiency improvements")
        
        # Cash flow risk actions
        if component_risks['cash_flow']['score'] > 50:
            if component_risks['cash_flow']['details']['negative_cash_flow_months'] > 0:
                actions.append("Improve cash flow management through better receivables collection")
            else:
                actions.append("Enhance cash flow stability through predictable revenue streams")
        
        # General actions if no specific high risks
        if not actions:
            actions.append("Maintain current risk management practices and monitor key ratios")
        
        return actions
    
    def _empty_risk_response(self) -> Dict[str, Any]:
        """Return empty response when insufficient data"""
        return {
            'overall_risk_score': None,
            'overall_risk_level': 'No Data',
            'component_breakdown': {
                'leverage': {'score': None, 'level': 'No Data', 'details': {}},
                'liquidity': {'score': None, 'level': 'No Data', 'details': {}},
                'profitability': {'score': None, 'level': 'No Data', 'details': {}},
                'cash_flow': {'score': None, 'level': 'No Data', 'details': {}}
            },
            'mitigation_actions': []
        }
