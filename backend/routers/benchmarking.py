from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request
from models import BenchmarkSummary
from database import get_db
from deps import get_request_company_id
from auth import get_current_active_user
from models import User
from utils.benchmark_analyzer import BenchmarkAnalyzer

router = APIRouter()

@router.get("/benchmark")
async def get_benchmark(
    request: Request,
    industry_type: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get benchmark analysis for the current tenant's company"""
    
    company_id = get_request_company_id(request)
    
    # Try to get cached benchmark summary first
    summary = db.query(BenchmarkSummary).filter(
        BenchmarkSummary.company_id == company_id
    ).first()
    
    if summary:
        # Reconstruct benchmark results from stored data
        benchmark_results = {}
        
        if summary.net_profit_margin:
            benchmark_results['net_profit_margin'] = summary.net_profit_margin
        if summary.gross_margin:
            benchmark_results['gross_margin'] = summary.gross_margin
        if summary.debt_to_equity:
            benchmark_results['debt_to_equity'] = summary.debt_to_equity
        if summary.current_ratio:
            benchmark_results['current_ratio'] = summary.current_ratio
        if summary.quick_ratio:
            benchmark_results['quick_ratio'] = summary.quick_ratio
        if summary.revenue_growth_rate:
            benchmark_results['revenue_growth_rate'] = summary.revenue_growth_rate
        if summary.operating_margin:
            benchmark_results['operating_margin'] = summary.operating_margin
        if summary.cash_conversion_cycle:
            benchmark_results['cash_conversion_cycle'] = summary.cash_conversion_cycle
        
        overall_summary = {
            'overall_percentile': float(summary.overall_percentile) if summary.overall_percentile else 0,
            'metrics_above_avg': summary.metrics_above_avg or 0,
            'total_metrics': summary.total_metrics or 0,
            'summary_text': f"Your company ranks in the {summary.overall_percentile:.0f}th percentile in the {summary.industry_type} sector" if summary.overall_percentile else "No data available"
        }
        
        return {
            'industry_type': summary.industry_type or 'Unknown',
            'industry_description': BenchmarkAnalyzer().INDUSTRY_TYPES.get(summary.industry_type, {}).get('description', 'Unknown industry'),
            'benchmark_results': benchmark_results,
            'overall_summary': overall_summary,
            'last_updated': summary.last_updated.isoformat() if summary.last_updated else None
        }
    
    # If no cached summary, calculate on-demand
    analyzer = BenchmarkAnalyzer()
    benchmark_data = analyzer.analyze_benchmarks(company_id, db, industry_type)
    
    return benchmark_data
