# Azure App Service Deployment Checklist
# dev-hv-sch-ai Hospital Scheduling System

## ✅ Migration Complete - Ready for Deployment

### 📋 Pre-Deployment Checklist

**Azure Resources:**
- ✅ App Service: `dev-hv-sch-ai` (Central India)
- ✅ Resource Group: `dev-hv-sch-ai_group`
- ✅ GitHub Actions: Configured with publish profile

**Application Configuration:**
- ✅ FastAPI app created (`app.py`)
- ✅ Requirements.txt updated for App Service
- ✅ Azure Functions dependencies removed
- ✅ Production-ready middleware added
- ✅ Health check endpoints configured
- ✅ CORS properly configured
- ✅ Environment-based configuration

**Deployment Files:**
- ✅ GitHub Actions workflow updated
- ✅ Startup command files created
- ✅ Web.config for IIS integration
- ✅ Azure Functions artifacts archived

### 🚀 Deployment Steps

1. **Push to GitHub (Triggers Auto-Deployment):**
   ```bash
   git add .
   git commit -m "Migrate to Azure App Service - Ready for deployment"
   git push origin main
   ```

2. **Configure Environment Variables in Azure Portal:**
   
   Navigate to: Azure Portal > App Services > dev-hv-sch-ai > Configuration > Application settings
   
   **Required Variables:**
   ```
   OPENAI_API_KEY = <your-openai-api-key>
   AUTH_BASE_URL = https://dev-hv-auth.azurewebsites.net
   SCHEDULER_BASE_URL = https://dev-hapivet-sch.azurewebsites.net
   CORS_ORIGINS = https://dev-hv-sch-ai.azurewebsites.net,https://localhost:3000
   ```

3. **Set Startup Command:**
   
   Navigate to: Azure Portal > App Services > dev-hv-sch-ai > Configuration > General Settings
   
   **Startup Command:**
   ```
   python -m uvicorn app:app --host 0.0.0.0 --port 8000
   ```

4. **Verify Python Runtime:**
   
   Ensure Python 3.11 is selected in General Settings

### 🔍 Post-Deployment Verification

Once deployed, test these endpoints:

- **✅ Root**: https://dev-hv-sch-ai.azurewebsites.net/
- **✅ Health**: https://dev-hv-sch-ai.azurewebsites.net/health
- **✅ API Health**: https://dev-hv-sch-ai.azurewebsites.net/api/v1/health

### 📊 Expected Response Examples

**Root Endpoint:**
```json
{
  "message": "HapiVet Hospital Scheduling Agent API",
  "version": "1.0.0",
  "status": "running",
  "environment": "production",
  "health": "/api/v1/health"
}
```

**Health Endpoint:**
```json
{
  "status": "healthy",
  "service": "hospital-scheduler-agent",
  "version": "1.0.0",
  "environment": "production"
}
```

### 🛠 Troubleshooting

**If deployment fails:**
1. Check GitHub Actions logs
2. Verify publish profile in GitHub secrets
3. Check Azure App Service logs in Azure Portal

**If app doesn't start:**
1. Verify startup command is set correctly
2. Check environment variables are configured
3. Review Application logs in Azure Portal

**Common Issues:**
- Missing OPENAI_API_KEY: Set in Application Settings
- CORS errors: Verify CORS_ORIGINS includes your domain
- Import errors: Ensure all dependencies in requirements.txt

### 📝 Next Steps After Deployment

1. **Test all API endpoints**
2. **Configure monitoring and alerts**
3. **Set up Application Insights (optional)**
4. **Configure custom domain (if needed)**
5. **Set up SSL certificate**
6. **Configure scaling settings**

### 📞 Support Information

- **Azure Resource**: `/subscriptions/3958d3bd-71f7-441b-b4fb-b2025462a08d/resourceGroups/dev-hv-sch-ai_group/providers/Microsoft.Web/sites/dev-hv-sch-ai`
- **Region**: Central India
- **Runtime**: Python 3.11
- **Deployment**: GitHub Actions (automated)

## 🎉 Ready to Deploy!

Your application is now fully configured for Azure App Service deployment. Simply push your code to trigger the automated deployment process.