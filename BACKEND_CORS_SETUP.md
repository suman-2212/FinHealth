# Backend CORS Configuration Guide

## Current Setup

Your backend at `https://finhealth-7tze.onrender.com` now uses environment-based CORS configuration for security.

## Required Environment Variables on Render

Add this environment variable in your Render dashboard:

### **ALLOWED_ORIGINS**

**Value**: Your Vercel deployment URLs (comma-separated)

```
ALLOWED_ORIGINS=https://fin-health.vercel.app,https://fin-health-git-main.vercel.app,https://*.vercel.app
```

### How to Add in Render:

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your `finhealth-api` service
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Key: `ALLOWED_ORIGINS`
6. Value: (paste your Vercel URLs after deployment)
7. Click **Save Changes**

---

## After Vercel Deployment

Once you deploy to Vercel, you'll get URLs like:

- **Production**: `https://fin-health.vercel.app`
- **Preview**: `https://fin-health-git-main.vercel.app`
- **Branch**: `https://fin-health-git-feature.vercel.app`

### Update ALLOWED_ORIGINS:

```
ALLOWED_ORIGINS=https://fin-health.vercel.app,https://fin-health-git-main.vercel.app
```

Or use wildcard for all Vercel deployments:
```
ALLOWED_ORIGINS=https://*.vercel.app
```

---

## Default Allowed Origins (Already Configured)

The backend automatically allows:
- ✅ `http://localhost:3000` (local React dev)
- ✅ `http://localhost:5173` (local Vite dev)
- ✅ `https://finhealth-7tze.onrender.com` (backend itself)

---

## Testing CORS

After deployment, test CORS with:

```bash
curl -H "Origin: https://your-vercel-url.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Authorization" \
     -X OPTIONS \
     https://finhealth-7tze.onrender.com/api/auth/login
```

Should return:
```
access-control-allow-origin: https://your-vercel-url.vercel.app
access-control-allow-credentials: true
```

---

## Troubleshooting

### Issue: CORS error in browser console
```
Access to fetch at 'https://finhealth-7tze.onrender.com/api/...' 
from origin 'https://your-app.vercel.app' has been blocked by CORS policy
```

**Fix**: Add your Vercel URL to `ALLOWED_ORIGINS` in Render environment variables

### Issue: Wildcard not working
**Fix**: Use specific URLs instead of `*.vercel.app` pattern

---

**Last Updated**: February 6, 2026
