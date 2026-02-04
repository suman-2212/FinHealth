from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from models import MonthlySummary, RiskSummary
from database import get_db
from deps import get_request_company_id
from auth import get_current_active_user
from models import User
from typing import List, Dict, Any

router = APIRouter()

@router.get("/dashboard-summary")
async def get_dashboard_summary(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    # Get latest 12 months of summaries
    summaries = db.query(MonthlySummary).filter(
        MonthlySummary.company_id == company_id
    ).order_by(MonthlySummary.month.desc()).limit(12).all()
    print(f"[DASHBOARD SUMMARY] Found {len(summaries)} summaries for company {company_id}")
    if not summaries:
        print("[DASHBOARD SUMMARY] No summaries found")
        return {
            "revenue": None,
            "net_income": None,
            "total_assets": None,
            "current_ratio": None,
            "financial_health_score": None,
            "revenue_trend": [],
            "cash_flow_trend": [],
            "health_trend": [],
            "months": []
        }
    # Latest month
    latest = summaries[0]
    print(f"[DASHBOARD SUMMARY] Latest month: {latest.month}, revenue: {latest.revenue}, net_income: {latest.net_income}")
    # Get latest risk metrics
    risk = db.query(RiskSummary).filter(RiskSummary.company_id == company_id).first()
    debt_to_equity = float(risk.debt_to_equity) if risk and risk.debt_to_equity else None
    # Prepare trends
    revenue_trend = [(s.month, s.revenue or 0) for s in reversed(summaries)]
    cash_flow_trend = [(s.month, s.operating_cash_flow or 0) for s in reversed(summaries)]
    health_trend = [(s.month, s.financial_health_score or 0) for s in reversed(summaries)]
    result = {
        "revenue": latest.revenue,
        "net_income": latest.net_income,
        "total_assets": latest.total_assets,
        "current_ratio": latest.current_ratio,
        "financial_health_score": latest.financial_health_score,
        "debt_to_equity": debt_to_equity,  # Use authoritative value from RiskSummary
        "revenue_trend": revenue_trend,
        "cash_flow_trend": cash_flow_trend,
        "health_trend": health_trend,
        "months": [s.month for s in reversed(summaries)]
    }
    print(f"[DASHBOARD SUMMARY] Returning: {result}")
    return result
