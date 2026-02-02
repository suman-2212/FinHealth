from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# User Schemas
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class CompanyBrief(BaseModel):
    id: uuid.UUID
    name: str
    industry: str

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    companies: List[CompanyBrief]
    default_company_id: Optional[uuid.UUID] = None

class TokenData(BaseModel):
    email: Optional[str] = None

# Company Schemas
class CompanyCreate(BaseModel):
    name: str
    industry: str
    registration_number: Optional[str] = None

class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    industry: str
    registration_number: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Financial Data Schemas
class FinancialDataCreate(BaseModel):
    period: str
    data_type: str
    
    # Income Statement
    revenue: Optional[float] = None
    sales_returns: Optional[float] = None
    net_sales: Optional[float] = None
    cost_of_goods_sold: Optional[float] = None
    gross_profit: Optional[float] = None
    salaries_wages: Optional[float] = None
    rent_expense: Optional[float] = None
    utilities: Optional[float] = None
    marketing_expense: Optional[float] = None
    administrative_expense: Optional[float] = None
    depreciation: Optional[float] = None
    other_operating_expense: Optional[float] = None
    operating_income: Optional[float] = None
    interest_expense: Optional[float] = None
    tax_expense: Optional[float] = None
    net_income: Optional[float] = None
    
    # Balance Sheet
    cash: Optional[float] = None
    accounts_receivable: Optional[float] = None
    inventory: Optional[float] = None
    current_assets: Optional[float] = None
    fixed_assets: Optional[float] = None
    total_assets: Optional[float] = None
    accounts_payable: Optional[float] = None
    short_term_debt: Optional[float] = None
    current_liabilities: Optional[float] = None
    long_term_debt: Optional[float] = None
    total_liabilities: Optional[float] = None
    equity: Optional[float] = None
    
    # Cash Flow
    operating_cash_flow: Optional[float] = None
    investing_cash_flow: Optional[float] = None
    financing_cash_flow: Optional[float] = None
    net_cash_flow: Optional[float] = None

class FinancialDataResponse(BaseModel):
    id: uuid.UUID
    period: str
    data_type: str
    revenue: Optional[float]
    net_income: Optional[float]
    total_assets: Optional[float]
    upload_date: datetime
    
    class Config:
        from_attributes = True

# Financial Metrics Schemas
class FinancialMetricsResponse(BaseModel):
    id: uuid.UUID
    period: str
    
    # Profitability
    gross_profit_margin: Optional[float]
    net_profit_margin: Optional[float]
    operating_margin: Optional[float]
    return_on_assets: Optional[float]
    return_on_equity: Optional[float]
    
    # Liquidity
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    cash_ratio: Optional[float]
    
    # Leverage
    debt_to_equity: Optional[float]
    debt_to_assets: Optional[float]
    interest_coverage_ratio: Optional[float]
    
    # Efficiency
    asset_turnover: Optional[float]
    inventory_turnover: Optional[float]
    accounts_receivable_turnover: Optional[float]
    accounts_payable_turnover: Optional[float]
    
    # Working Capital
    working_capital: Optional[float]
    cash_conversion_cycle: Optional[float]
    
    calculated_at: datetime
    
    class Config:
        from_attributes = True

# Risk Assessment Schemas
class RiskAssessmentResponse(BaseModel):
    id: uuid.UUID
    period: str
    
    liquidity_risk: Optional[float]
    solvency_risk: Optional[float]
    operational_risk: Optional[float]
    compliance_risk: Optional[float]
    overall_risk: Optional[float]
    
    risk_level: Optional[str]
    risk_factors: Optional[Dict[str, Any]]
    recommendations: Optional[List[str]]
    
    assessed_at: datetime
    
    class Config:
        from_attributes = True

