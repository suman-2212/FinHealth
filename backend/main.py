import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import uvicorn
from database import get_db, engine
from models import Base
from routers import auth, company, data, metrics, risk, narrative, dashboard_summary, risk_latest, forecast_latest, credit_latest, cashflow_latest, financial_health, risk_analysis, credit_evaluation, forecasting, benchmarking, reports, settings, user
from middleware.tenant import TenantMiddleware

# Create database tables only after database is available
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")
    print("Tables will be created on first request")

app = FastAPI(
    title="Financial Health Intelligence Platform",
    description="AI-powered financial health assessment for SMEs",
    version="1.0.0"
)

# CORS Configuration
# Allow specific origins for security
allowed_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:5173",  # Vite dev server (if used)
    "https://finhealth-7tze.onrender.com",  # Backend itself
    "https://fin-health-amber.vercel.app",  # Vercel production deployment
]

# Add Vercel domains from environment variable
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")

# Add custom allowed origins from environment
# allowed_origins = [
#     "http://localhost:3000",  # Local development
#     "http://localhost:5173",  # Vite dev server (if used)
#     "https://finhealth-7tze.onrender.com",  # Backend itself
#     "https://fin-health-amber.vercel.app",  # Vercel production deployment
# ]

# # Add Vercel domains from environment variable
# vercel_url = os.getenv("VERCEL_URL")
# if vercel_url:
#     allowed_origins.append(f"https://{vercel_url}")

# # Add custom allowed origins from environment
# custom_origins = os.getenv("ALLOWED_ORIGINS", "")
# if custom_origins:
#     allowed_origins.extend([origin.strip() for origin in custom_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(TenantMiddleware)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(company.router, prefix="/api/company", tags=["company"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
app.include_router(dashboard_summary.router, prefix="/api", tags=["dashboard-summary"])
app.include_router(risk_latest.router, prefix="/api/risk", tags=["risk"])
app.include_router(forecast_latest.router, prefix="/api/forecast", tags=["forecast"])
app.include_router(credit_latest.router, prefix="/api/credit", tags=["credit"])
app.include_router(cashflow_latest.router, prefix="/api/cashflow", tags=["cashflow"])
app.include_router(financial_health.router, prefix="/api", tags=["financial-health"])
app.include_router(risk_analysis.router, prefix="/api", tags=["risk-analysis"])
app.include_router(credit_evaluation.router, prefix="/api", tags=["credit-evaluation"])
app.include_router(forecasting.router, prefix="/api", tags=["forecasting"])
app.include_router(benchmarking.router, prefix="/api", tags=["benchmarking"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(user.router, prefix="/api/user", tags=["user"])

@app.get("/")
async def root():
    return {"message": "Financial Health Intelligence Platform API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "financial-health-api"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
