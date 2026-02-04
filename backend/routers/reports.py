from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from starlette.requests import Request
from fastapi.responses import FileResponse
from models import Report, UploadedDocument
from database import get_db
from deps import get_request_company_id
from auth import get_current_active_user
from models import User
from utils.report_generator import ReportGenerator
from typing import List, Optional
import os
from pathlib import Path
import uuid

router = APIRouter()

@router.get("/reports")
async def get_reports(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all reports for the current tenant's company"""
    
    company_id = get_request_company_id(request)
    
    reports = db.query(Report).filter(
        Report.company_id == company_id
    ).order_by(Report.version_number.desc()).all()
    
    report_list = []
    for report in reports:
        report_list.append({
            "report_id": str(report.id),
            "version_number": report.version_number,
            "report_type": report.report_type,
            "generated_at": report.generated_at.isoformat(),
            "processing_period": report.processing_period,
            "health_score": float(report.health_score) if report.health_score else None,
            "risk_score": float(report.risk_score) if report.risk_score else None,
            "credit_score": float(report.credit_score) if report.credit_score else None,
            "credit_rating": report.credit_rating,
            "file_paths": {
                "pdf": report.file_path_pdf,
                "json": report.file_path_json
            }
        })
    
    return {"reports": report_list}

@router.post("/reports/generate")
async def generate_report(
    request: Request,
    report_type: str = "Full Report",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a new report"""
    
    company_id = get_request_company_id(request)
    
    # Validate report type
    valid_types = ["Full Report", "Risk Only", "Credit Only"]
    if report_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report type. Must be one of: {', '.join(valid_types)}"
        )
    
    generator = ReportGenerator()
    report_data = generator.generate_report(company_id, db, report_type)
    
    if not report_data.get("report_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No financial data available for report generation"
        )
    
    return report_data

@router.get("/reports/{report_id}/download/{file_type}")
async def download_report(
    report_id: str,
    file_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download a report file (PDF or JSON)"""
    
    # Validate file type
    if file_type not in ["pdf", "json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Must be 'pdf' or 'json'"
        )
    
    # Convert string to UUID
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID format"
        )
    
    # Get report
    report = db.query(Report).filter(Report.id == report_uuid).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Get file path
    if file_type == "pdf":
        file_path = report.file_path_pdf
        filename = f"report_{report.version_number}.pdf"
    else:
        file_path = report.file_path_json
        filename = f"report_{report.version_number}.json"
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    # Return file
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf" if file_type == "pdf" else "application/json"
    )

@router.get("/documents")
async def get_documents(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all uploaded documents for the current tenant's company"""
    
    company_id = get_request_company_id(request)
    
    documents = db.query(UploadedDocument).filter(
        UploadedDocument.company_id == company_id
    ).order_by(UploadedDocument.upload_date.desc()).all()
    
    document_list = []
    for doc in documents:
        document_list.append({
            "document_id": str(doc.id),
            "file_name": doc.file_name,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "upload_date": doc.upload_date.isoformat(),
            "processing_status": doc.processing_status,
            "processing_error": doc.processing_error,
            "processing_period": doc.processing_period,
            "linked_report_id": str(doc.linked_report_id) if doc.linked_report_id else None
        })
    
    return {"documents": document_list}

@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download an uploaded document"""
    
    # Convert string to UUID
    try:
        document_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format"
        )
    
    # Get document
    document = db.query(UploadedDocument).filter(UploadedDocument.id == document_uuid).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not document.file_path or not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found"
        )
    
    # Return file
    return FileResponse(
        path=document.file_path,
        filename=document.file_name,
        media_type=document.mime_type or "application/octet-stream"
    )
