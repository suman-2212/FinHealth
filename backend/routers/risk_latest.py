from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from auth import get_current_active_user
from database import get_db
from deps import get_request_company_id
from models import User, RiskSummary

router = APIRouter()

@router.get("/latest")
async def get_latest_risk(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    risk = db.query(RiskSummary).filter(RiskSummary.company_id == company_id).first()
    if risk:
        return {
            "overall_risk": risk.risk_level,
            "risk_level": risk.risk_level,
            "debt_to_equity": float(risk.debt_to_equity) if risk.debt_to_equity else None,
            "total_debt": float(risk.total_debt) if risk.total_debt else None,
            "equity": float(risk.equity) if risk.equity else None,
            "recommendations": []
        }
    else:
        return {
            "overall_risk": None,
            "risk_level": "No Data",
            "debt_to_equity": None,
            "total_debt": None,
            "equity": None,
            "recommendations": []
        }
