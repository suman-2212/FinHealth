from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from models import FinancialHealthSummary
from database import get_db
from deps import get_request_company_id
from auth import get_current_active_user
from models import User
from utils.financial_health_calculator import FinancialHealthCalculator
from sqlalchemy.sql import func

router = APIRouter()

@router.get("/financial-health")
async def get_financial_health(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive financial health analysis for the current tenant's company"""
    
    company_id = get_request_company_id(request)
    
    # Try to get cached summary first
    summary = db.query(FinancialHealthSummary).filter(
        FinancialHealthSummary.company_id == company_id
    ).first()
    
    if summary:
        return {
            'health_score': float(summary.health_score) if summary.health_score else None,
            'health_category': summary.health_category,
            'component_scores': {
                'profitability': float(summary.profitability_score) if summary.profitability_score else None,
                'liquidity': float(summary.liquidity_score) if summary.liquidity_score else None,
                'leverage': float(summary.leverage_score) if summary.leverage_score else None,
                'cash_flow': float(summary.cash_flow_score) if summary.cash_flow_score else None,
                'growth': float(summary.growth_score) if summary.growth_score else None
            },
            'component_details': {
                'net_margin': float(summary.net_margin) if summary.net_margin else None,
                'current_ratio': float(summary.current_ratio) if summary.current_ratio else None,
                'debt_to_equity': float(summary.debt_to_equity) if summary.debt_to_equity else None,
                'cash_flow_stability': float(summary.cash_flow_stability) if summary.cash_flow_stability else None,
                'revenue_growth_rate': float(summary.revenue_growth_rate) if summary.revenue_growth_rate else None
            },
            'improvement_recommendations': summary.improvement_recommendations or [],
            'last_updated': summary.last_updated.isoformat() if summary.last_updated else None
        }
    
    # If no cached summary, calculate on-demand
    calculator = FinancialHealthCalculator()
    health_data = calculator.calculate_comprehensive_health(company_id, db)
    
    # Cache the result if we have valid data
    if health_data['health_score'] is not None:
        existing = db.query(FinancialHealthSummary).filter(
            FinancialHealthSummary.company_id == company_id
        ).first()
        
        if existing:
            existing.health_score = health_data['health_score']
            existing.health_category = health_data['health_category']
            existing.profitability_score = health_data['component_scores']['profitability']
            existing.liquidity_score = health_data['component_scores']['liquidity']
            existing.leverage_score = health_data['component_scores']['leverage']
            existing.cash_flow_score = health_data['component_scores']['cash_flow']
            existing.growth_score = health_data['component_scores']['growth']
            existing.net_margin = health_data['component_details']['net_margin']
            existing.current_ratio = health_data['component_details']['current_ratio']
            existing.debt_to_equity = health_data['component_details']['debt_to_equity']
            existing.cash_flow_stability = health_data['component_details']['cash_flow_stability']
            existing.revenue_growth_rate = health_data['component_details']['revenue_growth_rate']
            existing.improvement_recommendations = health_data['improvement_recommendations']
            existing.last_updated = func.now()
        else:
            new_summary = FinancialHealthSummary(
                company_id=company_id,
                health_score=health_data['health_score'],
                health_category=health_data['health_category'],
                profitability_score=health_data['component_scores']['profitability'],
                liquidity_score=health_data['component_scores']['liquidity'],
                leverage_score=health_data['component_scores']['leverage'],
                cash_flow_score=health_data['component_scores']['cash_flow'],
                growth_score=health_data['component_scores']['growth'],
                net_margin=health_data['component_details']['net_margin'],
                current_ratio=health_data['component_details']['current_ratio'],
                debt_to_equity=health_data['component_details']['debt_to_equity'],
                cash_flow_stability=health_data['component_details']['cash_flow_stability'],
                revenue_growth_rate=health_data['component_details']['revenue_growth_rate'],
                improvement_recommendations=health_data['improvement_recommendations']
            )
            db.add(new_summary)
        
        db.commit()
    
    return health_data
