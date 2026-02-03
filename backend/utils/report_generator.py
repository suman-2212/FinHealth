import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
from pathlib import Path
import uuid

# PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart

from models import (
    MonthlySummary, FinancialHealthSummary, RiskSummary, 
    CreditScoreSummary, ForecastSummary, BenchmarkSummary,
    Report, UploadedDocument
)

class ReportGenerator:
    """Comprehensive report generation engine"""
    
    def __init__(self, storage_path: str = "reports"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
    def generate_report(self, company_id: str, db: Session, 
                        report_type: str = "Full Report") -> Dict[str, Any]:
        """Generate comprehensive financial report"""
        
        print(f"[REPORT GENERATOR] company_id={company_id} report_type={report_type}")
        
        # Get latest financial data
        latest_summary = db.query(MonthlySummary).filter(
            MonthlySummary.company_id == company_id
        ).order_by(MonthlySummary.month.desc()).first()
        
        if not latest_summary:
            print(f"[REPORT GENERATOR] No monthly summary found for company_id={company_id}")
            return self._empty_report_response()
        
        print(f"[REPORT GENERATOR] Found monthly summary for month={latest_summary.month}")
        
        # Get analysis data
        health_summary = db.query(FinancialHealthSummary).filter(
            FinancialHealthSummary.company_id == company_id
        ).first()
        
        print(f"[REPORT GENERATOR] Health summary found: {health_summary is not None}")
        if health_summary:
            print(f"[REPORT GENERATOR] Health score: {health_summary.health_score}")
        
        risk_summary = db.query(RiskSummary).filter(
            RiskSummary.company_id == company_id
        ).first()
        
        print(f"[REPORT GENERATOR] Risk summary found: {risk_summary is not None}")
        if risk_summary:
            print(f"[REPORT GENERATOR] Risk score: {risk_summary.overall_risk_score}")
        
        credit_summary = db.query(CreditScoreSummary).filter(
            CreditScoreSummary.company_id == company_id
        ).first()
        
        print(f"[REPORT GENERATOR] Credit summary found: {credit_summary is not None}")
        if credit_summary:
            print(f"[REPORT GENERATOR] Credit score: {credit_summary.credit_score}")
        
        forecast_data = db.query(ForecastSummary).filter(
            ForecastSummary.company_id == company_id,
            ForecastSummary.forecast_type == "Base"
        ).order_by(ForecastSummary.projection_month).limit(6).all()
        
        benchmark_summary = db.query(BenchmarkSummary).filter(
            BenchmarkSummary.company_id == company_id
        ).first()
        
        # Get next version number
        latest_report = db.query(Report).filter(
            Report.company_id == company_id
        ).order_by(Report.version_number.desc()).first()
        next_version = (latest_report.version_number + 1) if latest_report else 1
        
        # Compile report data
        report_data = {
            "company_id": company_id,
            "report_type": report_type,
            "version_number": next_version,
            "generated_at": datetime.utcnow().isoformat(),
            "processing_period": latest_summary.month,
            "executive_summary": self._generate_executive_summary(
                latest_summary, health_summary, risk_summary, credit_summary
            ),
            "kpis": self._extract_kpis(latest_summary),
            "health_analysis": self._extract_health_data(health_summary),
            "risk_analysis": self._extract_risk_data(risk_summary),
            "credit_evaluation": self._extract_credit_data(credit_summary),
            "forecast_summary": self._extract_forecast_data(forecast_data),
            "benchmark_comparison": self._extract_benchmark_data(benchmark_summary),
            "recommendations": self._generate_recommendations(
                health_summary, risk_summary, credit_summary
            )
        }
        
        # Generate files
        pdf_path = self._generate_pdf_report(report_data)
        json_path = self._generate_json_report(report_data)
        
        # Store in database
        report = Report(
            company_id=company_id,
            report_type=report_type,
            version_number=next_version,
            health_score=float(health_summary.health_score) if health_summary else None,
            risk_score=float(risk_summary.overall_risk_score) if risk_summary else None,
            credit_score=float(credit_summary.credit_score) if credit_summary else None,
            credit_rating=credit_summary.credit_rating if credit_summary else None,
            file_path_pdf=str(pdf_path),
            file_path_json=str(json_path),
            executive_summary=report_data["executive_summary"],
            kpis=report_data["kpis"],
            risk_analysis=report_data["risk_analysis"],
            credit_evaluation=report_data["credit_evaluation"],
            forecast_summary=report_data["forecast_summary"],
            benchmark_comparison=report_data["benchmark_comparison"],
            recommendations=report_data["recommendations"],
            processing_period=latest_summary.month,
            data_months_used=db.query(MonthlySummary).filter(
                MonthlySummary.company_id == company_id
            ).count()
        )
        
        db.add(report)
        db.commit()
        
        return {
            "report_id": str(report.id),
            "version_number": next_version,
            "generated_at": report.generated_at.isoformat(),
            "file_paths": {
                "pdf": str(pdf_path),
                "json": str(json_path)
            },
            "scores": {
                "health": report.health_score,
                "risk": report.risk_score,
                "credit": report.credit_score,
                "credit_rating": report.credit_rating
            }
        }
    
    def _generate_executive_summary(self, latest: MonthlySummary, 
                                   health: FinancialHealthSummary,
                                   risk: RiskSummary,
                                   credit: CreditScoreSummary) -> str:
        """Generate AI-like executive summary"""
        
        summary_parts = []
        
        # Overall performance
        if health:
            health_score = float(health.health_score)
            if health_score >= 80:
                summary_parts.append("The company demonstrates excellent financial health with strong operational efficiency and solid profitability metrics.")
            elif health_score >= 60:
                summary_parts.append("The company shows good financial health with room for improvement in operational efficiency.")
            elif health_score >= 40:
                summary_parts.append("The company faces moderate financial challenges requiring immediate attention to improve operational performance.")
            else:
                summary_parts.append("The company is experiencing significant financial distress requiring urgent intervention.")
        
        # Risk assessment
        if risk:
            risk_score = float(risk.overall_risk_score)
            if risk_score <= 30:
                summary_parts.append("Risk levels are well-controlled with strong financial stability.")
            elif risk_score <= 60:
                summary_parts.append("Moderate risk levels exist that should be monitored closely.")
            else:
                summary_parts.append("High risk levels require immediate mitigation strategies.")
        
        # Credit position
        if credit:
            credit_score = float(credit.credit_score)
            if credit_score >= 700:
                summary_parts.append("Credit position is strong with excellent loan eligibility.")
            elif credit_score >= 600:
                summary_parts.append("Credit position is moderate with reasonable loan eligibility.")
            else:
                summary_parts.append("Credit position requires improvement to enhance loan eligibility.")
        
        # Financial highlights
        if latest:
            revenue = float(latest.revenue or 0)
            net_income = float(latest.net_income or 0)
            if revenue > 0:
                margin = (net_income / revenue) * 100
                summary_parts.append(f"Current period shows revenue of ${revenue:,.0f} with net margin of {margin:.1f}%.")
        
        return " ".join(summary_parts)
    
    def _extract_kpis(self, latest: MonthlySummary) -> Dict[str, Any]:
        """Extract key performance indicators"""
        return {
            "revenue": float(latest.revenue or 0),
            "net_income": float(latest.net_income or 0),
            "total_assets": float(latest.total_assets or 0),
            "current_ratio": float(latest.current_ratio or 0),
            "debt_to_equity": float(latest.debt_to_equity or 0),
            "net_margin": float(latest.net_margin or 0),
            "gross_margin": float(latest.gross_margin or 0),
            "operating_cash_flow": float(latest.operating_cash_flow or 0)
        }
    
    def _extract_health_data(self, health: FinancialHealthSummary) -> Optional[Dict]:
        """Extract financial health data"""
        if not health:
            return None
        
        return {
            "health_score": float(health.health_score),
            "category": health.health_category,  # Fixed: use health_category instead of category
            "component_scores": {
                "profitability": float(health.profitability_score) if health.profitability_score else None,
                "liquidity": float(health.liquidity_score) if health.liquidity_score else None,
                "leverage": float(health.leverage_score) if health.leverage_score else None,
                "cash_flow": float(health.cash_flow_score) if health.cash_flow_score else None,
                "growth": float(health.growth_score) if health.growth_score else None
            },
            "improvement_recommendations": health.improvement_recommendations
        }
    
    def _extract_risk_data(self, risk: RiskSummary) -> Optional[Dict]:
        """Extract risk analysis data"""
        if not risk:
            return None
        
        return {
            "overall_risk_score": float(risk.overall_risk_score),
            "risk_level": risk.overall_risk_level,
            "component_risks": {
                "leverage": {
                    "score": float(risk.leverage_risk_score) if risk.leverage_risk_score else None,
                    "level": risk.leverage_risk_level
                },
                "liquidity": {
                    "score": float(risk.liquidity_risk_score) if risk.liquidity_risk_score else None,
                    "level": risk.liquidity_risk_level
                },
                "profitability": {
                    "score": float(risk.profitability_risk_score) if risk.profitability_risk_score else None,
                    "level": risk.profitability_risk_level
                },
                "cash_flow": {
                    "score": float(risk.cash_flow_risk_score) if risk.cash_flow_risk_score else None,
                    "level": risk.cash_flow_risk_level
                }
            },
            "risk_flags": [],  # Empty array since model doesn't have this field
            "mitigation_actions": risk.mitigation_actions or []
        }
    
    def _extract_credit_data(self, credit: CreditScoreSummary) -> Optional[Dict]:
        """Extract credit evaluation data"""
        if not credit:
            return None
        
        return {
            "credit_score": float(credit.credit_score),
            "credit_rating": credit.credit_rating,
            "component_scores": {
                "profitability": float(credit.profitability_score) if credit.profitability_score else None,
                "liquidity": float(credit.liquidity_score) if credit.liquidity_score else None,
                "leverage": float(credit.leverage_score) if credit.leverage_score else None,
                "cash_flow": float(credit.cash_flow_score) if credit.cash_flow_score else None,
                "growth": float(credit.growth_score) if credit.growth_score else None
            },
            "repayment_capacity": float(credit.repayment_capacity_ratio) if credit.repayment_capacity_ratio else None,
            "loan_eligibility": credit.loan_eligibility_status,
            "risk_flags": credit.risk_flags or [],
            "improvement_recommendations": credit.improvement_recommendations or []
        }
    
    def _extract_forecast_data(self, forecasts: List) -> Dict:
        """Extract forecast data"""
        if not forecasts:
            return {"projections": [], "confidence": None}
        
        projections = []
        for forecast in forecasts:
            projections.append({
                "month": forecast.projection_month,
                "revenue": float(forecast.projected_revenue),
                "expenses": float(forecast.projected_expenses),
                "net_income": float(forecast.projected_net_income),
                "cash_flow": float(forecast.projected_cash_flow)
            })
        
        return {
            "projections": projections,
            "confidence": float(forecasts[0].confidence_score) if forecasts else None
        }
    
    def _extract_benchmark_data(self, benchmark: BenchmarkSummary) -> Optional[Dict]:
        """Extract benchmark comparison data"""
        if not benchmark:
            return None
        
        return {
            "industry_type": benchmark.industry_type,
            "overall_percentile": float(benchmark.overall_percentile) if benchmark.overall_percentile else None,
            "metrics_above_avg": benchmark.metrics_above_avg,
            "total_metrics": benchmark.total_metrics,
            "comparisons": {
                "net_profit_margin": benchmark.net_profit_margin,
                "current_ratio": benchmark.current_ratio,
                "debt_to_equity": benchmark.debt_to_equity,
                "revenue_growth_rate": benchmark.revenue_growth_rate
            }
        }
    
    def _generate_recommendations(self, health: FinancialHealthSummary,
                                 risk: RiskSummary,
                                 credit: CreditScoreSummary) -> List[str]:
        """Generate consolidated recommendations"""
        recommendations = []
        
        if health and health.improvement_recommendations:
            recommendations.extend(health.improvement_recommendations)
        
        if risk and risk.mitigation_actions:
            recommendations.extend(risk.mitigation_actions)
        
        if credit and credit.improvement_recommendations:
            recommendations.extend(credit.improvement_recommendations)
        
        # Remove duplicates and return
        return list(dict.fromkeys(recommendations))
    
    def _generate_pdf_report(self, report_data: Dict) -> Path:
        """Generate PDF report"""
        filename = f"report_{report_data['company_id']}_{report_data['version_number']}.pdf"
        pdf_path = self.storage_path / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("Financial Health Report", title_style))
        
        # Report metadata
        metadata_style = ParagraphStyle(
            'CustomMetadata',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=20
        )
        story.append(Paragraph(f"Version: {report_data['version_number']}", metadata_style))
        story.append(Paragraph(f"Generated: {report_data['generated_at']}", metadata_style))
        story.append(Paragraph(f"Period: {report_data['processing_period']}", metadata_style))
        
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Paragraph(report_data['executive_summary'], styles['Normal']))
        story.append(Spacer(1, 20))
        
        # KPIs Table
        story.append(Paragraph("Key Performance Indicators", styles['Heading2']))
        kpis = report_data['kpis']
        kpi_data = [
            ['Metric', 'Value'],
            ['Revenue', f"${kpis['revenue']:,.0f}"],
            ['Net Income', f"${kpis['net_income']:,.0f}"],
            ['Net Margin', f"{kpis['net_margin']*100:.1f}%"],
            ['Current Ratio', f"{kpis['current_ratio']:.2f}"],
            ['Debt-to-Equity', f"{kpis['debt_to_equity']:.2f}"]
        ]
        
        kpi_table = Table(kpi_data)
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 20))
        
        # Scores
        story.append(Paragraph("Performance Scores", styles['Heading2']))
        scores_data = [
            ['Metric', 'Score', 'Rating'],
            ['Health Score', f"{report_data['scores']['health']:.1f}" if report_data.get('scores', {}).get('health') else 'N/A', ''],
            ['Risk Score', f"{report_data['scores']['risk']:.1f}" if report_data.get('scores', {}).get('risk') else 'N/A', ''],
            ['Credit Score', f"{report_data['scores']['credit']:.0f}" if report_data.get('scores', {}).get('credit') else 'N/A', report_data.get('scores', {}).get('credit_rating', 'N/A')]
        ]
        
        scores_table = Table(scores_data)
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(scores_table)
        
        # Build PDF
        doc.build(story)
        
        return pdf_path
    
    def _generate_json_report(self, report_data: Dict) -> Path:
        """Generate JSON report"""
        filename = f"report_{report_data['company_id']}_{report_data['version_number']}.json"
        json_path = self.storage_path / filename
        
        with open(json_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return json_path
    
    def _empty_report_response(self) -> Dict[str, Any]:
        """Return empty response when no data available"""
        return {
            "report_id": None,
            "version_number": 0,
            "generated_at": None,
            "file_paths": {},
            "scores": {},
            "error": "No financial data available for report generation"
        }
