from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import get_db
from models import FinancialData, FinancialMetrics, RiskAssessment, User
from schemas import RiskAssessmentResponse
from auth import get_current_active_user
from utils.financial_calculator import FinancialCalculator
from deps import get_request_company_id

router = APIRouter()
calculator = FinancialCalculator()

@router.get("/evaluate", response_model=RiskAssessmentResponse)
async def evaluate_risk(
    request: Request,
    period: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    
    # Get latest metrics for the period
    metrics = db.query(FinancialMetrics).filter(
        FinancialMetrics.company_id == company_id,
        FinancialMetrics.period == period
    ).first()
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial metrics not found for the specified period"
        )
    
    # Get financial data for additional context
    financial_data = db.query(FinancialData).filter(
        FinancialData.company_id == company_id,
        FinancialData.period == period
    ).first()
    
    # Perform risk assessment
    metrics_dict = {
        'current_ratio': metrics.current_ratio,
        'quick_ratio': metrics.quick_ratio,
        'cash_ratio': metrics.cash_ratio,
        'debt_to_equity': metrics.debt_to_equity,
        'debt_to_assets': metrics.debt_to_assets,
        'interest_coverage_ratio': metrics.interest_coverage_ratio,
        'working_capital': metrics.working_capital,
        'cash_conversion_cycle': metrics.cash_conversion_cycle,
        'net_profit_margin': metrics.net_profit_margin,
    }
    risk_analysis = calculator.assess_financial_risks(metrics_dict, financial_data, industry="")
    
    # Check if risk assessment already exists
    existing_assessment = db.query(RiskAssessment).filter(
        RiskAssessment.company_id == company_id,
        RiskAssessment.period == period
    ).first()
    
    if existing_assessment:
        # Update existing assessment
        for key, value in risk_analysis.items():
            if key not in ['risk_factors', 'recommendations']:
                setattr(existing_assessment, key, value)
        existing_assessment.risk_factors = risk_analysis.get('risk_factors', {})
        existing_assessment.recommendations = risk_analysis.get('recommendations', [])
        db_assessment = existing_assessment
    else:
        # Create new risk assessment
        db_assessment = RiskAssessment(
            company_id=company_id,
            period=period,
            **risk_analysis
        )
        db.add(db_assessment)
    
    db.commit()
    db.refresh(db_assessment)
    
    return db_assessment

