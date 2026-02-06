# Vercel Deployment Configuration

This document contains the exact configuration needed for deploying the frontend on Vercel.

## Project Configuration

**Framework Preset**: Create React App  
**Root Directory**: `frontend`  
**Build Command**: `npm run build`  
**Output Directory**: `build`  
**Install Command**: `npm install`

## Environment Variables

Set these in the Vercel dashboard under Settings → Environment Variables:

### Production Environment

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `REACT_APP_API_URL` | `https://your-backend.onrender.com` | Production |

**Important**: Replace `your-backend.onrender.com` with your actual Render backend URL.

### Preview/Development (Optional)

For preview deployments, you can use the same production backend or a separate staging backend:

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `REACT_APP_API_URL` | `https://your-backend.onrender.com` | Preview |

## Vercel Configuration File

The `vercel.json` file in the frontend directory contains:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

This ensures React Router works correctly with client-side routing.

## Build Settings

Vercel will automatically detect Create React App and use these settings:

- **Framework**: Create React App
- **Node Version**: 18.x (auto-detected from package.json)
- **Package Manager**: npm

## Deployment

### Initial Deployment

1. Import repository from GitHub: `suman-2212/FinHealth`
2. Set root directory to `frontend`
3. Configure environment variables
4. Click Deploy

### Automatic Deployments

Vercel will automatically deploy when you push to:
- `main` branch → Production deployment
- Other branches → Preview deployments

## Custom Domain (Optional)

To add a custom domain:
1. Go to Project Settings → Domains
2. Add your domain
3. Update DNS records as instructed
4. Update backend CORS to include your custom domain

## Performance Optimization

Vercel automatically provides:
- Global CDN
- Automatic HTTPS
- Compression (Gzip/Brotli)
- Image optimization
- Edge caching

## Monitoring

View deployment logs:
1. Go to Deployments tab
2. Click on a deployment
3. View Function Logs and Build Logs

## Troubleshooting

### Build Fails
- Check build logs in Vercel dashboard
- Verify all dependencies are in package.json
- Ensure no TypeScript errors

### Environment Variables Not Working
- Verify variable name starts with `REACT_APP_`
- Redeploy after adding/changing variables
- Check variable is set for correct environment (Production/Preview)

### 404 on Routes
- Verify `vercel.json` is in frontend directory
- Check rewrites configuration is correct
