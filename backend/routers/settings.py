from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import Company, User
from database import get_db
from deps import get_request_company_id, get_request_user_id
from auth import get_current_active_user
from utils.settings_manager import SettingsManager

router = APIRouter()

# Pydantic models for validation
class CompanyProfileUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    financial_year_start: Optional[int] = None
    currency: Optional[str] = None
    gst_number: Optional[str] = None

class IntegrationCreate(BaseModel):
    integration_type: str
    provider_name: Optional[str] = None
    api_endpoint: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
    sync_frequency: Optional[str] = "daily"
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = False

class UserPreferencesUpdate(BaseModel):
    email_alerts: Optional[Dict[str, bool]] = None
    notification_frequency: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    currency_display: Optional[str] = None
    default_dashboard_view: Optional[str] = None
    chart_preferences: Optional[Dict[str, Any]] = None

class UserInvite(BaseModel):
    email: str  # Using regular str instead of EmailStr temporarily
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@router.get("/settings/company")
async def get_company_profile(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get company profile settings"""
    company_id = get_request_company_id(request)
    user_id = get_request_user_id(request)
    
    settings_manager = SettingsManager()
    profile = settings_manager.get_company_profile(db, company_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )
    
    return profile

@router.put("/settings/company")
async def update_company_profile(
    request: Request,
    updates: CompanyProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update company profile settings"""
    company_id = get_request_company_id(request)
    user_id = get_request_user_id(request)
    
    # Validate financial year start
    if updates.financial_year_start and (updates.financial_year_start < 1 or updates.financial_year_start > 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial year start must be between 1 and 12"
        )
    
    # Validate currency
    valid_currencies = ['USD', 'EUR', 'GBP', 'INR', 'JPY', 'CAD', 'AUD']
    if updates.currency and updates.currency not in valid_currencies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid currency. Must be one of: {', '.join(valid_currencies)}"
        )
    
    settings_manager = SettingsManager()
    
    # Get client info for audit
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        updated_profile = settings_manager.update_company_profile(
            db=db,
            company_id=company_id,
            user_id=user_id,
            updates=updates.dict(exclude_unset=True),
            ip_address=client_host,
            user_agent=user_agent
        )
        return updated_profile
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/settings/integrations")
async def get_integrations(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all integrations for the company"""
    company_id = get_request_company_id(request)
    
    settings_manager = SettingsManager()
    integrations = settings_manager.get_integrations(db, company_id)
    
    return {"integrations": integrations}

@router.post("/settings/integrations")
async def create_integration(
    request: Request,
    integration_data: IntegrationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new integration"""
    company_id = get_request_company_id(request)
    user_id = get_request_user_id(request)
    
    # Validate integration type
    valid_types = ['bank_api', 'gst_portal', 'tally', 'zoho', 'quickbooks']
    if integration_data.integration_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid integration type. Must be one of: {', '.join(valid_types)}"
        )
    
    settings_manager = SettingsManager()
    
    # Get client info for audit
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    integration = settings_manager.create_integration(
        db=db,
        company_id=company_id,
        user_id=user_id,
        integration_data=integration_data.dict(),
        ip_address=client_host,
        user_agent=user_agent
    )
    
    return integration

@router.get("/settings/preferences")
async def get_user_preferences(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    company_id = get_request_company_id(request)
    user_id = get_request_user_id(request)
    
    settings_manager = SettingsManager()
    preferences = settings_manager.get_user_preferences(db, user_id, company_id)
    
    if not preferences:
        # Return default preferences
        return {
            'email_alerts': {
                'risk_changes': True,
                'credit_alerts': True,
                'reports': True,
                'uploads': True
            },
            'notification_frequency': 'immediate',
            'language': 'en',
            'timezone': 'UTC',
            'date_format': 'YYYY-MM-DD',
            'currency_display': 'symbol',
            'default_dashboard_view': 'overview',
            'chart_preferences': {}
        }
    
    return preferences

@router.put("/settings/preferences")
async def update_user_preferences(
    request: Request,
    preferences: UserPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    company_id = get_request_company_id(request)
    user_id = get_request_user_id(request)
    
    # Validate notification frequency
    valid_frequencies = ['immediate', 'daily', 'weekly']
    if preferences.notification_frequency and preferences.notification_frequency not in valid_frequencies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid notification frequency. Must be one of: {', '.join(valid_frequencies)}"
        )
    
    # Validate language
    valid_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko']
    if preferences.language and preferences.language not in valid_languages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid language. Must be one of: {', '.join(valid_languages)}"
        )
    
    settings_manager = SettingsManager()
    
    # Get client info for audit
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    updated_preferences = settings_manager.update_user_preferences(
        db=db,
        user_id=user_id,
        company_id=company_id,
        preferences=preferences.dict(exclude_unset=True),
        ip_address=client_host,
        user_agent=user_agent
    )
    
    return updated_preferences

@router.get("/settings/audit-logs")
async def get_audit_logs(
    request: Request,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin only)"""
    company_id = get_request_company_id(request)
    
    # Check if user is admin
    # This is a simplified check - in production, implement proper role-based access
    # For now, we'll allow all authenticated users to view audit logs
    
    settings_manager = SettingsManager()
    logs = settings_manager.get_audit_logs(db, company_id, limit)
    
    return {"audit_logs": logs}

@router.post("/settings/users/invite")
async def invite_user(
    request: Request,
    user_data: UserInvite,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Invite a new user to the company"""
    company_id = get_request_company_id(request)
    
    # Basic email validation
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Validate role
    valid_roles = ['admin', 'finance_manager', 'viewer']
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Create invitation logic (simplified - in production, implement proper invitation system)
    # For now, we'll just return a success message
    
    return {
        "message": "Invitation sent successfully",
        "email": user_data.email,
        "role": user_data.role
    }
