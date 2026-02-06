# Vercel Deployment Guide - FinHealth Application

Complete guide to deploy the FinHealth frontend to Vercel with proper configuration.

---

## Prerequisites

- ✅ GitHub account with repository access
- ✅ Vercel account (sign up at [vercel.com](https://vercel.com))
- ✅ Backend API deployed and accessible (e.g., on Render, Railway, or similar)

---

## Step 1: Prepare Your Repository

### 1.1 Verify Project Structure
```
FinHealth/
├── frontend/           # React application
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vercel.json    # Vercel configuration
└── backend/           # Python FastAPI (deployed separately)
```

### 1.2 Check `vercel.json` Configuration
Ensure your `frontend/vercel.json` exists with proper settings:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/favicon.ico",
      "dest": "/favicon.ico"
    },
    {
      "src": "/manifest.json",
      "dest": "/manifest.json"
    },
    {
      "src": "/robots.txt",
      "dest": "/robots.txt"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### 1.3 Update Environment Variables Template
Create `frontend/.env.example`:

```bash
# Backend API URL (update with your deployed backend URL)
REACT_APP_API_URL=https://your-backend-api.onrender.com

# Optional: Analytics, etc.
# REACT_APP_ANALYTICS_ID=your-analytics-id
```

---

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

#### 2.1 Import Project
1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"**
3. Select your GitHub repository: `suman-2212/FinHealth`
4. Click **"Import"**

#### 2.2 Configure Project Settings
- **Framework Preset**: `Create React App`
- **Root Directory**: `frontend` ⚠️ **IMPORTANT**
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `build` (auto-detected)
- **Install Command**: `npm install` (auto-detected)

#### 2.3 Add Environment Variables
Click **"Environment Variables"** and add:

| Name | Value | Environment |
|------|-------|-------------|
| `REACT_APP_API_URL` | `https://your-backend.onrender.com` | Production, Preview, Development |

**Replace** `https://your-backend.onrender.com` with your actual backend URL.

#### 2.4 Deploy
1. Click **"Deploy"**
2. Wait for build to complete (2-3 minutes)
3. Your app will be live at: `https://your-project.vercel.app`

---

### Option B: Deploy via Vercel CLI

#### 2.1 Install Vercel CLI
```bash
npm install -g vercel
```

#### 2.2 Login to Vercel
```bash
vercel login
```

#### 2.3 Navigate to Frontend Directory
```bash
cd frontend
```

#### 2.4 Deploy
```bash
# First deployment
vercel

# Production deployment
vercel --prod
```

#### 2.5 Set Environment Variables via CLI
```bash
vercel env add REACT_APP_API_URL production
# Enter your backend URL when prompted
```

---

## Step 3: Configure Custom Domain (Optional)

### 3.1 Add Domain in Vercel
1. Go to your project dashboard
2. Click **"Settings"** → **"Domains"**
3. Add your custom domain (e.g., `finhealth.yourdomain.com`)

### 3.2 Update DNS Records
Add these records to your domain provider:

**For subdomain (finhealth.yourdomain.com):**
```
Type: CNAME
Name: finhealth
Value: cname.vercel-dns.com
```

**For root domain (yourdomain.com):**
```
Type: A
Name: @
Value: 76.76.21.21
```

---

## Step 4: Environment-Specific Configuration

### 4.1 Production Environment Variables
```bash
REACT_APP_API_URL=https://finhealth-backend.onrender.com
```

### 4.2 Preview/Staging Environment Variables
```bash
REACT_APP_API_URL=https://finhealth-backend-staging.onrender.com
```

### 4.3 Development Environment Variables
```bash
REACT_APP_API_URL=http://localhost:8000
```

---

## Step 5: Backend CORS Configuration

⚠️ **CRITICAL**: Update your backend to allow requests from Vercel domain.

### Python FastAPI Example (`backend/main.py`):
```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Update allowed origins
origins = [
    "http://localhost:3000",           # Local development
    "https://your-project.vercel.app", # Vercel production
    "https://*.vercel.app",            # Vercel preview deployments
    "https://your-custom-domain.com"   # Custom domain (if any)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Step 6: Verify Deployment

### 6.1 Check Build Logs
1. Go to Vercel dashboard
2. Click on your deployment
3. Check **"Building"** tab for any errors

### 6.2 Test Application
1. Visit your Vercel URL: `https://your-project.vercel.app`
2. Test key features:
   - ✅ Login/Register
   - ✅ Company selection
   - ✅ Dashboard loads
   - ✅ API calls work (check Network tab)

### 6.3 Common Issues & Fixes

#### Issue: "Failed to fetch" or CORS errors
**Fix**: Update backend CORS settings (see Step 5)

#### Issue: API calls return 404
**Fix**: Verify `REACT_APP_API_URL` environment variable is set correctly

#### Issue: Blank page after deployment
**Fix**: Check browser console for errors, verify build logs

#### Issue: ESLint errors during build
**Fix**: Already fixed in latest commit! If issues persist:
```bash
# In frontend directory
npm run build
# Fix any errors shown
```

---

## Step 7: Continuous Deployment

### 7.1 Automatic Deployments
Vercel automatically deploys when you push to GitHub:

- **Push to `main`** → Production deployment
- **Push to other branches** → Preview deployment
- **Pull requests** → Preview deployment with unique URL

### 7.2 Disable Auto-Deploy (Optional)
1. Go to **Settings** → **Git**
2. Toggle **"Production Branch"** settings
3. Configure deployment branches

---

## Step 8: Performance Optimization

### 8.1 Enable Analytics
1. Go to **Analytics** tab in Vercel dashboard
2. Enable **Web Analytics**
3. Monitor performance metrics

### 8.2 Enable Speed Insights
1. Install package:
```bash
npm install @vercel/speed-insights
```

2. Add to `src/index.js`:
```javascript
import { SpeedInsights } from '@vercel/speed-insights/react';

// In your root component
<SpeedInsights />
```

### 8.3 Configure Caching
Add to `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

---

## Step 9: Monitoring & Debugging

### 9.1 View Deployment Logs
```bash
vercel logs <deployment-url>
```

### 9.2 Check Function Logs (if using serverless functions)
1. Go to **Deployments** → Select deployment
2. Click **"Functions"** tab
3. View real-time logs

### 9.3 Enable Error Tracking (Optional)
Integrate with Sentry or similar:
```bash
npm install @sentry/react
```

---

## Quick Reference Commands

```bash
# Deploy to production
cd frontend && vercel --prod

# View logs
vercel logs

# List deployments
vercel ls

# Remove deployment
vercel rm <deployment-url>

# Pull environment variables
vercel env pull

# Add environment variable
vercel env add VARIABLE_NAME
```

---

## Troubleshooting Checklist

- [ ] Root directory set to `frontend`
- [ ] `REACT_APP_API_URL` environment variable configured
- [ ] Backend CORS allows Vercel domain
- [ ] Build command is `npm run build`
- [ ] Output directory is `build`
- [ ] No ESLint errors in code
- [ ] Backend is deployed and accessible
- [ ] Environment variables are set for all environments

---

## Support & Resources

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel Support**: https://vercel.com/support
- **Community**: https://github.com/vercel/vercel/discussions

---

## Current Deployment Status

✅ **Repository**: `suman-2212/FinHealth`  
✅ **Latest Commit**: `18fbf27` (ESLint fixes applied)  
🔄 **Build Status**: Should deploy successfully now  
📍 **Next Step**: Follow Step 2 to deploy to Vercel

---

**Last Updated**: February 6, 2026
