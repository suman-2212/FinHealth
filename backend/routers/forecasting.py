from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from models import ForecastSummary
from database import get_db
from deps import get_request_company_id
from auth import get_current_active_user
from models import User
from utils.financial_forecaster import FinancialForecaster
from typing import Optional

router = APIRouter()

@router.get("/forecast")
async def get_forecast(
    request: Request,
    months_ahead: Optional[int] = 6,
    forecast_type: Optional[str] = 'Base',
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get financial forecast for the current tenant's company"""
    
    company_id = get_request_company_id(request)
    
    # Validate forecast type
    valid_types = ['Base', 'Optimistic', 'Conservative']
    if forecast_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid forecast type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Validate months ahead
    if months_ahead < 1 or months_ahead > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Months ahead must be between 1 and 12"
        )
    
    # Try to get cached forecast first
    cached_forecasts = db.query(ForecastSummary).filter(
        ForecastSummary.company_id == company_id,
        ForecastSummary.forecast_type == forecast_type
    ).order_by(ForecastSummary.projection_month).limit(months_ahead).all()
    
    if cached_forecasts and len(cached_forecasts) >= months_ahead:
        # Return cached data
        projections = []
        for forecast in cached_forecasts:
            projections.append({
                'projection_month': forecast.projection_month,
                'projected_revenue': float(forecast.projected_revenue),
                'projected_expenses': float(forecast.projected_expenses),
                'projected_net_income': float(forecast.projected_net_income),
                'projected_cash_flow': float(forecast.projected_cash_flow)
            })
        
        # Get metadata from first forecast
        first = cached_forecasts[0]
        
        # Calculate runway from projections
        cash_flows = [p['projected_cash_flow'] for p in projections]
        current_cash = cash_flows[0] if cash_flows else 0
        negative_flows = [cf for cf in cash_flows if cf < 0]
        avg_burn = abs(sum(negative_flows) / len(negative_flows)) if negative_flows else 0
        runway = current_cash / avg_burn if avg_burn > 0 else 999.99
        
        return {
            'forecast_type': forecast_type,
            'months_ahead': months_ahead,
            'historical_months_used': first.months_used,
            'projections': projections,
            'runway_months': runway,
            'confidence_score': float(first.confidence_score),
            'revenue_growth_rate': float(first.revenue_growth_rate),
            'expense_growth_rate': float(first.expense_growth_rate),
            'cash_flow_volatility': float(first.cash_flow_volatility),
            'last_updated': first.created_at.isoformat() if first.created_at else None
        }
    
    # If no cached forecast or insufficient data, generate new forecast
    forecaster = FinancialForecaster()
    forecast_data = forecaster.generate_forecast(
        company_id, db, months_ahead, forecast_type
    )
    
    return forecast_data
