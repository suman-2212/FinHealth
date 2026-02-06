import uuid
import time
from typing import Callable, Optional

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from database import SessionLocal
from auth import verify_token
from models import User, UserCompany


EXEMPT_PATH_PREFIXES = (
    "/api/auth/login",
    "/api/auth/register",
    "/api/health",
    "/docs",
    "/openapi.json",
    "/redoc",
)

COMPANY_OPTIONAL_PREFIXES = (
    "/api/company",
    "/api/company/switch",
    "/api/auth/me",
)


class SimpleRateLimiter:
    def __init__(self, limit_per_minute: int = 240):
        self.limit = limit_per_minute
        self._buckets = {}  # key -> (window_start, count)

    def allow(self, key: str) -> bool:
        now = int(time.time())
        window = now // 60
        prev = self._buckets.get(key)
        if not prev or prev[0] != window:
            self._buckets[key] = (window, 1)
            return True
        if prev[1] >= self.limit:
            return False
        self._buckets[key] = (window, prev[1] + 1)
        return True


rate_limiter = SimpleRateLimiter()


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        path = request.url.path

        if not path.startswith("/api/"):
            return await call_next(request)

        if path.startswith(EXEMPT_PATH_PREFIXES):
            return await call_next(request)

        # Handle CORS preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        if not rate_limiter.allow(client_ip):
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return JSONResponse(
                {"detail": "Missing or invalid Authorization header"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        token = auth_header.split(" ", 1)[1].strip()
        try:
            email = verify_token(token)
        except Exception:
            return JSONResponse(
                {"detail": "Invalid token"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return JSONResponse(
                    {"detail": "User not found"},
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            request.state.user_id = user.id

            if path.startswith(COMPANY_OPTIONAL_PREFIXES):
                return await call_next(request)

            company_id_header = request.headers.get("x-company-id")
            if not company_id_header:
                return JSONResponse(
                    {"detail": "Missing X-Company-ID"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            try:
                company_uuid = uuid.UUID(company_id_header)
            except Exception:
                return JSONResponse(
                    {"detail": "Invalid X-Company-ID"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            link = db.query(UserCompany).filter(
                UserCompany.user_id == user.id,
                UserCompany.company_id == company_uuid,
            ).first()
            if not link:
                return JSONResponse(
                    {"detail": "Forbidden for this company"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            request.state.company_id = company_uuid

            return await call_next(request)
        finally:
            db.close()
