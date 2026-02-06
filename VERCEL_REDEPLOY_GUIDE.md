# How to Add Environment Variable and Redeploy on Vercel

## Step-by-Step Guide

### Method 1: Add Environment Variable in Vercel Dashboard

#### Step 1: Go to Project Settings
1. In Vercel dashboard, click on your project name
2. Click **"Settings"** tab at the top
3. Click **"Environment Variables"** in the left sidebar

#### Step 2: Add the Variable
1. You'll see a form with:
   - **Key** field
   - **Value** field
   - Environment checkboxes (Production, Preview, Development)

2. Fill in:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: `https://finhealth-7tze.onrender.com`
   - **Check**: ✅ Production, ✅ Preview, ✅ Development

3. Click **"Save"** button

#### Step 3: Trigger Redeploy
After adding the variable, you have 3 options:

**Option A: From Deployments Tab**
1. Click **"Deployments"** tab
2. Find your latest deployment
3. Click the **three dots (...)** on the right
4. Click **"Redeploy"**
5. Confirm by clicking **"Redeploy"** again

**Option B: Push to GitHub**
```bash
# Make any small change (like updating README)
cd d:\FinHealth
git commit --allow-empty -m "trigger redeploy"
git push origin main
```

**Option C: From Project Overview**
1. Go to your project overview page
2. Click **"Redeploy"** button (if available)

---

### Method 2: Use Vercel CLI (Alternative)

If you can't access the dashboard:

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Navigate to frontend
cd d:\FinHealth\frontend

# Add environment variable
vercel env add REACT_APP_API_URL production
# When prompted, enter: https://finhealth-7tze.onrender.com

# Redeploy
vercel --prod
```

---

## Troubleshooting

### Can't Find Redeploy Button?
- Make sure you're on the **Deployments** tab
- Look for the **three dots menu (...)** next to your deployment
- The option should say "Redeploy" or "Redeploy with existing Build Cache"

### Environment Variable Not Taking Effect?
- Make sure you selected **Production** environment
- Wait for redeploy to complete (2-3 minutes)
- Clear browser cache and reload

### Still Having Issues?
**Quick Fix**: Make an empty commit to trigger auto-deploy:
```bash
cd d:\FinHealth
git commit --allow-empty -m "redeploy with env vars"
git push origin main
```

---

## Verification

After redeployment:
1. Open your Vercel URL
2. Open browser DevTools (F12)
3. Go to Console tab
4. Try to login
5. Check Network tab - API calls should go to `https://finhealth-7tze.onrender.com`

---

**Your Backend URL**: `https://finhealth-7tze.onrender.com`
