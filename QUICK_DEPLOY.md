# 🚀 Quick Deployment Commands

## Generate Secrets (PowerShell)

```powershell
# JWT Secret (64 characters)
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

# Encryption Key (32 characters)
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

## Push to GitHub

```powershell
cd d:\FinHealth
git add .
git commit -m "Configure for production deployment"
git push origin main
```

## Render Configuration

**Web Service Settings:**
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Required Environment Variables:**
- `DATABASE_URL` - From Render PostgreSQL
- `JWT_SECRET` - Generated above
- `ENCRYPTION_KEY` - Generated above
- `FIELD_ENCRYPTION_KEY` - Same as ENCRYPTION_KEY
- `ALLOWED_ORIGINS` - `http://localhost:3000` (update after Vercel)
- `ENVIRONMENT` - `production`
- `DEBUG` - `false`

## Vercel Configuration

**Project Settings:**
- Root Directory: `frontend`
- Framework: Create React App
- Build Command: `npm run build`
- Output Directory: `build`

**Environment Variable:**
- `REACT_APP_API_URL` - Your Render backend URL

## Update CORS After Deployment

1. Get Vercel URL: `https://your-app.vercel.app`
2. Update Render environment variable:
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   ```
3. Render auto-redeploys

## Test URLs

- Backend Health: `https://your-backend.onrender.com/api/health`
- Frontend: `https://your-app.vercel.app`

---

**Full Guide**: See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
