from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import get_db
from models import FinancialMetrics, User
from schemas import FinancialMetricsResponse
from auth import get_current_active_user
from deps import get_request_company_id

router = APIRouter()

@router.get("/generate")
async def generate_insight(
    request: Request,
    period: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)

    # Fetch only this company's metrics (tenant isolation)
    metrics = db.query(FinancialMetrics).filter(
        FinancialMetrics.company_id == company_id,
        FinancialMetrics.period == period
    ).first()

    if not metrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metrics not found")

    # Prepare tenant-scoped payload for GPT-5 (no cross-tenant leakage)
    payload = {
        "company_id": str(company_id),
        "period": period,
        "metrics": {
            "gross_profit_margin": metrics.gross_profit_margin,
            "net_profit_margin": metrics.net_profit_margin,
            "current_ratio": metrics.current_ratio,
            "debt_to_equity": metrics.debt_to_equity,
            "interest_coverage_ratio": metrics.interest_coverage_ratio,
        }
    }

    # Placeholder: In production, call GPT-5 API with tenant-scoped payload
    narrative = (
        f"The company achieved a net profit margin of {metrics.net_profit_margin:.1f}% "
        f"and a current ratio of {metrics.current_ratio:.2f}. "
        f"Leverage stands at {metrics.debt_to_equity:.2f}. "
        "Recommend focusing on working capital optimization if current ratio is below 1.0."
    )

    return {"narrative": narrative, "tenant": str(company_id)}
