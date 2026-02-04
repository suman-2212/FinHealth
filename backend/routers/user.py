from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from models import User, UserCompany, Company
from database import get_db
from deps import get_request_user_id
from auth import get_current_active_user, verify_password, get_password_hash
import uuid
import os
from datetime import datetime

router = APIRouter()

# Pydantic models for validation
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    profile_image_url: Optional[str]
    preferred_language: str
    timezone: str
    notification_preferences: Dict[str, Any]
    two_fa_enabled: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    companies: List[Dict[str, Any]]

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile with company access"""
    
    # Get user's companies
    user_companies = db.query(UserCompany).filter(UserCompany.user_id == current_user.id).all()
    companies_data = []
    
    for uc in user_companies:
        company = db.query(Company).filter(Company.id == uc.company_id).first()
        if company:
            companies_data.append({
                "id": str(company.id),
                "name": company.name,
                "industry": company.industry,
                "role": uc.role,
                "is_default": uc.is_default
            })
    
    # Default notification preferences
    default_notifications = {
        "email_alerts": {
            "risk_changes": True,
            "weekly_summary": True,
            "loan_eligibility": True,
            "report_generation": False
        },
        "push_notifications": {
            "critical_alerts": True,
            "monthly_reports": False
        }
    }
    
    notification_prefs = current_user.notification_preferences or default_notifications
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "role": current_user.role or "viewer",
        "profile_image_url": current_user.profile_image_url,
        "preferred_language": current_user.preferred_language or "en",
        "timezone": current_user.timezone or "UTC",
        "notification_preferences": notification_prefs,
        "two_fa_enabled": current_user.two_fa_enabled or False,
        "last_login_at": current_user.last_login_at,
        "created_at": current_user.created_at,
        "companies": companies_data
    }

@router.put("/profile")
async def update_user_profile(
    request: Request,
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    # Update allowed fields
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    
    if profile_data.preferred_language is not None:
        current_user.preferred_language = profile_data.preferred_language
    
    if profile_data.timezone is not None:
        current_user.timezone = profile_data.timezone
    
    if profile_data.notification_preferences is not None:
        current_user.notification_preferences = profile_data.notification_preferences
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Profile updated successfully"}

@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user's password"""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/upload-profile-image")
async def upload_profile_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload user's profile image"""
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/profile_images"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update user's profile image URL
    current_user.profile_image_url = f"/{file_path}"
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"profile_image_url": f"/{file_path}"}

@router.post("/enable-2fa")
async def enable_2fa(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enable 2FA for user (placeholder for TOTP implementation)"""
    
    # For now, just enable 2FA flag
    # In production, implement TOTP secret generation and QR code
    current_user.two_fa_enabled = True
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "2FA enabled successfully", "qr_code": "placeholder_qr_code"}

@router.post("/disable-2fa")
async def disable_2fa(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disable 2FA for user"""
    
    current_user.two_fa_enabled = False
    current_user.two_fa_secret = None
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "2FA disabled successfully"}

@router.get("/account-activity")
async def get_account_activity(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's account activity log"""
    
    # For now, return basic info
    # In production, implement proper activity tracking
    return {
        "last_login": current_user.last_login_at,
        "recent_activities": [
            {
                "action": "login",
                "timestamp": current_user.last_login_at,
                "ip_address": request.client.host if request.client else "Unknown"
            }
        ]
    }
