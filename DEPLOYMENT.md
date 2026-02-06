# FinHealth SaaS Deployment Guide

## Overview
Deploy your FinHealth financial intelligence SaaS with frontend on Vercel and backend on Render.

## Prerequisites
- GitHub account with repository access
- Vercel account
- Render account
- Domain name (optional)

## Backend Deployment (Render)

### 1. Push Backend to GitHub
```bash
cd backend
git add .
git commit -m "Add production deployment configuration"
git push origin main
```

### 2. Create Render Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure service:
   - **Name**: `finhealth-api`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
   - **Instance Type**: `Free`

### 3. Add Environment Variables
In Render dashboard → Service → Environment:
```
PYTHON_VERSION=3.11.0
PORT=10000
DATABASE_URL=[will be auto-filled from database]
JWT_SECRET=[auto-generated]
ENCRYPTION_KEY=[auto-generated]
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app
ENVIRONMENT=production
```

### 4. Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `finhealth-db`
   - **Database Name**: `financial_health_platform`
   - **User**: `postgres`
   - **Plan**: `Free`

### 5. Connect Database to API
In your web service settings, link the database connection string to `DATABASE_URL`.

### 6. Deploy
Render will automatically deploy. Your backend URL will be: `https://finhealth-api.onrender.com`

## Frontend Deployment (Vercel)

### 1. Push Frontend to GitHub
```bash
cd frontend
git add .
git commit -m "Add Vercel deployment configuration"
git push origin main
```

### 2. Import to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your frontend repository
4. Configure:
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

### 3. Add Environment Variable
In Vercel dashboard → Project → Settings → Environment Variables:
```
REACT_APP_API_URL=https://finhealth-api.onrender.com
```

### 4. Deploy
Click "Deploy". Your frontend will be available at: `https://your-project.vercel.app`

## Post-Deployment Configuration

### 1. Update CORS Settings
In Render dashboard, update `ALLOWED_ORIGINS` to your actual Vercel domain:
```
ALLOWED_ORIGINS=https://your-actual-vercel-domain.vercel.app
```

### 2. Test Production URLs
```bash
# Test backend health
curl https://finhealth-api.onrender.com/api/health

# Test frontend
# Open https://your-project.vercel.app in browser
```

### 3. Verify Functionality
- [ ] User registration/login works
- [ ] JWT tokens stored properly
- [ ] Company creation/deletion works
- [ ] File uploads work (check size limits)
- [ ] All dashboard modules load:
  - [ ] Dashboard Summary
  - [ ] Risk Analysis
  - [ ] Credit Evaluation
  - [ ] Forecasting
  - [ ] Benchmarking
  - [ ] Reports
- [ ] API calls use HTTPS only
- [ ] No CORS errors

## Environment Variables Summary

### Backend (Render)
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: JWT signing secret
- `ENCRYPTION_KEY`: Data encryption key
- `ALLOWED_ORIGINS`: Your Vercel domain
- `ENVIRONMENT`: production
- `OPENAI_API_KEY`: OpenAI API key (if using AI features)
- `REDIS_URL`: Redis connection (if using caching)

### Frontend (Vercel)
- `REACT_APP_API_URL`: Your Render backend URL

## Security Checklist
- [ ] No hardcoded secrets in code
- [ ] HTTPS enforced everywhere
- [ ] CORS properly configured
- [ ] Environment variables set in production
- [ ] Database connection uses SSL
- [ ] File upload size limits enforced
- [ ] JWT tokens have proper expiration
- [ ] Sensitive data encrypted in database

## Troubleshooting

### Common Issues
1. **CORS errors**: Update `ALLOWED_ORIGINS` in Render
2. **Database connection**: Verify `DATABASE_URL` format
3. **Build failures**: Check `requirements.txt` dependencies
4. **API timeouts**: Free Render instances have cold starts (30-60 seconds)
5. **File upload issues**: Check `MAX_FILE_SIZE` and upload directory permissions

### Debug Commands
```bash
# Check backend health
curl https://finhealth-api.onrender.com/api/health

# Check CORS headers
curl -H "Origin: https://your-vercel-domain.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://finhealth-api.onrender.com/api/auth/login
```

### Log Locations
- **Backend**: Render Dashboard → Service → Logs
- **Frontend**: Vercel Dashboard → Project → Functions → Logs

## Domain Configuration (Optional)
1. Add custom domain in Vercel dashboard
2. Update `ALLOWED_ORIGINS` in Render to include custom domain
3. Configure SSL certificates (handled automatically by both platforms)

## Monitoring
- **Render**: Built-in metrics and logs in dashboard
- **Vercel**: Analytics and performance metrics
- **Database**: PostgreSQL metrics in Render dashboard
- **Uptime**: Use external monitoring like UptimeRobot

## Scaling Guide
- **Backend**: Upgrade to paid Render instance for better performance
- **Database**: Upgrade PostgreSQL plan for more resources
- **Frontend**: Vercel Pro plan for advanced features and edge functions

## Backup Strategy
- **Database**: Render provides automated backups (7-day retention)
- **Code**: GitHub repository with version control
- **Environment**: Store secrets securely in platform dashboards
- **User Data**: Regular database exports for critical data

## Production Optimization
- Enable Redis caching for frequently accessed data
- Implement CDN for static assets
- Use database connection pooling
- Monitor and optimize slow queries
- Set up alerting for errors and performance issues
