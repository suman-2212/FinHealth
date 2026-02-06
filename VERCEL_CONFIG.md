# Vercel Deployment Configuration

## Quick Setup Guide

### 1. Framework Preset
**Select**: `Create React App`

### 2. Root Directory
**Set to**: `frontend`

### 3. Build Settings (Auto-detected)
- **Build Command**: `npm run build`
- **Output Directory**: `build`
- **Install Command**: `npm install`

### 4. Environment Variables

Add this in Vercel's Environment Variables section:

| Key | Value |
|-----|-------|
| `REACT_APP_API_URL` | `https://finhealth-7tze.onrender.com` |

**Important**: Add this variable for all environments (Production, Preview, Development)

---

## Post-Deployment Checklist

After deploying, verify:

- [ ] Frontend is accessible at your Vercel URL
- [ ] Login/Register pages load
- [ ] API calls connect to backend (check Network tab)
- [ ] No CORS errors in console

---

## Backend CORS Configuration

Make sure your backend at `https://finhealth-7tze.onrender.com` has CORS configured to allow your Vercel domain.

In your backend `main.py`, ensure:

```python
origins = [
    "http://localhost:3000",
    "https://*.vercel.app",  # All Vercel deployments
    "https://your-custom-domain.com"  # If you have one
]
```

---

## Troubleshooting

### Issue: CORS errors
**Fix**: Update backend CORS to include your Vercel URL

### Issue: API calls fail
**Fix**: Verify `REACT_APP_API_URL` is set correctly in Vercel environment variables

### Issue: Blank page
**Fix**: Check browser console for errors, verify build logs in Vercel dashboard

---

**Backend URL**: https://finhealth-7tze.onrender.com  
**Last Updated**: February 6, 2026
