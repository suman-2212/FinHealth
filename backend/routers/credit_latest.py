from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from auth import get_current_active_user
from database import get_db
from models import User

router = APIRouter()

@router.get("/latest")
async def get_latest_credit(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return {
        "credit_score": None,
        "credit_grade": "No Data",
        "score_explanation": "No credit data available"
    }
