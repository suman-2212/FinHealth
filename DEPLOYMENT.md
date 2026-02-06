# Production Deployment Guide

## Backend Deployment (Render)

### Step 1: Deploy to Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Select the `FinHealth` repository
5. Configure the service:
   - **Name**: `finhealth-api`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

### Step 2: Set up PostgreSQL Database
1. In Render dashboard, click "New" → "PostgreSQL"
2. Configure:
   - **Name**: `finhealth-db`
   - **Database Name**: `finhealth_platform`
   - **User**: `finhealth_user`
   - **Plan**: Free (to start)

### Step 3: Configure Environment Variables
In your web service settings, add these environment variables:

```bash
# Database
DATABASE_URL=postgresql://finhealth_user:password@host:5432/finhealth_platform

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
ENCRYPTION_KEY=your-32-character-encryption-key-here

# CORS (replace with your Vercel URL)
ALLOWED_ORIGINS=https://your-app.vercel.app

# Application
DEBUG=false
ENVIRONMENT=production
PORT=10000

# Optional APIs
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://host:port
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Copy the deployed URL (e.g., `https://finhealth-api.onrender.com`)

## Frontend Deployment (Vercel)

### Step 1: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

### Step 2: Set Environment Variables
In Vercel dashboard → Settings → Environment Variables:
```bash
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

### Step 3: Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Test the deployed application

## Post-Deployment Configuration

### Update Backend CORS
After getting your Vercel URL, update the `ALLOWED_ORIGINS` environment variable on Render:
```bash
ALLOWED_ORIGINS=https://your-app.vercel.app
```

### Test End-to-End Functionality
1. **Authentication**: Test login/register flow
2. **Company Management**: Create/select companies
3. **Data Upload**: Test file uploads
4. **Dashboard**: Verify all modules load correctly
5. **API Calls**: Check all requests go to production backend
6. **CORS**: Ensure no CORS errors in browser console

## Troubleshooting

### Common Issues
1. **CORS Errors**: Update `ALLOWED_ORIGINS` on Render
2. **Database Connection**: Verify `DATABASE_URL` format
3. **Build Failures**: Check logs on Render/Vercel
4. **Environment Variables**: Ensure all required vars are set

### Health Checks
- Backend Health: `https://your-backend.onrender.com/api/health`
- Frontend: Visit your Vercel URL

## Security Notes
- Never commit `.env` files
- Use strong secrets in production
- Enable HTTPS (automatic on Render/Vercel)
- Monitor logs for suspicious activity
