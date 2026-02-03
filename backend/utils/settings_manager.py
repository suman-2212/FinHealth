import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from models import Company, User, Integration, UserPreference, AuditLog

class SettingsManager:
    """Central settings management with encryption and audit logging"""
    
    def __init__(self):
        # Generate encryption key from environment or use default
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key"""
        key_env = os.environ.get('ENCRYPTION_KEY')
        if key_env:
            try:
                # Try to decode the base64 key
                decoded_key = base64.urlsafe_b64decode(key_env.encode())
                if len(decoded_key) == 32:  # 256 bits
                    return decoded_key
                else:
                    print("Warning: ENCRYPTION_KEY is not 32 bytes, generating new key")
            except Exception as e:
                print(f"Warning: Invalid ENCRYPTION_KEY format: {e}, generating new key")
        
        # Generate a key from a password (in production, use proper key management)
        password = os.environ.get('SETTINGS_PASSWORD', 'default-finhealth-key-2024')
        salt = b'finhealth-salt-2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return ""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return ""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            return ""
    
    def log_audit(self, db: Session, company_id: str, user_id: str, action: str,
                   resource_type: str, resource_id: str, old_values: Dict = None,
                   new_values: Dict = None, ip_address: str = None, user_agent: str = None):
        """Create audit log entry"""
        audit_log = AuditLog(
            company_id=company_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        db.commit()
    
    def update_company_profile(self, db: Session, company_id: str, user_id: str,
                              updates: Dict, ip_address: str = None, user_agent: str = None) -> Dict:
        """Update company profile with audit logging"""
        
        # Get current company data for audit
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError("Company not found")
        
        old_values = {
            'name': company.name,
            'industry': company.industry,
            'registration_number': company.registration_number,
            'financial_year_start': company.financial_year_start,
            'currency': company.currency,
            'gst_number': company.gst_number
        }
        
        # Update company fields
        if 'name' in updates:
            company.name = updates['name']
        if 'industry' in updates:
            company.industry = updates['industry']
        if 'financial_year_start' in updates:
            company.financial_year_start = updates['financial_year_start']
        if 'currency' in updates:
            company.currency = updates['currency']
        if 'gst_number' in updates:
            company.gst_number = updates['gst_number']
        
        db.commit()
        
        # Log audit trail
        new_values = {
            'name': company.name,
            'industry': company.industry,
            'registration_number': company.registration_number,
            'financial_year_start': company.financial_year_start,
            'currency': company.currency,
            'gst_number': company.gst_number
        }
        
        self.log_audit(
            db=db,
            company_id=company_id,
            user_id=user_id,
            action='company_update',
            resource_type='company',
            resource_id=str(company_id),
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            'id': str(company.id),
            'name': company.name,
            'industry': company.industry,
            'registration_number': company.registration_number,
            'financial_year_start': company.financial_year_start,
            'currency': company.currency,
            'gst_number': company.gst_number,
            'updated_at': company.updated_at.isoformat() if company.updated_at else None
        }
    
    def get_company_profile(self, db: Session, company_id: str) -> Optional[Dict]:
        """Get company profile"""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return None
        
        return {
            'id': str(company.id),
            'name': company.name,
            'industry': company.industry,
            'registration_number': company.registration_number,
            'financial_year_start': company.financial_year_start,
            'currency': company.currency,
            'gst_number': company.gst_number,
            'created_at': company.created_at.isoformat(),
            'updated_at': company.updated_at.isoformat() if company.updated_at else None
        }
    
    def create_integration(self, db: Session, company_id: str, user_id: str,
                          integration_data: Dict, ip_address: str = None, user_agent: str = None) -> Dict:
        """Create new integration with encrypted credentials"""
        
        # Encrypt sensitive credentials
        encrypted_credentials = self.encrypt_data(json.dumps(integration_data.get('credentials', {})))
        
        integration = Integration(
            company_id=company_id,
            integration_type=integration_data['integration_type'],
            provider_name=integration_data.get('provider_name', ''),
            api_endpoint=integration_data.get('api_endpoint', ''),
            encrypted_credentials=encrypted_credentials,
            sync_frequency=integration_data.get('sync_frequency', 'daily'),
            configuration=integration_data.get('configuration', {}),
            is_active=integration_data.get('is_active', False)
        )
        
        db.add(integration)
        db.commit()
        
        # Log audit trail
        self.log_audit(
            db=db,
            company_id=company_id,
            user_id=user_id,
            action='integration_add',
            resource_type='integration',
            resource_id=str(integration.id),
            new_values={
                'integration_type': integration.integration_type,
                'provider_name': integration.provider_name,
                'is_active': integration.is_active
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            'id': str(integration.id),
            'integration_type': integration.integration_type,
            'provider_name': integration.provider_name,
            'is_active': integration.is_active,
            'sync_frequency': integration.sync_frequency,
            'last_sync_at': integration.last_sync_at.isoformat() if integration.last_sync_at else None,
            'created_at': integration.created_at.isoformat()
        }
    
    def get_integrations(self, db: Session, company_id: str) -> List[Dict]:
        """Get all integrations for a company"""
        integrations = db.query(Integration).filter(
            Integration.company_id == company_id
        ).all()
        
        result = []
        for integration in integrations:
            result.append({
                'id': str(integration.id),
                'integration_type': integration.integration_type,
                'provider_name': integration.provider_name,
                'is_active': integration.is_active,
                'api_endpoint': integration.api_endpoint,
                'sync_frequency': integration.sync_frequency,
                'last_sync_at': integration.last_sync_at.isoformat() if integration.last_sync_at else None,
                'created_at': integration.created_at.isoformat(),
                'updated_at': integration.updated_at.isoformat() if integration.updated_at else None
            })
        
        return result
    
    def update_user_preferences(self, db: Session, user_id: str, company_id: str,
                               preferences: Dict, ip_address: str = None, user_agent: str = None) -> Dict:
        """Update user preferences"""
        
        # Get existing preferences
        existing_prefs = db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.company_id == company_id
        ).first()
        
        old_values = {}
        if existing_prefs:
            old_values = {
                'email_alerts': existing_prefs.email_alerts,
                'notification_frequency': existing_prefs.notification_frequency,
                'language': existing_prefs.language,
                'timezone': existing_prefs.timezone,
                'date_format': existing_prefs.date_format,
                'currency_display': existing_prefs.currency_display
            }
        
        if existing_prefs:
            # Update existing preferences
            if 'email_alerts' in preferences:
                existing_prefs.email_alerts = preferences['email_alerts']
            if 'notification_frequency' in preferences:
                existing_prefs.notification_frequency = preferences['notification_frequency']
            if 'language' in preferences:
                existing_prefs.language = preferences['language']
            if 'timezone' in preferences:
                existing_prefs.timezone = preferences['timezone']
            if 'date_format' in preferences:
                existing_prefs.date_format = preferences['date_format']
            if 'currency_display' in preferences:
                existing_prefs.currency_display = preferences['currency_display']
            if 'default_dashboard_view' in preferences:
                existing_prefs.default_dashboard_view = preferences['default_dashboard_view']
            if 'chart_preferences' in preferences:
                existing_prefs.chart_preferences = preferences['chart_preferences']
        else:
            # Create new preferences
            existing_prefs = UserPreference(
                user_id=user_id,
                company_id=company_id,
                email_alerts=preferences.get('email_alerts', {}),
                notification_frequency=preferences.get('notification_frequency', 'immediate'),
                language=preferences.get('language', 'en'),
                timezone=preferences.get('timezone', 'UTC'),
                date_format=preferences.get('date_format', 'YYYY-MM-DD'),
                currency_display=preferences.get('currency_display', 'symbol'),
                default_dashboard_view=preferences.get('default_dashboard_view', 'overview'),
                chart_preferences=preferences.get('chart_preferences', {})
            )
            db.add(existing_prefs)
        
        db.commit()
        
        # Log audit trail
        new_values = {
            'email_alerts': existing_prefs.email_alerts,
            'notification_frequency': existing_prefs.notification_frequency,
            'language': existing_prefs.language,
            'timezone': existing_prefs.timezone,
            'date_format': existing_prefs.date_format,
            'currency_display': existing_prefs.currency_display
        }
        
        self.log_audit(
            db=db,
            company_id=company_id,
            user_id=user_id,
            action='preferences_update',
            resource_type='user_preferences',
            resource_id=str(existing_prefs.id),
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            'id': str(existing_prefs.id),
            'email_alerts': existing_prefs.email_alerts,
            'notification_frequency': existing_prefs.notification_frequency,
            'language': existing_prefs.language,
            'timezone': existing_prefs.timezone,
            'date_format': existing_prefs.date_format,
            'currency_display': existing_prefs.currency_display,
            'default_dashboard_view': existing_prefs.default_dashboard_view,
            'chart_preferences': existing_prefs.chart_preferences,
            'updated_at': existing_prefs.updated_at.isoformat() if existing_prefs.updated_at else None
        }
    
    def get_user_preferences(self, db: Session, user_id: str, company_id: str) -> Optional[Dict]:
        """Get user preferences"""
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.company_id == company_id
        ).first()
        
        if not preferences:
            return None
        
        return {
            'id': str(preferences.id),
            'email_alerts': preferences.email_alerts or {},
            'notification_frequency': preferences.notification_frequency,
            'language': preferences.language,
            'timezone': preferences.timezone,
            'date_format': preferences.date_format,
            'currency_display': preferences.currency_display,
            'default_dashboard_view': preferences.default_dashboard_view,
            'chart_preferences': preferences.chart_preferences,
            'created_at': preferences.created_at.isoformat(),
            'updated_at': preferences.updated_at.isoformat() if preferences.updated_at else None
        }
    
    def get_audit_logs(self, db: Session, company_id: str, limit: int = 50) -> List[Dict]:
        """Get audit logs for a company"""
        logs = db.query(AuditLog).filter(
            AuditLog.company_id == company_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
        
        result = []
        for log in logs:
            result.append({
                'id': str(log.id),
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'old_values': log.old_values,
                'new_values': log.new_values,
                'user_id': str(log.user_id) if log.user_id else None,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat()
            })
        
        return result