@router.get("/history", response_model=List[RiskAssessmentResponse])
async def get_risk_history(
    request: Request,
    limit: int = 12,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    
    # Get risk assessment history
    risk_history = db.query(RiskAssessment).filter(
        RiskAssessment.company_id == company_id
    ).order_by(RiskAssessment.period.desc()).limit(limit).all()
    
    return risk_history

@router.get("/heatmap")
async def get_risk_heatmap(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    
    # Get latest risk assessment
    latest_risk = db.query(RiskAssessment).filter(
        RiskAssessment.company_id == company_id
    ).order_by(RiskAssessment.period.desc()).first()
    
    if not latest_risk:
        return {"heatmap": [], "overall_risk": "UNKNOWN"}
    
    # Create risk heatmap data
    heatmap_data = [
        {
            "category": "Liquidity Risk",
            "score": latest_risk.liquidity_risk or 0,
            "level": _get_risk_level(latest_risk.liquidity_risk),
            "description": "Risk of not meeting short-term obligations"
        },
        {
            "category": "Solvency Risk",
            "score": latest_risk.solvency_risk or 0,
            "level": _get_risk_level(latest_risk.solvency_risk),
            "description": "Risk of long-term financial distress"
        },
        {
            "category": "Operational Risk",
            "score": latest_risk.operational_risk or 0,
            "level": _get_risk_level(latest_risk.operational_risk),
            "description": "Risk from operational inefficiencies"
        },
        {
            "category": "Compliance Risk",
            "score": latest_risk.compliance_risk or 0,
            "level": _get_risk_level(latest_risk.compliance_risk),
            "description": "Risk of regulatory non-compliance"
        }
    ]
    
    return {
        "heatmap": heatmap_data,
        "overall_risk": latest_risk.risk_level,
        "overall_score": latest_risk.overall_risk,
        "period": latest_risk.period,
        "risk_factors": latest_risk.risk_factors,
        "recommendations": latest_risk.recommendations
    }

def _get_risk_level(score: float) -> str:
    """Convert risk score to risk level"""
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    elif score >= 20:
        return "LOW"
    else:
        return "VERY_LOW"

# Add risk assessment methods to FinancialCalculator
def assess_financial_risks(self, metrics, financial_data, industry) -> Dict:
    """Assess various financial risks"""
    
    # Liquidity Risk Assessment
    liquidity_risk = self._assess_liquidity_risk(metrics)
    
    # Solvency Risk Assessment
    solvency_risk = self._assess_solvency_risk(metrics)
    
    # Operational Risk Assessment
    operational_risk = self._assess_operational_risk(metrics, financial_data)
    
    # Compliance Risk Assessment
    compliance_risk = self._assess_compliance_risk(metrics, financial_data)
    
    # Overall Risk Score
    overall_risk = (liquidity_risk + solvency_risk + operational_risk + compliance_risk) / 4
    
    # Determine risk level
    if overall_risk >= 80:
        risk_level = "CRITICAL"
    elif overall_risk >= 60:
        risk_level = "HIGH"
    elif overall_risk >= 40:
        risk_level = "MEDIUM"
    elif overall_risk >= 20:
        risk_level = "LOW"
    else:
        risk_level = "VERY_LOW"
    
    # Identify risk factors
    risk_factors = self._identify_risk_factors(metrics, financial_data)
    
    # Generate recommendations
    recommendations = self._generate_risk_recommendations(risk_factors, risk_level)
    
    return {
        'liquidity_risk': liquidity_risk,
        'solvency_risk': solvency_risk,
        'operational_risk': operational_risk,
        'compliance_risk': compliance_risk,
        'overall_risk': overall_risk,
        'risk_level': risk_level,
        'risk_factors': risk_factors,
        'recommendations': recommendations
    }

def _assess_liquidity_risk(self, metrics) -> float:
    """Assess liquidity risk (0-100, higher = more risky)"""
    risk_score = 0
    
    # Current ratio assessment
    if metrics.get('current_ratio'):
        if metrics['current_ratio'] < 1.0:
            risk_score += 40
        elif metrics['current_ratio'] < 1.5:
            risk_score += 20
        elif metrics['current_ratio'] < 2.0:
            risk_score += 10
    
    # Quick ratio assessment
    if metrics.get('quick_ratio'):
        if metrics['quick_ratio'] < 0.5:
            risk_score += 30
        elif metrics['quick_ratio'] < 1.0:
            risk_score += 15
    
    # Cash ratio assessment
    if metrics.get('cash_ratio'):
        if metrics['cash_ratio'] < 0.1:
            risk_score += 30
        elif metrics['cash_ratio'] < 0.3:
            risk_score += 15
    
    return min(100, risk_score)

def _assess_solvency_risk(self, metrics) -> float:
    """Assess solvency risk (0-100, higher = more risky)"""
    risk_score = 0
    
    # Debt to equity assessment
    if metrics.get('debt_to_equity'):
        if metrics['debt_to_equity'] > 2.0:
            risk_score += 40
        elif metrics['debt_to_equity'] > 1.5:
            risk_score += 25
        elif metrics['debt_to_equity'] > 1.0:
            risk_score += 15
    
    # Interest coverage assessment
    if metrics.get('interest_coverage_ratio'):
        if metrics['interest_coverage_ratio'] < 1.0:
            risk_score += 40
        elif metrics['interest_coverage_ratio'] < 2.0:
            risk_score += 25
        elif metrics['interest_coverage_ratio'] < 3.0:
            risk_score += 15
    
    # Debt to assets assessment
    if metrics.get('debt_to_assets'):
        if metrics['debt_to_assets'] > 0.8:
            risk_score += 20
        elif metrics['debt_to_assets'] > 0.6:
            risk_score += 10
    
    return min(100, risk_score)

def _assess_operational_risk(self, metrics, financial_data) -> float:
    """Assess operational risk (0-100, higher = more risky)"""
    risk_score = 0
    
    # Working capital assessment
    if metrics.get('working_capital'):
        if metrics['working_capital'] < 0:
            risk_score += 30
        elif metrics['working_capital'] < 100000:  # Assuming currency units
            risk_score += 15
    
    # Cash conversion cycle assessment
    if metrics.get('cash_conversion_cycle'):
        if metrics['cash_conversion_cycle'] > 120:
            risk_score += 25
        elif metrics['cash_conversion_cycle'] > 90:
            risk_score += 15
        elif metrics['cash_conversion_cycle'] > 60:
            risk_score += 10
    
    # Profit margin assessment
    if metrics.get('net_profit_margin'):
        if metrics['net_profit_margin'] < 0:
            risk_score += 35
        elif metrics['net_profit_margin'] < 0.02:
            risk_score += 20
        elif metrics['net_profit_margin'] < 0.05:
            risk_score += 10
    
    return min(100, risk_score)

def _assess_compliance_risk(self, metrics, financial_data) -> float:
    """Assess compliance risk (0-100, higher = more risky)"""
    risk_score = 20  # Base compliance risk
    
    # Tax compliance assessment (simplified)
    if financial_data:
        if financial_data.tax_expense and financial_data.net_income:
            tax_ratio = financial_data.tax_expense / abs(financial_data.net_income) if financial_data.net_income != 0 else 0
            # If tax expense seems unusually low or high
            if tax_ratio < 0.1 or tax_ratio > 0.4:
                risk_score += 20
    
    # Regulatory compliance based on industry
    industry_risk_factors = {
        'Manufacturing': 15,
        'Financial Services': 25,
        'Healthcare': 20,
        'Retail': 10,
        'Services': 5
    }
    
    # Default risk score for other industries
    risk_score += industry_risk_factors.get('Manufacturing', 10)
    
    return min(100, risk_score)

def _identify_risk_factors(self, metrics, financial_data) -> Dict[str, Any]:
    """Identify specific risk factors"""
    factors = {}
    
    # Liquidity factors
    if metrics.get('current_ratio', 0) < 1.0:
        factors['poor_liquidity'] = "Current ratio below 1.0 indicates difficulty meeting short-term obligations"
    
    if metrics.get('quick_ratio', 0) < 0.5:
        factors['low_cash_conversion'] = "Quick ratio below 0.5 suggests poor immediate liquidity"
    
    # Solvency factors
    if metrics.get('debt_to_equity', 0) > 2.0:
        factors['high_leverage'] = "Debt-to-equity ratio above 2.0 indicates excessive leverage"
    
    if metrics.get('interest_coverage_ratio', 0) < 1.5:
        factors['poor_interest_coverage'] = "Interest coverage ratio below 1.5 suggests difficulty servicing debt"
    
    # Operational factors
    if metrics.get('working_capital', 0) < 0:
        factors['negative_working_capital'] = "Negative working capital indicates operational distress"
    
    if metrics.get('net_profit_margin', 0) < 0:
        factors['negative_profitability'] = "Negative profit margin indicates business losses"
    
    return factors

def _generate_risk_recommendations(self, risk_factors: Dict, risk_level: str) -> List[str]:
    """Generate risk mitigation recommendations"""
    recommendations = []
    
    if 'poor_liquidity' in risk_factors:
        recommendations.append("Improve cash management by accelerating receivables and optimizing inventory")
        recommendations.append("Consider arranging short-term financing facilities")
    
    if 'high_leverage' in risk_factors:
        recommendations.append("Develop debt reduction strategy through improved profitability")
        recommendations.append("Consider equity financing to reduce debt burden")
    
    if 'negative_working_capital' in risk_factors:
        recommendations.append("Immediate action required: secure emergency financing")
        recommendations.append("Review and reduce operating expenses")
    
    if 'negative_profitability' in risk_factors:
        recommendations.append("Conduct comprehensive cost structure analysis")
        recommendations.append("Review pricing strategy and market positioning")
    
    if risk_level in ["HIGH", "CRITICAL"]:
        recommendations.append("Engage financial advisor for comprehensive turnaround strategy")
        recommendations.append("Consider business restructuring options")
    
    # General recommendations
    if risk_level not in ["LOW", "VERY_LOW"]:
        recommendations.append("Implement regular financial monitoring and reporting")
        recommendations.append("Develop contingency plans for cash flow shortages")
    
    return recommendations

# Add the methods to FinancialCalculator class
FinancialCalculator.assess_financial_risks = assess_financial_risks
FinancialCalculator._assess_liquidity_risk = _assess_liquidity_risk
FinancialCalculator._assess_solvency_risk = _assess_solvency_risk
FinancialCalculator._assess_operational_risk = _assess_operational_risk
FinancialCalculator._assess_compliance_risk = _assess_compliance_risk
FinancialCalculator._identify_risk_factors = _identify_risk_factors
FinancialCalculator._generate_risk_recommendations = _generate_risk_recommendations
