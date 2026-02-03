from sqlalchemy.orm import Session
from models import AuditLog
import uuid

def log_audit(
    db: Session,
    user_id: uuid.UUID,
    company_id: uuid.UUID,
    action: str,
    resource_type: str,
    resource_id: str = None,
    old_values: dict = None,
    new_values: dict = None,
    ip_address: str = None,
    user_agent: str = None,
):
    entry = AuditLog(
        company_id=company_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(entry)
    db.commit()
