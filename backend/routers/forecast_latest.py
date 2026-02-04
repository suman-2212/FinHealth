from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from auth import get_current_active_user
from database import get_db
from models import User

router = APIRouter()

@router.get("/latest")
async def get_latest_forecast(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return {
        "revenue_forecast": [],
        "expense_forecast": [],
        "cash_flow_forecast": [],
        "growth_rate": 0,
        "confidence_level": 0.5
    }
