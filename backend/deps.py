from fastapi import Request, HTTPException, status
import uuid


def get_request_user_id(request: Request) -> uuid.UUID:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))


def get_request_company_id(request: Request) -> uuid.UUID:
    company_id = getattr(request.state, "company_id", None)
    if not company_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Company-ID")
    return company_id if isinstance(company_id, uuid.UUID) else uuid.UUID(str(company_id))