# Credit Score Schemas
class CreditScoreResponse(BaseModel):
    id: uuid.UUID
    period: str
    
    profitability_score: Optional[float]
    liquidity_score: Optional[float]
    leverage_score: Optional[float]
    cash_stability_score: Optional[float]
    tax_compliance_score: Optional[float]
    industry_risk_modifier: Optional[float]
    
    credit_score: Optional[float]
    credit_grade: Optional[str]
    
    score_explanation: Optional[str]
    improvement_suggestions: Optional[List[str]]
    
    calculated_at: datetime
    
    class Config:
        from_attributes = True

# Forecast Schemas
class ForecastRequest(BaseModel):
    periods: int = 12  # Number of months to forecast
    forecast_type: str = "financial"  # "financial", "cash_flow", "revenue"

class ForecastResponse(BaseModel):
    period: str
    forecast_type: str
    
    # Forecasted values
    revenue_forecast: List[float]
    expense_forecast: List[float]
    cash_flow_forecast: List[float]
    profit_forecast: List[float]
    
    # Confidence intervals
    confidence_level: float
    upper_bound: List[float]
    lower_bound: List[float]
    
    # Key insights
    growth_rate: float
    cash_runway_months: int
    risk_indicators: List[str]
    
    generated_at: datetime

# Loan Product Schemas
class LoanProductResponse(BaseModel):
    id: uuid.UUID
    product_name: str
    provider: str
    product_type: str
    
    min_revenue: Optional[float]
    max_revenue: Optional[float]
    min_credit_score: Optional[float]
    max_loan_amount: Optional[float]
    interest_rate: Optional[float]
    tenure_months: Optional[int]
    
    supported_industries: Optional[List[str]]
    risk_appetite: Optional[str]
    
    class Config:
        from_attributes = True

class LoanRecommendationRequest(BaseModel):
    loan_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    preferred_tenure: Optional[int] = None

class LoanRecommendationResponse(BaseModel):
    recommended_products: List[LoanProductResponse]
    eligibility_score: float
    matching_criteria: Dict[str, Any]
    alternative_options: List[LoanProductResponse]

# Industry Benchmark Schemas
class BenchmarkRequest(BaseModel):
    industry: str
    metrics: List[str] = ["all"]

class BenchmarkResponse(BaseModel):
    industry: str
    company_metrics: Dict[str, float]
    industry_averages: Dict[str, float]
    percentile_rankings: Dict[str, float]
    gap_analysis: Dict[str, str]
    
    class Config:
        from_attributes = True

# Report Schemas
class ReportRequest(BaseModel):
    report_type: str  # "financial_health", "credit_analysis", "investor_report"
    period: str
    include_forecasts: bool = True
    language: str = "en"

class ReportResponse(BaseModel):
    report_id: uuid.UUID
    report_type: str
    period: str
    
    # Report content
    executive_summary: str
    financial_health_score: float
    key_metrics: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    recommendations: List[str]
    
    # File information
    file_url: str
    file_size: int
    generated_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardResponse(BaseModel):
    company: CompanyResponse
    current_period: str
    
    # Key metrics
    financial_health_score: float
    revenue_trend: List[Dict[str, Any]]
    expense_trend: List[Dict[str, Any]]
    cash_flow_trend: List[Dict[str, Any]]
    
    # Risk indicators
    debt_risk_level: str
    cash_runway_months: int
    accounts_receivable_aging: List[Dict[str, Any]]
    
    # AI insights
    ai_insights: List[str]
    top_recommendations: List[str]
    
    # Benchmark data
    industry_benchmark: Optional[BenchmarkResponse]
    
    class Config:
        from_attributes = True

# File Upload Schemas
class FileUploadResponse(BaseModel):
    file_id: uuid.UUID
    filename: str
    file_size: int
    upload_status: str
    parsed_data: Optional[Dict[str, Any]]
    errors: Optional[List[str]]
    metrics_generated: Optional[bool] = False
    period: Optional[str] = None
    
    class Config:
        from_attributes = True
