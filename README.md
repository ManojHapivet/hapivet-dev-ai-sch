# 🏥 HapiVet Hospital Scheduling Agent

[![Azure App Service](https://img.shields.io/badge/Azure-App%20Service-blue?logo=microsoftazure)](https://azure.microsoft.com/en-us/services/app-service/)
[![Docker](https://img.shields.io/badge/Docker-Container-blue?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.12-green?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange?logo=openai)](https://openai.com/)
[![LangChain](https://img.shields.io/badge/LangChain-AI-purple)](https://langchain.com/)

A **production-ready AI-powered scheduling system** for veterinary hospitals, deployed as a containerized FastAPI application on Azure App Service.

## 🎯 What This Does

This AI agent automatically generates optimized 2-week staff schedules for veterinary hospitals by:

- **Authenticating** users via JWT tokens with multi-tenant support
- **Fetching** real hospital operating hours and employee availability data
- **Generating** intelligent schedules using OpenAI LangChain that respect business rules
- **Returning** production-ready schedule payloads for direct API consumption

## 🏗️ Architecture

```
┌─────────────────────┐
│   FastAPI App       │
│   (Docker Container)│
└──────────┬──────────┘
           │
           ├──> JWT Authentication Middleware
           │
           ├──> AI Schedule Agent (LangChain + OpenAI)
           │
           └──> Backend API Integration
                 ├─> Hospital Hours
                 ├─> Employee Availability
                 └─> Auth Service
```

## 📁 Project Structure

```
havpivet-dev-ai-sch/
├── app.py                      # FastAPI application entry point
├── config.py                   # Configuration and environment settings
├── Dockerfile                  # Container build configuration
├── .dockerignore               # Docker ignore rules
├── requirements-full.txt       # Python dependencies
├── redeploy-container.ps1      # Deployment script
│
├── api/                        # API layer
│   ├── __init__.py
│   └── endpoints.py            # REST API routes and handlers
│
├── core/                       # Business logic
│   ├── __init__.py
│   ├── schedule_agent.py       # AI agent for schedule generation
│   └── data_processors.py      # Data normalization and validation
│
├── models/                     # Data models
│   ├── __init__.py
│   └── requests.py             # Pydantic models for API contracts
│
└── services/                   # External services
    ├── __init__.py
    ├── auth_middleware.py      # JWT authentication and context management
    ├── auth_service.py         # HapiVet authentication service
    ├── base_tool.py            # Base HTTP client for external APIs
    └── scheduling_tools.py     # Hospital data fetching tools (LangChain tools)
```

## 🚀 Deployment

### Production (Azure App Service)

The application is deployed as a Docker container to Azure App Service:

```powershell
# Build, tag, push to ACR, and deploy
.\redeploy-container.ps1
```

**Deployed URL**: https://dev-hv-sch-ai.azurewebsites.net

### Local Development

```bash
# Install dependencies
pip install -r requirements-full.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export API_BASE_URL="your-backend-url"
export JWT_SECRET="your-secret"

# Run locally
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Endpoints

### Documentation
- `GET /docs` - Swagger UI (interactive API documentation)
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI schema

### Health & Status
- `GET /` - Service information
- `GET /health` - Azure health check endpoint
- `GET /api/v1/health` - API health check

### Scheduling (Requires JWT Authentication)
- `POST /api/v1/schedule/generate` - Generate AI-optimized schedule
- `GET /api/v1/hospital/hours` - Get hospital operating hours
- `GET /api/v1/hospital/availability` - Get employee availability
- `GET /api/v1/context/validate` - Validate JWT token and context

## 🔒 Authentication

All API endpoints (except health checks) require JWT authentication:

```bash
POST /api/v1/schedule/generate
Authorization: Bearer <your-jwt-token>
tenant-id: <tenant-id>
location-id: <location-id>
Content-Type: application/json

{
  "query": "Create a balanced two-week schedule with proper coverage",
  "use_agent": true
}
```

**JWT Token Requirements:**
- `tenant_id` - Hospital organization identifier
- `business_location_id` - Specific location within tenant
- `user_id` - Authenticated user identifier

## 📊 Sample Response

```json
{
  "success": true,
  "tenant_id": "c4d17e20-0aff-4918-b0dc-38d6df5584f8",
  "location_id": "87ca5344-8ffb-4013-94a7-518b68910a56",
  "bulk_update_payload": {
    "employeeSchedules": [...],
    "validateOnly": false
  },
  "generation_metadata": {
    "employee_count": 12,
    "schedule_count": 168,
    "operating_days": 7,
    "generation_time": "2.34s"
  }
}
```

## 🔧 Configuration

Set these environment variables in Azure App Service:

```bash
OPENAI_API_KEY=<your-openai-api-key>
API_BASE_URL=<backend-api-base-url>
JWT_SECRET=<jwt-secret-key>
```

## 🐳 Docker

### Build Image
```bash
docker build -t hapivet-scheduler-ai:latest .
```

### Run Locally
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=<your-key> \
  -e API_BASE_URL=<your-url> \
  -e JWT_SECRET=<your-secret> \
  hapivet-scheduler-ai:latest
```

### Push to Azure Container Registry
```bash
az acr login --name hapivetregistry7299
docker tag hapivet-scheduler-ai:latest hapivetregistry7299.azurecr.io/hapivet-scheduler-ai:latest
docker push hapivetregistry7299.azurecr.io/hapivet-scheduler-ai:latest
```

## ⚡ Key Features

- **AI-Powered**: Uses OpenAI GPT-4 with LangChain for intelligent schedule optimization
- **Multi-Tenant**: Supports multiple hospital organizations and locations
- **Production-Ready**: Comprehensive error handling, logging, and validation
- **CORS-Compliant**: Backend proxies external APIs to avoid browser restrictions
- **Containerized**: Docker-based deployment for consistent environments
- **Scalable**: Stateless design suitable for cloud deployment
- **Secure**: JWT authentication with multi-tenant isolation

## 🧪 Testing

### Health Check
```bash
curl https://dev-hv-sch-ai.azurewebsites.net/api/v1/health
```

### With Authentication
```bash
curl -X POST https://dev-hv-sch-ai.azurewebsites.net/api/v1/schedule/generate \
  -H "Authorization: Bearer <your-token>" \
  -H "tenant-id: <tenant-id>" \
  -H "location-id: <location-id>" \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a 2-week schedule", "use_agent": true}'
```

## 📝 Technologies

- **FastAPI** - Modern Python web framework
- **LangChain** - AI agent framework
- **OpenAI GPT-4** - Natural language processing
- **Pydantic** - Data validation
- **Gunicorn + Uvicorn** - Production ASGI server
- **Docker** - Containerization
- **Azure App Service** - Cloud hosting
- **Azure Container Registry** - Container image storage

## 🔄 CI/CD

Deployment is managed via PowerShell script:

```powershell
.\redeploy-container.ps1
```

This script:
1. Builds the Docker image
2. Tags it for Azure Container Registry
3. Pushes to ACR
4. Updates App Service configuration
5. Restarts the application

---

**Built for production veterinary hospital scheduling with enterprise-grade reliability and AI optimization.** 🏥✨