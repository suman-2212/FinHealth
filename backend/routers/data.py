from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import tempfile
from pathlib import Path
import io
from database import get_db
from models import FinancialData, User, FinancialMetrics, RiskAssessment, CreditScore, Forecast
from schemas import FinancialDataCreate, FinancialDataResponse, FileUploadResponse
from auth import get_current_active_user
from utils.data_processor import DataProcessor
from utils.financial_calculator import FinancialCalculator
from utils.audit import log_audit
from deps import get_request_company_id

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_financial_data(
    request: Request,
    file: UploadFile = File(...),
    period: str = Form(...),
    data_type: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    print(f"[UPLOAD START] file={file.filename}, period={period}, data_type={data_type}")
    try:
        company_id = get_request_company_id(request)
        
        # Validate file type
        if file.content_type not in [
            "text/csv",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/pdf"
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Please upload CSV, XLSX, or PDF files."
            )
        
        # Read file content
        content = await file.read()
        
        # Securely save file to temporary storage
        upload_dir = Path("uploads") / str(company_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_id = str(uuid.uuid4())
        file_path = upload_dir / f"{file_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Process the file
        processor = DataProcessor()
        parsed_data, errors = processor.process_file(content, file.filename, file.content_type)
        
        if errors and not parsed_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File processing failed: {', '.join(errors)}"
            )
        
        # Initialize calculator for downstream calculations
        calculator = FinancialCalculator()
        
        # Create financial data record# Store the latest month's data in FinancialData (for compatibility)
        # Only include fields that exist in FinancialData model
        valid_fields = {
            'revenue', 'cost_of_goods_sold', 'salaries_wages', 'rent_expense',
            'marketing_expense', 'other_operating_expense', 'interest_expense',
            'tax_expense', 'depreciation_expense', 'other_income', 'gross_profit',
            'operating_income', 'net_income', 'cash_balance', 'accounts_receivable',
            'inventory', 'prepaid_expenses', 'total_current_assets', 'property_plant_equipment',
            'accumulated_depreciation', 'total_non_current_assets', 'total_assets',
            'accounts_payable', 'short_term_debt', 'accrued_expenses', 'total_current_liabilities',
            'long_term_debt', 'total_non_current_liabilities', 'total_liabilities',
            'common_stock', 'retained_earnings', 'total_equity', 'total_liabilities_equity'
        }
        latest_data = {k: v for k, v in parsed_data.items() if k in valid_fields}
        
        financial_data = FinancialData(
            company_id=company_id,
            period=period,
            data_type=data_type,
            **latest_data
        )
        
        db.add(financial_data)
        db.commit()
        db.refresh(financial_data)

        # Store monthly summaries for all months present in the file
        monthly_statements = parsed_data.get('monthly_statements', {})
        if monthly_statements:
            from models import MonthlySummary, RiskSummary
            for month, stmt in monthly_statements.items():
                # Compute metrics for this month
                metrics_dict = calculator.calculate_financial_metrics(stmt)
                health_score_dict = calculator.calculate_financial_health_score(metrics_dict)
                
                # Upsert monthly summary
                existing = db.query(MonthlySummary).filter(
                    MonthlySummary.company_id == company_id,
                    MonthlySummary.month == month
                ).first()
                if existing:
                    existing.revenue = stmt.get('revenue')
                    existing.operating_expense = stmt.get('other_operating_expense')
                    existing.interest_expense = stmt.get('interest_expense')
                    existing.tax_expense = stmt.get('tax_expense')
                    existing.net_income = stmt.get('net_income')
                    existing.total_assets = stmt.get('total_assets')
                    existing.current_assets = stmt.get('current_assets')
                    existing.current_liabilities = stmt.get('current_liabilities')
                    existing.equity = stmt.get('equity')
                    existing.operating_cash_flow = stmt.get('operating_cash_flow')
                    existing.gross_margin = metrics_dict.get('gross_profit_margin')
                    existing.net_margin = metrics_dict.get('net_profit_margin')
                    existing.current_ratio = metrics_dict.get('current_ratio')
                    existing.debt_to_equity = stmt.get('debt_to_equity')
                    existing.financial_health_score = health_score_dict.get('financial_health_score')
                    existing.statement_json = {k: v for k, v in stmt.items() if k != 'monthly_statements'}
                else:
                    db_month = MonthlySummary(
                        company_id=company_id,
                        month=month,
                        revenue=stmt.get('revenue'),
                        operating_expense=stmt.get('other_operating_expense'),
                        interest_expense=stmt.get('interest_expense'),
                        tax_expense=stmt.get('tax_expense'),
                        net_income=stmt.get('net_income'),
                        total_assets=stmt.get('total_assets'),
                        current_assets=stmt.get('current_assets'),
                        current_liabilities=stmt.get('current_liabilities'),
                        equity=stmt.get('equity'),
                        operating_cash_flow=stmt.get('operating_cash_flow'),
                        gross_margin=metrics_dict.get('gross_profit_margin'),
                        net_margin=metrics_dict.get('net_profit_margin'),
                        current_ratio=metrics_dict.get('current_ratio'),
                        debt_to_equity=stmt.get('debt_to_equity'),
                        financial_health_score=health_score_dict.get('financial_health_score'),
                        statement_json={k: v for k, v in stmt.items() if k != 'monthly_statements'}
                    )
                    db.add(db_month)
            
            # Atomically update RiskSummary with latest month's debt metrics
            latest_month = max(monthly_statements.keys())
            latest_stmt = monthly_statements[latest_month]
            existing_risk = db.query(RiskSummary).filter(RiskSummary.company_id == company_id).first()
            if existing_risk:
                existing_risk.debt_to_equity = latest_stmt.get('debt_to_equity')
                existing_risk.overall_risk_level = latest_stmt.get('risk_level')
                existing_risk.last_updated = func.now()
            else:
                risk_summary = RiskSummary(
                    company_id=company_id,
                    debt_to_equity=latest_stmt.get('debt_to_equity'),
                    overall_risk_level=latest_stmt.get('risk_level')
                )
                db.add(risk_summary)
            print(f"[RISK UPDATE] company_id={company_id} debt_to_equity={latest_stmt.get('debt_to_equity'):.2f} risk_level={latest_stmt.get('risk_level')}")
            db.commit()
            
            # Calculate and store comprehensive financial health
            from utils.financial_health_calculator import FinancialHealthCalculator
            from models import FinancialHealthSummary
            health_calc = FinancialHealthCalculator()
            health_data = health_calc.calculate_comprehensive_health(company_id, db)
            
            if health_data['health_score'] is not None:
                existing_health = db.query(FinancialHealthSummary).filter(
                    FinancialHealthSummary.company_id == company_id
                ).first()
                
                if existing_health:
                    existing_health.health_score = health_data['health_score']
                    existing_health.health_category = health_data['health_category']
                    existing_health.profitability_score = health_data['component_scores']['profitability']
                    existing_health.liquidity_score = health_data['component_scores']['liquidity']
                    existing_health.leverage_score = health_data['component_scores']['leverage']
                    existing_health.cash_flow_score = health_data['component_scores']['cash_flow']
                    existing_health.growth_score = health_data['component_scores']['growth']
                    existing_health.net_margin = health_data['component_details']['net_margin']
                    existing_health.current_ratio = health_data['component_details']['current_ratio']
                    existing_health.debt_to_equity = health_data['component_details']['debt_to_equity']
                    existing_health.cash_flow_stability = health_data['component_details']['cash_flow_stability']
                    existing_health.revenue_growth_rate = health_data['component_details']['revenue_growth_rate']
                    existing_health.improvement_recommendations = health_data['improvement_recommendations']
                    existing_health.last_updated = func.now()
                else:
                    health_summary = FinancialHealthSummary(
                        company_id=company_id,
                        health_score=health_data['health_score'],
                        health_category=health_data['health_category'],
                        profitability_score=health_data['component_scores']['profitability'],
                        liquidity_score=health_data['component_scores']['liquidity'],
                        leverage_score=health_data['component_scores']['leverage'],
                        cash_flow_score=health_data['component_scores']['cash_flow'],
                        growth_score=health_data['component_scores']['growth'],
                        net_margin=health_data['component_details']['net_margin'],
                        current_ratio=health_data['component_details']['current_ratio'],
                        debt_to_equity=health_data['component_details']['debt_to_equity'],
                        cash_flow_stability=health_data['component_details']['cash_flow_stability'],
                        revenue_growth_rate=health_data['component_details']['revenue_growth_rate'],
                        improvement_recommendations=health_data['improvement_recommendations']
                    )
                    db.add(health_summary)
                
                db.commit()
                print(f"[HEALTH UPDATE] company_id={company_id} health_score={health_data['health_score']:.2f} category={health_data['health_category']}")
            
            # Calculate and store comprehensive risk analysis
            from utils.risk_analyzer import RiskAnalyzer
            risk_analyzer = RiskAnalyzer()
            risk_data = risk_analyzer.analyze_comprehensive_risk(company_id, db)
            
            if risk_data['overall_risk_score'] is not None:
                existing_risk = db.query(RiskSummary).filter(
                    RiskSummary.company_id == company_id
                ).first()
                
                if existing_risk:
                    existing_risk.overall_risk_score = risk_data['overall_risk_score']
                    existing_risk.overall_risk_level = risk_data['overall_risk_level']
                    existing_risk.leverage_risk_score = risk_data['component_breakdown']['leverage']['score']
                    existing_risk.leverage_risk_level = risk_data['component_breakdown']['leverage']['level']
                    existing_risk.liquidity_risk_score = risk_data['component_breakdown']['liquidity']['score']
                    existing_risk.liquidity_risk_level = risk_data['component_breakdown']['liquidity']['level']
                    existing_risk.profitability_risk_score = risk_data['component_breakdown']['profitability']['score']
                    existing_risk.profitability_risk_level = risk_data['component_breakdown']['profitability']['level']
                    existing_risk.cash_flow_risk_score = risk_data['component_breakdown']['cash_flow']['score']
                    existing_risk.cash_flow_risk_level = risk_data['component_breakdown']['cash_flow']['level']
                    existing_risk.debt_to_equity = risk_data['component_breakdown']['leverage']['details'].get('debt_to_equity')
                    existing_risk.current_ratio = risk_data['component_breakdown']['liquidity']['details'].get('current_ratio')
                    existing_risk.quick_ratio = risk_data['component_breakdown']['liquidity']['details'].get('quick_ratio')
                    existing_risk.net_margin = risk_data['component_breakdown']['profitability']['details'].get('net_margin')
                    existing_risk.net_income = risk_data['component_breakdown']['profitability']['details'].get('net_income')
                    existing_risk.cash_flow_stability = risk_data['component_breakdown']['cash_flow']['details'].get('cash_flow_stability')
                    existing_risk.negative_cash_flow_months = risk_data['component_breakdown']['cash_flow']['details'].get('negative_cash_flow_months')
                    existing_risk.mitigation_actions = risk_data['mitigation_actions']
                    existing_risk.last_updated = func.now()
                else:
                    risk_summary = RiskSummary(
                        company_id=company_id,
                        overall_risk_score=risk_data['overall_risk_score'],
                        overall_risk_level=risk_data['overall_risk_level'],
                        leverage_risk_score=risk_data['component_breakdown']['leverage']['score'],
                        leverage_risk_level=risk_data['component_breakdown']['leverage']['level'],
                        liquidity_risk_score=risk_data['component_breakdown']['liquidity']['score'],
                        liquidity_risk_level=risk_data['component_breakdown']['liquidity']['level'],
                        profitability_risk_score=risk_data['component_breakdown']['profitability']['score'],
                        profitability_risk_level=risk_data['component_breakdown']['profitability']['level'],
                        cash_flow_risk_score=risk_data['component_breakdown']['cash_flow']['score'],
                        cash_flow_risk_level=risk_data['component_breakdown']['cash_flow']['level'],
                        debt_to_equity=risk_data['component_breakdown']['leverage']['details'].get('debt_to_equity'),
                        current_ratio=risk_data['component_breakdown']['liquidity']['details'].get('current_ratio'),
                        quick_ratio=risk_data['component_breakdown']['liquidity']['details'].get('quick_ratio'),
                        net_margin=risk_data['component_breakdown']['profitability']['details'].get('net_margin'),
                        net_income=risk_data['component_breakdown']['profitability']['details'].get('net_income'),
                        cash_flow_stability=risk_data['component_breakdown']['cash_flow']['details'].get('cash_flow_stability'),
                        negative_cash_flow_months=risk_data['component_breakdown']['cash_flow']['details'].get('negative_cash_flow_months'),
                        mitigation_actions=risk_data['mitigation_actions']
                    )
                    db.add(risk_summary)
                
                db.commit()
                print(f"[RISK ANALYSIS UPDATE] company_id={company_id} overall_risk={risk_data['overall_risk_score']:.2f} level={risk_data['overall_risk_level']}")
            
            # Calculate and store credit evaluation
            from utils.credit_scorer import CreditScorer
            from models import CreditScoreSummary
            credit_scorer = CreditScorer()
            credit_data = credit_scorer.calculate_credit_score(company_id, db)
            
            if credit_data['credit_score'] is not None:
                existing_credit = db.query(CreditScoreSummary).filter(
                    CreditScoreSummary.company_id == company_id
                ).first()
                
                if existing_credit:
                    existing_credit.credit_score = credit_data['credit_score']
                    existing_credit.credit_rating = credit_data['credit_rating']
                    existing_credit.profitability_score = credit_data['component_scores']['profitability']
                    existing_credit.liquidity_score = credit_data['component_scores']['liquidity']
                    existing_credit.leverage_score = credit_data['component_scores']['leverage']
                    existing_credit.cash_flow_score = credit_data['component_scores']['cash_flow']
                    existing_credit.growth_score = credit_data['component_scores']['growth']
                    existing_credit.repayment_capacity_ratio = credit_data['repayment_capacity_ratio']
                    existing_credit.loan_eligibility_status = credit_data['loan_eligibility_status']
                    existing_credit.risk_flags = credit_data['risk_flags']
                    existing_credit.net_margin = credit_data['component_details']['net_margin']
                    existing_credit.current_ratio = credit_data['component_details']['current_ratio']
                    existing_credit.quick_ratio = credit_data['component_details']['quick_ratio']
                    existing_credit.debt_to_equity = credit_data['component_details']['debt_to_equity']
                    existing_credit.cash_flow_stability = credit_data['component_details']['cash_flow_stability']
                    existing_credit.revenue_growth_rate = credit_data['component_details']['revenue_growth_rate']
                    existing_credit.improvement_recommendations = credit_data['improvement_recommendations']
                    existing_credit.last_updated = func.now()
                else:
                    credit_summary = CreditScoreSummary(
                        company_id=company_id,
                        credit_score=credit_data['credit_score'],
                        credit_rating=credit_data['credit_rating'],
                        profitability_score=credit_data['component_scores']['profitability'],
                        liquidity_score=credit_data['component_scores']['liquidity'],
                        leverage_score=credit_data['component_scores']['leverage'],
                        cash_flow_score=credit_data['component_scores']['cash_flow'],
                        growth_score=credit_data['component_scores']['growth'],
                        repayment_capacity_ratio=credit_data['repayment_capacity_ratio'],
                        loan_eligibility_status=credit_data['loan_eligibility_status'],
                        risk_flags=credit_data['risk_flags'],
                        net_margin=credit_data['component_details']['net_margin'],
                        current_ratio=credit_data['component_details']['current_ratio'],
                        quick_ratio=credit_data['component_details']['quick_ratio'],
                        debt_to_equity=credit_data['component_details']['debt_to_equity'],
                        cash_flow_stability=credit_data['component_details']['cash_flow_stability'],
                        revenue_growth_rate=credit_data['component_details']['revenue_growth_rate'],
                        improvement_recommendations=credit_data['improvement_recommendations']
                    )
                    db.add(credit_summary)
                
                db.commit()
                print(f"[CREDIT EVALUATION UPDATE] company_id={company_id} credit_score={credit_data['credit_score']:.2f} rating={credit_data['credit_rating']}")
            
            # Generate financial forecasts
            from utils.financial_forecaster import FinancialForecaster
            from models import ForecastSummary
            forecaster = FinancialForecaster()
            
            # Generate base forecast for 6 months
            forecast_data = forecaster.generate_forecast(company_id, db, months_ahead=6, forecast_type='Base')
            
            if forecast_data['projections']:
                print(f"[FORECAST UPDATE] company_id={company_id} months={len(forecast_data['projections'])} confidence={forecast_data['confidence_score']:.2f}")
            
        # Store uploaded document record (outside the if block)
        from models import UploadedDocument
        import hashlib
        
        # Calculate file hash
        file_hash = hashlib.sha256()
        for chunk in iter(lambda: file.file.read(4096), b""):
            file_hash.update(chunk)
        file.file.seek(0)  # Reset file pointer
        
        # Create document record
        document = UploadedDocument(
            company_id=company_id,
            file_name=file.filename,
            file_type=file.content_type.split('/')[-1] if file.content_type else 'unknown',
            file_path=str(file_path),  # Convert Path to string
            file_size=file.size,
            processing_status='Processed',
            processing_period=period,
            original_hash=file_hash.hexdigest(),
            mime_type=file.content_type
        )
        db.add(document)
        db.flush()  # Get the document ID
        
        # Generate comprehensive report after successful processing
        from utils.report_generator import ReportGenerator
        from models import Report
        
        if monthly_statements:
            try:
                generator = ReportGenerator()
                report_data = generator.generate_report(company_id, db, "Full Report")
                
                if report_data.get("report_id"):
                    # Link document to report
                    document.linked_report_id = report_data["report_id"]
                    print(f"[REPORT GENERATED] company_id={company_id} report_id={report_data['report_id']} version={report_data['version_number']}")
            except Exception as e:
                print(f"[REPORT GENERATION ERROR] company_id={company_id} error={str(e)}")
                # Don't fail the upload if report generation fails

        # Trigger downstream calculations
        try:
            calculator = FinancialCalculator()
            # 1) Calculate and store metrics
            metrics_dict = calculator.calculate_financial_metrics(parsed_data)
            existing_metrics = db.query(FinancialMetrics).filter(
                FinancialMetrics.company_id == company_id,
                FinancialMetrics.period == period
            ).first()
            if existing_metrics:
                for k, v in metrics_dict.items():
                    setattr(existing_metrics, k, v)
                db_metrics = existing_metrics
            else:
                db_metrics = FinancialMetrics(company_id=company_id, period=period, **metrics_dict)
                db.add(db_metrics)
            db.commit()

            # 2) Risk assessment
            risk_dict = calculator.assess_financial_risks(metrics_dict, parsed_data, industry='')
            existing_risk = db.query(RiskAssessment).filter(
                RiskAssessment.company_id == company_id,
                RiskAssessment.period == period
            ).first()
            if existing_risk:
                for k, v in risk_dict.items():
                    if k not in ('risk_factors', 'recommendations'):
                        setattr(existing_risk, k, v)
                existing_risk.risk_factors = risk_dict.get('risk_factors', {})
                existing_risk.recommendations = risk_dict.get('recommendations', [])
                db_risk = existing_risk
            else:
                db_risk = RiskAssessment(company_id=company_id, period=period, **risk_dict)
                db.add(db_risk)
            db.commit()

            # 3) Credit score
            credit_dict = calculator.calculate_credit_score(metrics_dict, risk_dict, industry='')
            existing_credit = db.query(CreditScore).filter(
                CreditScore.company_id == company_id,
                CreditScore.period == period
            ).first()
            if existing_credit:
                for k, v in credit_dict.items():
                    setattr(existing_credit, k, v)
                db_credit = existing_credit
            else:
                db_credit = CreditScore(company_id=company_id, period=period, **credit_dict)
                db.add(db_credit)
            db.commit()

            # 4) Financial health score
            health_score_dict = calculator.calculate_financial_health_score(metrics_dict)
            # Store in a summary table or include in metrics for now
            # For simplicity, attach to metrics_dict as a field
            metrics_dict['financial_health_score'] = health_score_dict['financial_health_score']
            metrics_dict['health_grade'] = health_score_dict['grade']

            # 5) Simple forecast (6/12 month moving average)
            forecast_dict = calculator.generate_forecast([parsed_data], months=12)
            existing_forecast = db.query(Forecast).filter(
                Forecast.company_id == company_id,
                Forecast.generated_for_period == period
            ).first()
            if existing_forecast:
                existing_forecast.payload = forecast_dict
                db_forecast = existing_forecast
            else:
                db_forecast = Forecast(
                    company_id=company_id,
                    generated_for_period=period,
                    horizon_months=12,
                    payload=forecast_dict
                )
                db.add(db_forecast)
            db.commit()

            # 5) Audit log
            log_audit(
                db=db,
                user_id=current_user.id,
                company_id=company_id,
                action="data_uploaded",
                resource_type="financial_data",
                resource_id=str(financial_data.id),
                new_values={"file_name": file.filename, "period": period},
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
        except Exception as calc_err:
            # Log calculation errors but do not fail upload
            print(f"Calculation pipeline error: {calc_err}")
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=len(content),
            upload_status="success",
            parsed_data={k: v for k, v in parsed_data.items() if k != 'monthly_statements'},  # Exclude circular ref
            errors=errors if errors else None,
            metrics_generated=True,
            period=period
        )
        
    except Exception as e:
        import traceback
        print(f"[UPLOAD ERROR] {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/uploads")
async def list_uploads(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    upload_dir = Path("uploads") / str(company_id)
    if not upload_dir.exists():
        return []
    files = []
    for file_path in upload_dir.glob("*"):
        if file_path.is_file():
            # Extract file_id and original filename
            parts = file_path.name.split("_", 1)
            file_id = parts[0] if parts else ""
            filename = parts[1] if len(parts) > 1 else file_path.name
            files.append({
                "file_id": file_id,
                "filename": filename,
                "size": file_path.stat().st_size,
                "uploaded_at": file_path.stat().st_ctime
            })
    return sorted(files, key=lambda x: x["uploaded_at"], reverse=True)

@router.get("/uploads/{file_id}/download")
async def download_upload(
    file_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    upload_dir = Path("uploads") / str(company_id)
    # Find file by prefix
    for file_path in upload_dir.glob(f"{file_id}_*"):
        if file_path.is_file():
            from fastapi.responses import FileResponse
            return FileResponse(file_path, filename=file_path.name.split("_", 1)[1])
    raise HTTPException(status_code=404, detail="File not found")

@router.get("/list", response_model=List[FinancialDataResponse])
async def list_financial_data(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    
    # Get financial data
    financial_data = db.query(FinancialData).filter(
        FinancialData.company_id == company_id
    ).order_by(FinancialData.upload_date.desc()).all()
    
    return financial_data

@router.get("/{data_id}", response_model=FinancialDataResponse)
async def get_financial_data(
    request: Request,
    data_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        # Convert string to UUID
        from uuid import UUID
        data_uuid = UUID(data_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data ID format"
        )
    
    company_id = get_request_company_id(request)
    financial_data = db.query(FinancialData).filter(
        FinancialData.id == data_uuid,
        FinancialData.company_id == company_id
    ).first()
    
    if not financial_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial data not found"
        )
    
    return financial_data

@router.post("/manual", response_model=FinancialDataResponse)
async def create_financial_data_manual(
    request: Request,
    financial_data: FinancialDataCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_id = get_request_company_id(request)
    
    # Create financial data record
    db_financial_data = FinancialData(
        company_id=company_id,
        **financial_data.dict()
    )
    
    db.add(db_financial_data)
    db.commit()
    db.refresh(db_financial_data)
    
    return db_financial_data
