# FinHealth Production Deployment Guide

## 🚀 Quick Deployment Overview

This guide will walk you through deploying the FinHealth SaaS application with:
- **Frontend**: Vercel (React app)
- **Backend**: Render (FastAPI + PostgreSQL)

---

## 📋 Prerequisites

Before starting, ensure you have:
- [x] GitHub account
- [x] Render account (sign up at https://render.com)
- [x] Vercel account (sign up at https://vercel.com)
- [x] OpenAI API key (optional, for AI insights)

---

## Part 1: Backend Deployment on Render

### Step 1: Prepare Secrets

Generate secure secrets for production. Run these commands in PowerShell:

```powershell
# Generate JWT Secret (copy the output)
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

# Generate Encryption Key (copy the output)
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

**Save these values** - you'll need them for Render environment variables.

### Step 2: Push Code to GitHub

```powershell
cd d:\FinHealth
git add .
git commit -m "Configure for production deployment"
git push origin main
```

### Step 3: Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `finhealth-db`
   - **Database**: `finhealth_production`
   - **User**: `finhealth_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free (or paid for production)
4. Click **"Create Database"**
5. **Copy the Internal Database URL** (starts with `postgresql://`)

### Step 4: Create Web Service on Render

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `suman-2212/FinHealth`
3. Configure:
   - **Name**: `finhealth-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid for production)

### Step 5: Set Environment Variables

In the Render dashboard, go to **Environment** tab and add:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | *Paste the Internal Database URL from Step 3* |
| `JWT_SECRET` | *Paste the JWT secret you generated* |
| `ENCRYPTION_KEY` | *Paste the encryption key you generated* |
| `FIELD_ENCRYPTION_KEY` | *Paste the same encryption key* |
| `ALLOWED_ORIGINS` | `http://localhost:3000` *(we'll update this after Vercel deployment)* |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `OPENAI_API_KEY` | *Your OpenAI API key (optional)* |

### Step 6: Deploy Backend

1. Click **"Create Web Service"**
2. Wait for deployment to complete (5-10 minutes)
3. Once deployed, **copy your backend URL**: `https://finhealth-backend.onrender.com`

### Step 7: Test Backend

Open your browser and visit:
```
https://finhealth-backend.onrender.com/api/health
```

You should see:
```json
{"status": "healthy", "service": "financial-health-api"}
```

---

## Part 2: Frontend Deployment on Vercel

### Step 1: Update Frontend Environment

Edit `d:\FinHealth\frontend\.env.production` and replace with your actual backend URL:

```bash
REACT_APP_API_URL=https://finhealth-backend.onrender.com
```

### Step 2: Push Updated Code

```powershell
cd d:\FinHealth
git add frontend/.env.production
git commit -m "Update production API URL"
git push origin main
```

### Step 3: Deploy to Vercel

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository: `suman-2212/FinHealth`
4. Configure:
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

### Step 4: Set Environment Variables in Vercel

In the project settings, go to **Environment Variables** and add:

| Key | Value | Environment |
|-----|-------|-------------|
| `REACT_APP_API_URL` | `https://finhealth-backend.onrender.com` | Production |

### Step 5: Deploy Frontend

1. Click **"Deploy"**
2. Wait for deployment (2-5 minutes)
3. **Copy your Vercel URL**: `https://finhealth-xyz123.vercel.app`

---

## Part 3: Update CORS Configuration

### Step 1: Update Backend CORS

1. Go back to Render dashboard
2. Open your `finhealth-backend` service
3. Go to **Environment** tab
4. Update `ALLOWED_ORIGINS` to include your Vercel URL:
   ```
   https://finhealth-xyz123.vercel.app,http://localhost:3000
   ```
5. Click **"Save Changes"**
6. Render will automatically redeploy

### Step 2: Wait for Redeployment

Wait 2-3 minutes for the backend to redeploy with updated CORS settings.

---

## Part 4: Testing & Verification

### ✅ Test Checklist

Visit your Vercel URL and test:

1. **Authentication**
   - [ ] Register a new user
   - [ ] Login with credentials
   - [ ] Verify no CORS errors in browser console (F12)

2. **Company Management**
   - [ ] Create a new company
   - [ ] Switch between companies
   - [ ] Delete a company

3. **Data Upload**
   - [ ] Upload a CSV file with financial data
   - [ ] Verify upload completes successfully

4. **Dashboard & Modules**
   - [ ] Dashboard loads with metrics
   - [ ] Risk Analysis displays data
   - [ ] Credit Evaluation shows score
   - [ ] Forecasting renders charts
   - [ ] Benchmarking loads comparisons

5. **Reports**
   - [ ] Generate a financial report
   - [ ] Download report as PDF

6. **Security**
   - [ ] All API calls use HTTPS (check Network tab)
   - [ ] No CORS errors in console
   - [ ] JWT token persists after page refresh

---

## 🎉 Deployment Complete!

Your FinHealth SaaS application is now live:

- **Frontend**: https://finhealth-xyz123.vercel.app
- **Backend**: https://finhealth-backend.onrender.com
- **Database**: PostgreSQL on Render

---

## 🔧 Troubleshooting

### CORS Errors
- Verify `ALLOWED_ORIGINS` in Render includes your exact Vercel URL
- Check for trailing slashes (should NOT have them)
- Wait for Render to finish redeploying

### Database Connection Errors
- Verify `DATABASE_URL` is set correctly in Render
- Check database is running in Render dashboard
- Ensure database and web service are in same region

### Frontend Not Loading
- Check Vercel deployment logs for build errors
- Verify `REACT_APP_API_URL` is set in Vercel environment variables
- Clear browser cache and try again

### 500 Internal Server Errors
- Check Render logs for backend errors
- Verify all required environment variables are set
- Check database migrations completed successfully

---

## 📞 Support

If you encounter issues:
1. Check Render logs: Dashboard → Service → Logs
2. Check Vercel logs: Dashboard → Project → Deployments → View Function Logs
3. Check browser console for frontend errors (F12)

---

## 🔄 Future Updates

To deploy updates:

**Backend changes:**
```powershell
git add backend/
git commit -m "Update backend"
git push origin main
# Render auto-deploys from GitHub
```

**Frontend changes:**
```powershell
git add frontend/
git commit -m "Update frontend"
git push origin main
# Vercel auto-deploys from GitHub
```

Both platforms support automatic deployments from GitHub!
