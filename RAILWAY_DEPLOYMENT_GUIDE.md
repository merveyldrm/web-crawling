# 🚂 Railway Deployment Guide - FastAPI + Playwright

## 🔍 Build Failure Analysis

Your build likely failed due to:
1. **Missing Chromium dependencies** - Playwright needs system libraries
2. **Incorrect Python version** - Railway needs explicit runtime.txt
3. **Missing build commands** - Chromium installation not configured
4. **Incorrect start command** - FastAPI needs proper uvicorn command

## 📁 Fixed File Structure

```
your-project/
├── app.py                 # FastAPI main application
├── parser.py              # Your Playwright scraper
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version specification
├── Procfile             # Railway start command
├── railway.json         # Railway configuration
├── nixpacks.toml        # Build configuration with Chromium
└── RAILWAY_DEPLOYMENT_GUIDE.md
```

## ⚙️ Railway Configuration

### Build Command (Automatic)
Railway uses `nixpacks.toml` to automatically:
1. Install system dependencies (Chromium, libraries)
2. Install Python packages from `requirements.txt`
3. Install Playwright browsers with `playwright install --with-deps chromium`

### Start Command
```
uvicorn app:app --host 0.0.0.0 --port $PORT
```

## 🚀 Step-by-Step Redeployment

### 1. Push Fixed Files
```bash
git add .
git commit -m "Fix Railway deployment for FastAPI + Playwright"
git push origin main
```

### 2. Railway Dashboard Setup
1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Click "Deploy Now"

### 3. Monitor Build Process
- Build time: 5-10 minutes
- Watch for Chromium installation logs
- Check for any error messages

### 4. Verify Deployment
- Visit your Railway URL
- Test `/` endpoint (health check)
- Test `/scrape?url=https://example.com`

## 🔧 Key Configuration Files

### requirements.txt
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
playwright>=1.40.0
beautifulsoup4>=4.12.0
requests>=2.31.0
pandas>=1.5.0
numpy>=1.21.0
python-dotenv>=1.0.0
python-multipart>=0.0.6
```

### runtime.txt
```txt
python-3.11.7
```

### Procfile
```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

### nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["chromium", "xvfb", "libxi6", "libgconf-2-4", "libnss3", "libatk-bridge2.0-0", "libdrm2", "libxkbcommon0", "libxcomposite1", "libxdamage1", "libxrandr2", "libgbm1", "libpango-1.0-0", "libcairo2", "libasound2"]

[phases.install]
cmds = [
  "pip install -r requirements.txt",
  "playwright install --with-deps chromium"
]

[phases.build]
cmds = ["echo 'Build completed'"]

[start]
cmd = "uvicorn app:app --host 0.0.0.0 --port $PORT"
```

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-app.railway.app/
```

### 2. Scraping Test
```bash
curl "https://your-app.railway.app/scrape?url=https://example.com"
```

### 3. API Documentation
Visit: `https://your-app.railway.app/docs`

## 🚨 Common Issues & Solutions

### Build Timeout
- **Issue**: Build takes too long
- **Solution**: Railway has 15-minute build limit, should complete within 10 minutes

### Chromium Installation Failed
- **Issue**: `playwright install` fails
- **Solution**: Check `nixpacks.toml` has all required system packages

### Port Issues
- **Issue**: App doesn't start
- **Solution**: Ensure using `$PORT` environment variable

### Memory Issues
- **Issue**: Out of memory during build
- **Solution**: Railway provides 1GB RAM, sufficient for most builds

## 📊 Expected Build Logs

```
✓ Installing system dependencies...
✓ Installing Python packages...
✓ Installing Playwright browsers...
✓ Build completed
✓ Starting application...
```

## 🔄 Environment Variables (Optional)

Add these in Railway dashboard if needed:
```
PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright
CHROME_BIN=/usr/bin/chromium-browser
```

## ✅ Success Criteria

- ✅ Build completes without errors
- ✅ Health check endpoint responds
- ✅ Scraping endpoint works
- ✅ API documentation accessible
- ✅ No timeout or memory errors

## 🆘 Troubleshooting

### If Build Still Fails:
1. Check Railway build logs for specific errors
2. Verify all files are committed and pushed
3. Try clearing Railway cache and redeploying
4. Check if repository is public (Railway requirement)

### If App Doesn't Start:
1. Check start command in Railway dashboard
2. Verify `app.py` has correct FastAPI setup
3. Check if port binding is correct
4. Review application logs in Railway dashboard

---

**Note**: This configuration ensures Chromium is properly installed and Playwright can run in Railway's environment without Docker. 