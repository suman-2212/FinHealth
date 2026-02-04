from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from models import RiskSummary
from database import get_db
from deps import get_request_company_id
from auth import get_current_active_user
from models import User
from utils.risk_analyzer import RiskAnalyzer
from sqlalchemy.sql import func

router = APIRouter()

@router.get("/risk-analysis")
async def get_risk_analysis(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive risk analysis for the current tenant's company"""
    
    company_id = get_request_company_id(request)
    
    # Try to get cached summary first
    summary = db.query(RiskSummary).filter(
        RiskSummary.company_id == company_id
    ).first()
    
    if summary:
        return {
            'overall_risk_score': float(summary.overall_risk_score) if summary.overall_risk_score else None,
            'overall_risk_level': summary.overall_risk_level,
            'component_breakdown': {
                'leverage': {
                    'score': float(summary.leverage_risk_score) if summary.leverage_risk_score else None,
                    'level': summary.leverage_risk_level,
                    'details': {
                        'debt_to_equity': float(summary.debt_to_equity) if summary.debt_to_equity else None
                    }
                },
                'liquidity': {
                    'score': float(summary.liquidity_risk_score) if summary.liquidity_risk_score else None,
                    'level': summary.liquidity_risk_level,
                    'details': {
                        'current_ratio': float(summary.current_ratio) if summary.current_ratio else None,
                        'quick_ratio': float(summary.quick_ratio) if summary.quick_ratio else None
                    }
                },
                'profitability': {
                    'score': float(summary.profitability_risk_score) if summary.profitability_risk_score else None,
                    'level': summary.profitability_risk_level,
                    'details': {
                        'net_margin': float(summary.net_margin) if summary.net_margin else None,
                        'net_income': float(summary.net_income) if summary.net_income else None
                    }
                },
                'cash_flow': {
                    'score': float(summary.cash_flow_risk_score) if summary.cash_flow_risk_score else None,
                    'level': summary.cash_flow_risk_level,
                    'details': {
                        'cash_flow_stability': float(summary.cash_flow_stability) if summary.cash_flow_stability else None,
                        'negative_cash_flow_months': summary.negative_cash_flow_months
                    }
                }
            },
            'mitigation_actions': summary.mitigation_actions or [],
            'last_updated': summary.last_updated.isoformat() if summary.last_updated else None
        }
    
    # If no cached summary, calculate on-demand
    analyzer = RiskAnalyzer()
    risk_data = analyzer.analyze_comprehensive_risk(company_id, db)
    
    # Cache the result if we have valid data
    if risk_data['overall_risk_score'] is not None:
        existing = db.query(RiskSummary).filter(
            RiskSummary.company_id == company_id
        ).first()
        
        if existing:
            existing.overall_risk_score = risk_data['overall_risk_score']
            existing.overall_risk_level = risk_data['overall_risk_level']
            existing.leverage_risk_score = risk_data['component_breakdown']['leverage']['score']
            existing.leverage_risk_level = risk_data['component_breakdown']['leverage']['level']
            existing.liquidity_risk_score = risk_data['component_breakdown']['liquidity']['score']
            existing.liquidity_risk_level = risk_data['component_breakdown']['liquidity']['level']
            existing.profitability_risk_score = risk_data['component_breakdown']['profitability']['score']
            existing.profitability_risk_level = risk_data['component_breakdown']['profitability']['level']
            existing.cash_flow_risk_score = risk_data['component_breakdown']['cash_flow']['score']
            existing.cash_flow_risk_level = risk_data['component_breakdown']['cash_flow']['level']
            existing.debt_to_equity = risk_data['component_breakdown']['leverage']['details'].get('debt_to_equity')
            existing.current_ratio = risk_data['component_breakdown']['liquidity']['details'].get('current_ratio')
            existing.quick_ratio = risk_data['component_breakdown']['liquidity']['details'].get('quick_ratio')
            existing.net_margin = risk_data['component_breakdown']['profitability']['details'].get('net_margin')
            existing.net_income = risk_data['component_breakdown']['profitability']['details'].get('net_income')
            existing.cash_flow_stability = risk_data['component_breakdown']['cash_flow']['details'].get('cash_flow_stability')
            existing.negative_cash_flow_months = risk_data['component_breakdown']['cash_flow']['details'].get('negative_cash_flow_months')
            existing.mitigation_actions = risk_data['mitigation_actions']
            existing.last_updated = func.now()
        else:
            new_summary = RiskSummary(
                company_id=company_id,
                overall_risk_score=risk_data['overall_risk_score'],
                overall_risk_level=risk_data['overall_risk_level'],
                leverage_risk_score=risk_data['component_breakdown']['leverage']['score'],
                leverage_risk_level=risk_data['component_breakdown']['leverage']['level'],
                liquidity_risk_score=risk_data['component_breakdown']['liquidity']['score'],
                liquidity_risk_level=risk_data['component_breakdown']['liquidity']['level'],
                profitability_risk_score=risk_data['component_breakdown']['profitability']['score'],
                profitability_risk_level=risk_data['component_breakdown']['profitability']['level'],
                cash_flow_risk_score=risk_data['component_breakdown']['cash_flow']['score'],
                cash_flow_risk_level=risk_data['component_breakdown']['cash_flow']['level'],
                debt_to_equity=risk_data['component_breakdown']['leverage']['details'].get('debt_to_equity'),
                current_ratio=risk_data['component_breakdown']['liquidity']['details'].get('current_ratio'),
                quick_ratio=risk_data['component_breakdown']['liquidity']['details'].get('quick_ratio'),
                net_margin=risk_data['component_breakdown']['profitability']['details'].get('net_margin'),
                net_income=risk_data['component_breakdown']['profitability']['details'].get('net_income'),
                cash_flow_stability=risk_data['component_breakdown']['cash_flow']['details'].get('cash_flow_stability'),
                negative_cash_flow_months=risk_data['component_breakdown']['cash_flow']['details'].get('negative_cash_flow_months'),
                mitigation_actions=risk_data['mitigation_actions']
            )
            db.add(new_summary)
        
        db.commit()
    
    return risk_data
