# Render Deployment Configuration

This document contains the exact configuration needed for deploying the backend on Render.

## Service Configuration

**Service Type**: Web Service  
**Name**: finhealth-backend  
**Runtime**: Python 3  
**Branch**: main  
**Root Directory**: `backend`

## Build & Start Commands

**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables

Set these in the Render dashboard under Environment tab:

### Required Variables

```bash
# Database (use Internal Database URL from your PostgreSQL instance)
DATABASE_URL=postgresql://finhealth_user:password@dpg-xxxxx/finhealth_production

# Security Keys (generate using the commands in DEPLOYMENT_GUIDE.md)
JWT_SECRET=<your-generated-64-char-secret>
ENCRYPTION_KEY=<your-generated-32-char-key>
FIELD_ENCRYPTION_KEY=<your-generated-32-char-key>

# CORS (update with your Vercel URL after frontend deployment)
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000

# Application
ENVIRONMENT=production
DEBUG=false
```

### Optional Variables

```bash
# OpenAI (for AI insights)
OPENAI_API_KEY=sk-...

# Redis (for caching - can add Render Redis instance)
REDIS_URL=redis://...

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
```

## Database Setup

1. Create PostgreSQL database on Render
2. Name: `finhealth-db`
3. Database: `finhealth_production`
4. User: `finhealth_user`
5. Copy the **Internal Database URL** to `DATABASE_URL` environment variable

## Health Check

After deployment, verify:
```
GET https://your-backend.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "financial-health-api"
}
```

## Auto-Deploy

Render will automatically deploy when you push to the `main` branch on GitHub.

## Logs

View logs in Render dashboard: Service → Logs tab
