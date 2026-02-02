from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, JSON, UUID, UniqueConstraint, Index, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, default="viewer")  # admin, analyst, viewer
    profile_image_url = Column(String, nullable=True)
    preferred_language = Column(String, default="en")  # en, hi
    timezone = Column(String, default="UTC")
    notification_preferences = Column(JSON, default=dict)
    two_fa_enabled = Column(Boolean, default=False)
    two_fa_secret = Column(String, nullable=True)  # For TOTP
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company_links = relationship("UserCompany", back_populates="user", cascade="all, delete-orphan")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    registration_number = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional company settings
    financial_year_start = Column(Integer, default=1)
    currency = Column(String(10), default="USD")
    gst_number = Column(String(50), default="")
    
    user_links = relationship("UserCompany", back_populates="company", cascade="all, delete-orphan")
    financial_data = relationship("FinancialData", back_populates="company")
    metrics = relationship("FinancialMetrics", back_populates="company")
    risk_assessments = relationship("RiskAssessment", back_populates="company")
    credit_scores = relationship("CreditScore", back_populates="company")


class UserCompany(Base):
    __tablename__ = "user_companies"
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company"),
        Index("ix_user_companies_user_id", "user_id"),
        Index("ix_user_companies_company_id", "company_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    role = Column(String, nullable=False, default="owner")  # owner/admin/member
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="company_links")
    company = relationship("Company", back_populates="user_links")

class FinancialData(Base):
    __tablename__ = "financial_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    period = Column(String, nullable=False)  # e.g., "2023-12"
    data_type = Column(String, nullable=False)  # "income_statement", "balance_sheet", "cash_flow"
    
    # Revenue and Sales
    revenue = Column(Float)
    sales_returns = Column(Float)
    net_sales = Column(Float)
    
    # Cost of Goods Sold
    cost_of_goods_sold = Column(Float)
    gross_profit = Column(Float)
    
    # Operating Expenses
    salaries_wages = Column(Float)
    rent_expense = Column(Float)
    utilities = Column(Float)
    marketing_expense = Column(Float)
    administrative_expense = Column(Float)
    depreciation = Column(Float)
    other_operating_expense = Column(Float)
    
    # Profit and Loss
    operating_income = Column(Float)
    interest_expense = Column(Float)
    tax_expense = Column(Float)
    net_income = Column(Float)
    
    # Balance Sheet Items
    cash = Column(Float)
    accounts_receivable = Column(Float)
    inventory = Column(Float)
    current_assets = Column(Float)
    fixed_assets = Column(Float)
    total_assets = Column(Float)
    
    accounts_payable = Column(Float)
    short_term_debt = Column(Float)
    current_liabilities = Column(Float)
    long_term_debt = Column(Float)
    total_liabilities = Column(Float)
    equity = Column(Float)
    
    # Cash Flow
    operating_cash_flow = Column(Float)
    investing_cash_flow = Column(Float)
    financing_cash_flow = Column(Float)
    net_cash_flow = Column(Float)
    
    # Additional metadata
    file_name = Column(String)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="financial_data")

class FinancialMetrics(Base):
    __tablename__ = "financial_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    period = Column(String, nullable=False)
    
    # Profitability Ratios
    gross_profit_margin = Column(Float)
    net_profit_margin = Column(Float)
    operating_margin = Column(Float)
    return_on_assets = Column(Float)
    return_on_equity = Column(Float)
    
    # Liquidity Ratios
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    cash_ratio = Column(Float)
    
    # Leverage Ratios
    debt_to_equity = Column(Float)
    debt_to_assets = Column(Float)
    interest_coverage_ratio = Column(Float)
    
    # Efficiency Ratios
    asset_turnover = Column(Float)
    inventory_turnover = Column(Float)
    accounts_receivable_turnover = Column(Float)
    accounts_payable_turnover = Column(Float)
    
    # Working Capital
    working_capital = Column(Float)
    cash_conversion_cycle = Column(Float)
    
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="metrics")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    period = Column(String, nullable=False)
    
    # Risk Scores
    liquidity_risk = Column(Float)
    solvency_risk = Column(Float)
    operational_risk = Column(Float)
    compliance_risk = Column(Float)
    overall_risk = Column(Float)
    
    # Risk Categories
    risk_level = Column(String)  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    
    # Risk Factors
    risk_factors = Column(JSON)
    recommendations = Column(JSON)
    
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="risk_assessments")

