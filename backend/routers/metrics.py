from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import get_db
from models import FinancialData, FinancialMetrics, User
from schemas import FinancialMetricsResponse
from auth import get_current_active_user
from utils.financial_calculator import FinancialCalculator
from deps import get_request_company_id

router = APIRouter()
calculator = FinancialCalculator()

@router.post("/calculate", response_model=FinancialMetricsResponse)
async def calculate_financial_metrics(
    request: Request,
    period: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    
    # Get financial data for the period
    financial_data = db.query(FinancialData).filter(
        FinancialData.company_id == company_id,
        FinancialData.period == period
    ).first()
    
    if not financial_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial data not found for the specified period"
        )
    
    # Convert financial data to dictionary
    data_dict = {
        'revenue': financial_data.revenue,
        'sales_returns': financial_data.sales_returns,
        'net_sales': financial_data.net_sales,
        'cost_of_goods_sold': financial_data.cost_of_goods_sold,
        'gross_profit': financial_data.gross_profit,
        'salaries_wages': financial_data.salaries_wages,
        'rent_expense': financial_data.rent_expense,
        'utilities': financial_data.utilities,
        'marketing_expense': financial_data.marketing_expense,
        'administrative_expense': financial_data.administrative_expense,
        'depreciation': financial_data.depreciation,
        'other_operating_expense': financial_data.other_operating_expense,
        'operating_income': financial_data.operating_income,
        'interest_expense': financial_data.interest_expense,
        'tax_expense': financial_data.tax_expense,
        'net_income': financial_data.net_income,
        'cash': financial_data.cash,
        'accounts_receivable': financial_data.accounts_receivable,
        'inventory': financial_data.inventory,
        'current_assets': financial_data.current_assets,
        'fixed_assets': financial_data.fixed_assets,
        'total_assets': financial_data.total_assets,
        'accounts_payable': financial_data.accounts_payable,
        'short_term_debt': financial_data.short_term_debt,
        'current_liabilities': financial_data.current_liabilities,
        'long_term_debt': financial_data.long_term_debt,
        'total_liabilities': financial_data.total_liabilities,
        'equity': financial_data.equity,
        'operating_cash_flow': financial_data.operating_cash_flow,
        'investing_cash_flow': financial_data.investing_cash_flow,
        'financing_cash_flow': financial_data.financing_cash_flow,
        'net_cash_flow': financial_data.net_cash_flow
    }
    
    # Calculate financial metrics
    metrics = calculator.calculate_financial_metrics(data_dict)
    
    # Check if metrics already exist for this period
    existing_metrics = db.query(FinancialMetrics).filter(
        FinancialMetrics.company_id == company_id,
        FinancialMetrics.period == period
    ).first()
    
    if existing_metrics:
        # Update existing metrics
        for key, value in metrics.items():
            setattr(existing_metrics, key, value)
        db_metrics = existing_metrics
    else:
        # Create new metrics record
        db_metrics = FinancialMetrics(
            company_id=company_id,
            period=period,
            **metrics
        )
        db.add(db_metrics)
    
    db.commit()
    db.refresh(db_metrics)
    
    return db_metrics

@router.get("/history", response_model=List[FinancialMetricsResponse])
async def get_metrics_history(
    request: Request,
    limit: int = 12,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    
    # Get metrics history
    metrics_history = db.query(FinancialMetrics).filter(
        FinancialMetrics.company_id == company_id
    ).order_by(FinancialMetrics.period.desc()).limit(limit).all()
    
    return metrics_history

@router.get("/trends")
async def get_financial_trends(
    request: Request,
    metric: str,
    periods: int = 12,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    
    # Get metrics for trend analysis
    metrics_data = db.query(FinancialMetrics).filter(
        FinancialMetrics.company_id == company_id
    ).order_by(FinancialMetrics.period.asc()).limit(periods).all()
    
    if not metrics_data:
        return {"trend": [], "insights": []}
    
    # Extract trend data
    trend_data = []
    for metric_record in metrics_data:
        value = getattr(metric_record, metric, None)
        if value is not None:
            trend_data.append({
                "period": metric_record.period,
                "value": value
            })
    
    # Calculate trend insights
    insights = []
    if len(trend_data) >= 2:
        recent_values = [item["value"] for item in trend_data[-3:]]
        older_values = [item["value"] for item in trend_data[-6:-3]] if len(trend_data) >= 6 else trend_data[:-3]
        
        if older_values:
            recent_avg = sum(recent_values) / len(recent_values)
            older_avg = sum(older_values) / len(older_values)
            
            change_percent = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
            
            if change_percent > 10:
                insights.append(f"{metric.replace('_', ' ').title()} has improved by {change_percent:.1f}% in recent periods")
            elif change_percent < -10:
                insights.append(f"{metric.replace('_', ' ').title()} has declined by {abs(change_percent):.1f}% in recent periods")
            else:
                insights.append(f"{metric.replace('_', ' ').title()} remains stable with minimal change")
    
    return {
        "trend": trend_data,
        "insights": insights,
        "metric": metric,
        "periods_analyzed": len(trend_data)
    }

@router.get("/dashboard")
async def get_dashboard_metrics(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    
    # Get latest financial data
    latest_data = db.query(FinancialData).filter(
        FinancialData.company_id == company_id
    ).order_by(FinancialData.period.desc()).first()
    
    if not latest_data:
        return {"message": "No financial data available"}
    
    # Get latest metrics
    latest_metrics = db.query(FinancialMetrics).filter(
        FinancialMetrics.company_id == company_id
    ).order_by(FinancialMetrics.period.desc()).first()
    
    # Get historical data for trends
    historical_data = db.query(FinancialData).filter(
        FinancialData.company_id == company_id
    ).order_by(FinancialData.period.asc()).limit(12).all()
    
    # Prepare dashboard data
    dashboard_data = {
        "company_id": str(company_id),
        "current_period": latest_data.period,
        "key_metrics": {
            "revenue": latest_data.revenue,
            "net_income": latest_data.net_income,
            "total_assets": latest_data.total_assets,
            "current_ratio": getattr(latest_metrics, 'current_ratio', None),
            "debt_to_equity": getattr(latest_metrics, 'debt_to_equity', None),
            "net_profit_margin": getattr(latest_metrics, 'net_profit_margin', None)
        },
        "revenue_trend": [
            {"period": data.period, "revenue": data.revenue}
            for data in historical_data if data.revenue
        ],
        "profit_trend": [
            {"period": data.period, "profit": data.net_income}
            for data in historical_data if data.net_income
        ],
        "cash_flow_trend": [
            {"period": data.period, "cash_flow": data.net_cash_flow}
            for data in historical_data if data.net_cash_flow
        ]
    }
    
    return dashboard_data
