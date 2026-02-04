from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Company, User, UserCompany, AuditLog
from schemas import CompanyCreate, CompanyResponse
from auth import get_current_active_user
from utils.audit import log_audit
from pydantic import BaseModel
import uuid

router = APIRouter()


class CompanySwitchRequest(BaseModel):
    company_id: uuid.UUID

@router.post("/create", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if company with registration number already exists
    if company.registration_number:
        existing_company = db.query(Company).filter(
            Company.registration_number == company.registration_number
        ).first()
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this registration number already exists"
            )
    
    # Create new company
    db_company = Company(
        name=company.name,
        industry=company.industry,
        registration_number=company.registration_number,
    )
    
    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    existing_links = db.query(UserCompany).filter(UserCompany.user_id == current_user.id).count()
    link = UserCompany(
        user_id=current_user.id,
        company_id=db_company.id,
        role="owner",
        is_default=(existing_links == 0),
    )
    db.add(link)

    log_audit(
        db=db,
        user_id=current_user.id,
        company_id=db_company.id,
        action="company_created",
        resource_type="company",
        resource_id=str(db_company.id),
        new_values={"name": company.name, "industry": company.industry},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    db.commit()
    
    return db_company

@router.get("/", response_model=List[CompanyResponse])
async def get_user_companies(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    company_ids = [
        link.company_id
        for link in db.query(UserCompany).filter(UserCompany.user_id == current_user.id).all()
    ]
    if not company_ids:
        return []
    return db.query(Company).filter(Company.id.in_(company_ids)).all()

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        company_uuid = uuid.UUID(company_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid company id")

    link = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_uuid,
    ).first()
    if not link:
        company = None
    else:
        company = db.query(Company).filter(Company.id == company_uuid).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.post("/switch")
async def switch_company(
    payload: CompanySwitchRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    link = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == payload.company_id,
    ).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this company")

    db.query(UserCompany).filter(UserCompany.user_id == current_user.id).update({"is_default": False})
    link.is_default = True

    log_audit(
        db=db,
        user_id=current_user.id,
        company_id=payload.company_id,
        action="company_switched",
        resource_type="company",
        resource_id=str(payload.company_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    db.commit()
    return {"default_company_id": str(payload.company_id)}

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company_update: CompanyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        company_uuid = uuid.UUID(company_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid company id")

    link = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_uuid,
    ).first()
    company = db.query(Company).filter(Company.id == company_uuid).first() if link else None
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update company details
    company.name = company_update.name
    company.industry = company_update.industry
    company.registration_number = company_update.registration_number
    
    db.commit()
    db.refresh(company)
    
    return company
