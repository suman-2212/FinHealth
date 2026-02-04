from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from models import CreditScoreSummary
from database import get_db
from deps import get_request_company_id
from auth import get_current_active_user
from models import User
from utils.credit_scorer import CreditScorer
from sqlalchemy.sql import func

router = APIRouter()

@router.get("/credit-evaluation")
async def get_credit_evaluation(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive credit evaluation for the current tenant's company"""
    
    company_id = get_request_company_id(request)
    
    # Try to get cached summary first
    summary = db.query(CreditScoreSummary).filter(
        CreditScoreSummary.company_id == company_id
    ).first()
    
    if summary:
        return {
            'credit_score': float(summary.credit_score) if summary.credit_score else None,
            'credit_rating': summary.credit_rating,
            'component_scores': {
                'profitability': float(summary.profitability_score) if summary.profitability_score else None,
                'liquidity': float(summary.liquidity_score) if summary.liquidity_score else None,
                'leverage': float(summary.leverage_score) if summary.leverage_score else None,
                'cash_flow': float(summary.cash_flow_score) if summary.cash_flow_score else None,
                'growth': float(summary.growth_score) if summary.growth_score else None
            },
            'repayment_capacity_ratio': float(summary.repayment_capacity_ratio) if summary.repayment_capacity_ratio else None,
            'loan_eligibility_status': summary.loan_eligibility_status,
            'risk_flags': summary.risk_flags or [],
            'component_details': {
                'net_margin': float(summary.net_margin) if summary.net_margin else None,
                'current_ratio': float(summary.current_ratio) if summary.current_ratio else None,
                'quick_ratio': float(summary.quick_ratio) if summary.quick_ratio else None,
                'debt_to_equity': float(summary.debt_to_equity) if summary.debt_to_equity else None,
                'cash_flow_stability': float(summary.cash_flow_stability) if summary.cash_flow_stability else None,
                'revenue_growth_rate': float(summary.revenue_growth_rate) if summary.revenue_growth_rate else None
            },
            'improvement_recommendations': summary.improvement_recommendations or [],
            'last_updated': summary.last_updated.isoformat() if summary.last_updated else None
        }
    
    # If no cached summary, calculate on-demand
    scorer = CreditScorer()
    credit_data = scorer.calculate_credit_score(company_id, db)
    
    # Cache the result if we have valid data
    if credit_data['credit_score'] is not None:
        existing = db.query(CreditScoreSummary).filter(
            CreditScoreSummary.company_id == company_id
        ).first()
        
        if existing:
            existing.credit_score = credit_data['credit_score']
            existing.credit_rating = credit_data['credit_rating']
            existing.profitability_score = credit_data['component_scores']['profitability']
            existing.liquidity_score = credit_data['component_scores']['liquidity']
            existing.leverage_score = credit_data['component_scores']['leverage']
            existing.cash_flow_score = credit_data['component_scores']['cash_flow']
            existing.growth_score = credit_data['component_scores']['growth']
            existing.repayment_capacity_ratio = credit_data['repayment_capacity_ratio']
            existing.loan_eligibility_status = credit_data['loan_eligibility_status']
            existing.risk_flags = credit_data['risk_flags']
            existing.net_margin = credit_data['component_details']['net_margin']
            existing.current_ratio = credit_data['component_details']['current_ratio']
            existing.quick_ratio = credit_data['component_details']['quick_ratio']
            existing.debt_to_equity = credit_data['component_details']['debt_to_equity']
            existing.cash_flow_stability = credit_data['component_details']['cash_flow_stability']
            existing.revenue_growth_rate = credit_data['component_details']['revenue_growth_rate']
            existing.improvement_recommendations = credit_data['improvement_recommendations']
            existing.last_updated = func.now()
        else:
            new_summary = CreditScoreSummary(
                company_id=company_id,
                credit_score=credit_data['credit_score'],
                credit_rating=credit_data['credit_rating'],
                profitability_score=credit_data['component_scores']['profitability'],
                liquidity_score=credit_data['component_scores']['liquidity'],
                leverage_score=credit_data['component_scores']['leverage'],
                cash_flow_score=credit_data['component_scores']['cash_flow'],
                growth_score=credit_data['component_scores']['growth'],
                repayment_capacity_ratio=credit_data['repayment_capacity_ratio'],
                loan_eligibility_status=credit_data['loan_eligibility_status'],
                risk_flags=credit_data['risk_flags'],
                net_margin=credit_data['component_details']['net_margin'],
                current_ratio=credit_data['component_details']['current_ratio'],
                quick_ratio=credit_data['component_details']['quick_ratio'],
                debt_to_equity=credit_data['component_details']['debt_to_equity'],
                cash_flow_stability=credit_data['component_details']['cash_flow_stability'],
                revenue_growth_rate=credit_data['component_details']['revenue_growth_rate'],
                improvement_recommendations=credit_data['improvement_recommendations']
            )
            db.add(new_summary)
        
        db.commit()
    
    return credit_data