class CreditScore(Base):
    __tablename__ = "credit_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    period = Column(String, nullable=False)
    
    # Credit Score Components
    profitability_score = Column(Float)
    liquidity_score = Column(Float)
    leverage_score = Column(Float)
    cash_stability_score = Column(Float)
    tax_compliance_score = Column(Float)
    industry_risk_modifier = Column(Float)
    
    # Final Score
    credit_score = Column(Float)  # 0-100
    credit_grade = Column(String)  # "A+", "A", "B+", "B", "C", "D"
    
    # AI-generated narrative
    score_explanation = Column(Text)
    improvement_suggestions = Column(JSON)
    
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="credit_scores")

class IndustryBenchmark(Base):
    __tablename__ = "industry_benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry = Column(String, nullable=False)
    
    # Average Ratios
    avg_gross_profit_margin = Column(Float)
    avg_net_profit_margin = Column(Float)
    avg_current_ratio = Column(Float)
    avg_quick_ratio = Column(Float)
    avg_debt_to_equity = Column(Float)
    avg_interest_coverage = Column(Float)
    avg_asset_turnover = Column(Float)
    avg_inventory_turnover = Column(Float)
    
    # Risk Metrics
    avg_working_capital_days = Column(Float)
    avg_cash_conversion_cycle = Column(Float)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class LoanProduct(Base):
    __tablename__ = "loan_products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    product_type = Column(String, nullable=False)  # "term_loan", "working_capital", "overdraft"
    
    # Eligibility Criteria
    min_revenue = Column(Float)
    max_revenue = Column(Float)
    min_credit_score = Column(Float)
    max_loan_amount = Column(Float)
    interest_rate = Column(Float)
    tenure_months = Column(Integer)
    
    # Target Industries
    supported_industries = Column(JSON)
    
    # Risk Appetite
    risk_appetite = Column(String)  # "CONSERVATIVE", "MODERATE", "AGGRESSIVE"
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    period = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LoanObligation(Base):
    __tablename__ = "loan_obligations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    lender = Column(String, nullable=False)
    principal_outstanding = Column(Float, nullable=False)
    interest_rate = Column(Float)
    monthly_emi = Column(Float)
    start_date = Column(String)
    end_date = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Receivable(Base):
    __tablename__ = "receivables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    invoice_no = Column(String)
    customer = Column(String)
    amount = Column(Float, nullable=False)
    due_date = Column(String)
    status = Column(String, default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Payable(Base):
    __tablename__ = "payables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    bill_no = Column(String)
    vendor = Column(String)
    amount = Column(Float, nullable=False)
    due_date = Column(String)
    status = Column(String, default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TaxRecord(Base):
    __tablename__ = "tax_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    period = Column(String, nullable=False)
    tax_type = Column(String, nullable=False)  # gst/tds/it
    amount = Column(Float)
    compliance_flag = Column(Boolean, default=False)
    tax_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MonthlySummary(Base):
    __tablename__ = "monthly_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    month = Column(String(7), nullable=False)  # YYYY-MM
    revenue = Column(Numeric(15, 2))
    operating_expense = Column(Numeric(15, 2))
    interest_expense = Column(Numeric(15, 2))
    tax_expense = Column(Numeric(15, 2))
    net_income = Column(Numeric(15, 2))
    total_assets = Column(Numeric(15, 2))
    current_assets = Column(Numeric(15, 2))
    current_liabilities = Column(Numeric(15, 2))
    equity = Column(Numeric(15, 2))
    operating_cash_flow = Column(Numeric(15, 2))
    gross_margin = Column(Numeric(5, 4))
    net_margin = Column(Numeric(5, 4))
    current_ratio = Column(Numeric(8, 4))
    debt_to_equity = Column(Numeric(8, 4))
    financial_health_score = Column(Numeric(5, 2))
    statement_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    __table_args__ = (UniqueConstraint('company_id', 'month', name='_company_month_uc'),)

class RiskSummary(Base):
    __tablename__ = "risk_summaries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    
    # Overall risk
    overall_risk_score = Column(Numeric(5, 2))  # 0-100
    overall_risk_level = Column(String(20))  # Low, Moderate, High, Critical
    
    # Component risk scores (0-100)
    leverage_risk_score = Column(Numeric(5, 2))
    liquidity_risk_score = Column(Numeric(5, 2))
    profitability_risk_score = Column(Numeric(5, 2))
    cash_flow_risk_score = Column(Numeric(5, 2))
    
    # Component risk levels
    leverage_risk_level = Column(String(20))
    liquidity_risk_level = Column(String(20))
    profitability_risk_level = Column(String(20))
    cash_flow_risk_level = Column(String(20))
    
    # Component details for transparency
    debt_to_equity = Column(Numeric(8, 4))
    current_ratio = Column(Numeric(8, 4))
    quick_ratio = Column(Numeric(8, 4))
    net_margin = Column(Numeric(5, 4))
    net_income = Column(Numeric(15, 2))
    cash_flow_stability = Column(Numeric(5, 2))
    negative_cash_flow_months = Column(Integer)
    
    # Mitigation recommendations
    mitigation_actions = Column(JSON)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FinancialHealthSummary(Base):
    __tablename__ = "financial_health_summaries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    health_score = Column(Numeric(5, 2))  # 0-100
    health_category = Column(String(20))  # Excellent, Good, Moderate, Weak, Critical
    
    # Component scores (0-100 each)
    profitability_score = Column(Numeric(5, 2))
    liquidity_score = Column(Numeric(5, 2))
    leverage_score = Column(Numeric(5, 2))
    cash_flow_score = Column(Numeric(5, 2))
    growth_score = Column(Numeric(5, 2))
    
    # Component details for recommendations
    net_margin = Column(Numeric(5, 4))
    current_ratio = Column(Numeric(8, 4))
    debt_to_equity = Column(Numeric(8, 4))
    cash_flow_stability = Column(Numeric(5, 2))  # Coefficient of variation
    revenue_growth_rate = Column(Numeric(5, 4))
    
    # Recommendations JSON
    improvement_recommendations = Column(JSON)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CreditScoreSummary(Base):
    __tablename__ = "credit_score_summaries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    
    # Credit score and rating
    credit_score = Column(Numeric(5, 2))  # 0-900 scale
    credit_rating = Column(String(10))  # AAA, AA, A, BBB, BB, High Risk
    
    # Component scores (out of 900 total)
    profitability_score = Column(Numeric(5, 2))  # Max 200 points
    liquidity_score = Column(Numeric(5, 2))  # Max 200 points
    leverage_score = Column(Numeric(5, 2))  # Max 200 points
    cash_flow_score = Column(Numeric(5, 2))  # Max 200 points
    growth_score = Column(Numeric(5, 2))  # Max 100 points
    
    # Repayment capacity
    repayment_capacity_ratio = Column(Numeric(5, 4))  # Net income / Total debt service
    loan_eligibility_status = Column(String(20))  # Eligible, Conditional, Not Eligible
    
    # Risk flags
    risk_flags = Column(JSON)  # Array of risk flag strings
    
    # Component details for transparency
    net_margin = Column(Numeric(5, 4))
    current_ratio = Column(Numeric(8, 4))
    quick_ratio = Column(Numeric(8, 4))
    debt_to_equity = Column(Numeric(8, 4))
    cash_flow_stability = Column(Numeric(5, 2))
    revenue_growth_rate = Column(Numeric(5, 4))
    
    # Recommendations
    improvement_recommendations = Column(JSON)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ForecastSummary(Base):
    __tablename__ = "forecast_summaries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Projection details
    projection_month = Column(String(7))  # YYYY-MM
    projected_revenue = Column(Numeric(15, 2))
    projected_expenses = Column(Numeric(15, 2))
    projected_net_income = Column(Numeric(15, 2))
    projected_cash_flow = Column(Numeric(15, 2))
    
    # Runway and confidence
    runway_months = Column(Numeric(5, 2))
    confidence_score = Column(Numeric(5, 2))  # 0-100
    
    # Forecast metadata
    forecast_type = Column(String(20))  # Base, Optimistic, Conservative
    months_used = Column(Integer)  # Number of historical months used
    revenue_growth_rate = Column(Numeric(5, 4))
    expense_growth_rate = Column(Numeric(5, 4))
    cash_flow_volatility = Column(Numeric(5, 4))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite index for company and month
    __table_args__ = (Index('idx_company_month', 'company_id', 'projection_month'),)

class IndustryBenchmarks(Base):
    __tablename__ = "industry_benchmarks_v2"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry_type = Column(String(50), nullable=False)  # Retail, Manufacturing, Services, etc.
    metric_name = Column(String(50), nullable=False)  # net_profit_margin, debt_to_equity, etc.
    industry_avg = Column(Numeric(8, 4))  # Industry average value
    top_quartile = Column(Numeric(8, 4))  # 75th percentile
    bottom_quartile = Column(Numeric(8, 4))  # 25th percentile
    percentile_distribution = Column(JSON)  # Array of percentile values
    sample_size = Column(Integer)  # Number of companies in dataset
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (UniqueConstraint('industry_type', 'metric_name', name='_industry_metric_uc_v2'),)

class BenchmarkSummary(Base):
    __tablename__ = "benchmark_summaries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    industry_type = Column(String(50))
    
    # Benchmark results for each metric
    net_profit_margin = Column(JSON)  # {value, industry_avg, percentile, status}
    gross_margin = Column(JSON)
    debt_to_equity = Column(JSON)
    current_ratio = Column(JSON)
    quick_ratio = Column(JSON)
    revenue_growth_rate = Column(JSON)
    operating_margin = Column(JSON)
    cash_conversion_cycle = Column(JSON)
    
    # Overall summary
    overall_percentile = Column(Numeric(5, 2))
    metrics_above_avg = Column(Integer)  # Count of metrics above industry average
    total_metrics = Column(Integer)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Report(Base):
    __tablename__ = "reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    report_type = Column(String(50))  # Full Report, Risk Only, Credit Only
    version_number = Column(Integer, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Scores and metrics
    health_score = Column(Numeric(5, 2))
    risk_score = Column(Numeric(5, 2))
    credit_score = Column(Numeric(5, 2))
    credit_rating = Column(String(10))
    
    # File paths
    file_path_pdf = Column(String(500))  # Path to generated PDF
    file_path_json = Column(String(500))  # Path to generated JSON
    
    # Report content
    executive_summary = Column(Text)
    kpis = Column(JSON)  # Key performance indicators
    risk_analysis = Column(JSON)
    credit_evaluation = Column(JSON)
    forecast_summary = Column(JSON)
    benchmark_comparison = Column(JSON)
    recommendations = Column(JSON)
    
    # Metadata
    processing_period = Column(String(7))  # YYYY-MM
    data_months_used = Column(Integer)
    
    __table_args__ = (Index('idx_company_report_version', 'company_id', 'version_number'),)

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50))  # CSV, XLSX, etc.
    file_path = Column(String(500))  # Encrypted storage path
    file_size = Column(Integer)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    processing_status = Column(String(20))  # Processed, Failed, Pending
    processing_error = Column(Text)
    linked_report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"))
    processing_period = Column(String(7))  # YYYY-MM
    
    # File metadata
    original_hash = Column(String(64))  # SHA-256 hash
    mime_type = Column(String(100))
    
    __table_args__ = (Index('idx_company_upload_date', 'company_id', 'upload_date'),)

class Integration(Base):
    __tablename__ = "integrations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    integration_type = Column(String(50))  # bank_api, gst_portal, tally, zoho, quickbooks
    provider_name = Column(String(100))  # Specific provider name
    is_active = Column(Boolean, default=False)
    api_endpoint = Column(String(500))
    encrypted_credentials = Column(Text)  # Encrypted API keys/tokens
    last_sync_at = Column(DateTime(timezone=True))
    sync_frequency = Column(String(20))  # daily, weekly, monthly
    configuration = Column(JSON)  # Additional config settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Notification preferences
    email_alerts = Column(JSON)  # {risk_changes, credit_alerts, reports, uploads}
    notification_frequency = Column(String(20))  # immediate, daily, weekly
    
    # UI preferences
    language = Column(String(10), default='en')
    timezone = Column(String(50), default='UTC')
    date_format = Column(String(20), default='YYYY-MM-DD')
    currency_display = Column(String(10), default='symbol')
    
    # Dashboard preferences
    default_dashboard_view = Column(String(20), default='overview')
    chart_preferences = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('user_id', 'company_id', name='_user_company_prefs_uc'),)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100))  # company_update, user_invite, integration_add, etc.
    resource_type = Column(String(50))  # company, user, integration, etc.
    resource_id = Column(String(100))
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (Index('idx_company_audit_date', 'company_id', 'created_at'), {'extend_existing': True})

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    generated_for_period = Column(String, nullable=False)
    horizon_months = Column(Integer, nullable=False, default=12)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
