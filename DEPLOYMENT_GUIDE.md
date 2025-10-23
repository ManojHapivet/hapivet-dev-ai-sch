# Azure App Service Deployment Guide
# Hospital Scheduling System - HapiVet

## Migration from Azure Functions to Azure App Service

This application has been successfully migrated from Azure Functions to Azure App Service architecture.

## Prerequisites

1. **Azure App Service**: `dev-hv-sch-ai` (already created)
2. **GitHub Repository**: Connected with Actions workflow
3. **Publish Profile**: Configured in GitHub Secrets

## Deployment Steps

### 1. GitHub Actions Deployment (Recommended)

The deployment will happen automatically when you push to the `main` branch:

```bash
git add .
git commit -m "Migrate to Azure App Service"
git push origin main
```

### 2. Manual Deployment (Alternative)

If you need to deploy manually:

```bash
# Install Azure CLI
az login

# Deploy to App Service
az webapp up --name dev-hv-sch-ai --resource-group <your-resource-group> --runtime "PYTHON|3.11"
```

## Azure App Service Configuration

### Required Environment Variables

Set these in Azure Portal > App Service > Configuration > Application Settings:

```bash
OPENAI_API_KEY=<your-openai-api-key>
AUTH_BASE_URL=https://dev-hv-auth.azurewebsites.net
SCHEDULER_BASE_URL=https://dev-hapivet-sch.azurewebsites.net
CORS_ORIGINS=https://dev-hv-sch-ai.azurewebsites.net,https://localhost:3000
```

### Startup Command

Set in Azure Portal > App Service > Configuration > General Settings > Startup Command:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## Application Endpoints

Once deployed, your application will be available at:

- **Base URL**: https://dev-hv-sch-ai.azurewebsites.net
- **Health Check**: https://dev-hv-sch-ai.azurewebsites.net/health
- **API Health**: https://dev-hv-sch-ai.azurewebsites.net/api/v1/health
- **API Documentation**: https://dev-hv-sch-ai.azurewebsites.net/docs (disabled in production)

## API Endpoints

- `GET /` - Root endpoint with service information
- `GET /health` - Health check endpoint
- `GET /api/v1/health` - API health check
- `POST /api/v1/schedule/generate` - Generate AI-powered schedule
- `GET /api/v1/hospital/hours` - Get hospital operating hours
- `GET /api/v1/hospital/availability` - Get employee availability
- `GET /api/v1/context/validate` - Validate JWT token

## Architecture Changes

### Removed (Azure Functions)
- `host.json` - Functions host configuration
- `ScheduleGenerator/` - Function app folder
- `ValidateContext/` - Function app folder
- Azure Functions runtime dependencies

### Added (Azure App Service)
- `app.py` - FastAPI application entry point
- `startup.sh` - Startup script for App Service
- `startup.txt` - Startup command reference
- `web.config` - IIS configuration for Python apps
- Production-ready middleware and security

## Security Features

- CORS properly configured for production
- Trusted host middleware for production
- API documentation disabled in production
- Environment-based configuration
- Health check endpoints for monitoring

## Monitoring and Logging

- Application logs available in Azure Portal
- Health check endpoints for uptime monitoring
- Structured logging with timestamps
- Error handling and HTTP status codes

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Troubleshooting

1. **Application not starting**: Check startup command and logs
2. **CORS errors**: Verify CORS_ORIGINS environment variable
3. **API errors**: Check OpenAI API key and other environment variables
4. **Health check failures**: Verify /health endpoint responds correctly