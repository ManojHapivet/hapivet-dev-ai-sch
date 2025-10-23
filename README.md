# 🏥 Hospital AI Schedule Generator (Azure Functions)

[![Azure Functions](https://img.shields.io/badge/Azure-Functions-blue?logo=microsoftazure)](https://azure.microsoft.com/en-us/services/functions/)
[![Python](https://img.shields.io/badge/Python-3.9+-green?logo=python)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange?logo=openai)](https://openai.com/)
[![Serverless](https://img.shields.io/badge/Architecture-Serverless-lightblue)](https://azure.microsoft.com/en-us/solutions/serverless/)

A **production-ready serverless AI system** for generating optimized hospital staff schedules using Azure Functions, OpenAI GPT models, and hospital management API integration.

## 🎯 What This Does

This AI agent automatically generates optimized staff schedules for veterinary hospitals by:



- **Authenticating** users via JWT tokens with multi-tenant support## 🎯 What This Agent Does## 🏗️ System Architecture

- **Fetching** real hospital operating hours and employee availability data

- **Generating** intelligent schedules using OpenAI that respect business rules

- **Returning** production-ready schedule payloads for direct API consumption

This AI agent automatically generates optimized 2-week staff schedules for veterinary hospitals by:```

## 🏗️ Code Structure

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐

```

scheduler/- **Authenticating** users via JWT tokens with multi-tenant support│  Authentication │    │   Base Tool      │    │ Scheduling Tools│

├── app.py                          # Main FastAPI application entry point

├── config.py                       # Configuration and environment settings- **Fetching** real hospital operating hours and employee availability data│    Service      │────│     Class        │────│   (Hospital,    │

├── requirements.txt                # Python dependencies

├── docker-compose.yml              # Docker deployment configuration- **Generating** intelligent schedules using OpenAI that respect business rules│                 │    │                  │    │ Break, Holiday, │

├── Dockerfile                      # Container build configuration

│- **Returning** production-ready schedule payloads for direct API consumption│                 │    │                  │    │   Overtime)     │

├── api/                            # API layer - HTTP endpoints

│   ├── __init__.py└─────────────────┘    └──────────────────┘    └─────────────────┘

│   └── endpoints.py                # REST API routes and handlers

│## 🏗️ Code Structure         │                       │                       │

├── core/                           # Business logic - AI agent core

│   ├── __init__.py         └───────────────────────┼───────────────────────┘

│   ├── schedule_agent.py           # AI agent for schedule generation

│   └── data_processors.py          # Data normalization and validation```                                 │

│

├── models/                         # Data models - Request/response schemasscheduler/                    ┌──────────────────┐

│   ├── __init__.py

│   └── requests.py                 # Pydantic models for API contracts├── app.py                          # Main FastAPI application entry point                    │  Main Scheduler  │

│

├── services/                       # External services - Auth & data tools├── config.py                       # Configuration and environment settings                    │   (FastAPI +     │

│   ├── __init__.py

│   ├── auth_middleware.py          # JWT authentication and context management├── requirements.txt                # Python dependencies                    │   LangChain)     │

│   ├── auth_service.py             # HapiVet authentication service

│   ├── base_tool.py                # Base HTTP client for external APIs├── docker-compose.yml              # Docker deployment configuration                    └──────────────────┘

│   └── scheduling_tools.py         # Hospital data fetching tools

│├── Dockerfile                      # Container build configuration```

└── test_frontend/                  # Local testing interface

    ├── index.html                  # Simple test frontend│

    └── README.md                   # Test instructions

```├── api/                            # API layer - HTTP endpoints## 📁 File Structure



## 🚀 Production Usage│   ├── __init__.py



### **Main Endpoint**: `/api/v1/schedule/generate`│   └── endpoints.py                # REST API routes and handlers- `auth_service.py` - Handles authentication with HapiVet Auth API



Your frontend application sends a JSON request with an `Authorization` header:│- `base_tool.py` - Base class for all scheduling tools with common functionality



```bash├── core/                           # Business logic - AI agent core- `scheduling_tools.py` - Individual tools for different scheduling data

POST /api/v1/schedule/generate

Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...│   ├── __init__.py- `main_scheduler.py` - FastAPI application with LangChain agents

Content-Type: application/json

│   ├── schedule_agent.py           # AI agent for schedule generation- `config.py` - Configuration file for credentials and endpoints

{

  "query": "Create a balanced two-week schedule with proper coverage",│   └── data_processors.py          # Data normalization and validation- `test_auth.py` - Simple authentication testing script

  "use_agent": true

}│- `example_usage.py` - Complete usage examples

```

├── models/                         # Data models - Request/response schemas- `requirements.txt` - Python dependencies

**The agent automatically:**

1. ✅ Validates JWT token and extracts tenant/location context│   ├── __init__.py

2. 🏥 Fetches hospital operating hours for the tenant/location  

3. 👥 Retrieves employee availability data for 14-day window│   └── requests.py                 # Pydantic models for API contracts## 🚀 Quick Start

4. 🤖 Generates AI-optimized schedule respecting all constraints

5. 📋 Returns sanitized schedule payload ready for API consumption│



### **Response Structure:**└── services/                       # External services - Auth & data tools### 1. Install Dependencies

```json

{    ├── __init__.py

  "success": true,

  "tenant_id": "c4d17e20-0aff-4918-b0dc-38d6df5584f8",    ├── auth_middleware.py          # JWT authentication and context management```bash

  "location_id": "87ca5344-8ffb-4013-94a7-518b68910a56", 

  "bulk_update_payload": {    ├── auth_service.py             # HapiVet authentication servicepip install requests fastapi uvicorn pydantic langchain langchain-openai openai

    "employeeSchedules": [...],

    "validateOnly": false    ├── base_tool.py                # Base HTTP client for external APIs```

  },

  "generation_metadata": {    └── scheduling_tools.py         # Hospital data fetching tools

    "employee_count": 12,

    "schedule_count": 168,```### 2. Configure Credentials

    "operating_days": 7

  }

}

```## 🚀 Production UsageEdit `config.py` and update the credentials:



## 🔧 Configuration



Set environment variables or update `config.py`:### **Main Endpoint**: `/api/v1/schedule/generate````python

- `OPENAI_API_KEY`: Your OpenAI API key for AI generation

- `AUTH_BASE_URL`: HapiVet authentication service URLTEST_CREDENTIALS = {

- `HOSPITAL_API_BASE_URL`: Hospital data service URL

Your frontend application sends a JSON request with an `Authorization` header:    "email": "your_email@example.com",

## 🐳 Deployment

    "password": "your_password",

**Development:**

```bash```bash    "tenant_domain": None,  # Optional

uvicorn app:app --host 0.0.0.0 --port 8000 --reload

```POST /api/v1/schedule/generate    "location_id": None     # Optional



**Production Docker:**Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...}

```bash

docker-compose up -dContent-Type: application/json

```

OPENAI_CONFIG = {

## 🧪 Local Testing

{    "model": "gpt-4o-mini",

**Test the API with the included frontend:**

```bash  "query": "Create a balanced two-week schedule with proper coverage",    "temperature": 0.1,

# 1. Start the API server

uvicorn app:app --host 0.0.0.0 --port 8000 --reload  "use_agent": true    "api_key": "your_openai_api_key_here"  # Replace with your OpenAI API key



# 2. Get a test JWT token  }}

python get_token.py

``````

# 3. Start test frontend

python serve_frontend.py

# Opens browser at http://localhost:3000

```**The agent automatically:**### 3. Test Authentication



The test frontend provides a step-by-step interface to test all API endpoints with real authentication.1. ✅ Validates JWT token and extracts tenant/location context



## 📡 API Endpoints2. 🏥 Fetches hospital operating hours for the tenant/location  ```bash



- `POST /api/v1/schedule/generate` - Main AI schedule generation3. 👥 Retrieves employee availability data for 14-day windowpython test_auth.py

- `GET /api/v1/health` - Health check

- `GET /api/v1/context/validate` - JWT validation only4. 🤖 Generates AI-optimized schedule respecting all constraints```

- `GET /api/v1/hospital/hours` - Hospital operating hours

- `GET /api/v1/hospital/availability` - Employee availability5. 📋 Returns sanitized schedule payload ready for API consumption



## 🔒 AuthenticationThis will test:



All endpoints require a valid JWT token in the `Authorization: Bearer <token>` header. The token must contain:### **Response Structure:**- API connectivity

- `tenant_id`: Hospital organization identifier

- `business_location_id`: Specific location within tenant```json- User authentication

- `user_id`: Authenticated user identifier

{- Token validation

## ⚡ Key Features

  "success": true,- Available tenants and locations

- **Multi-tenant**: Supports multiple hospital organizations

- **AI-Powered**: Uses OpenAI for intelligent schedule optimization    "tenant_id": "c4d17e20-0aff-4918-b0dc-38d6df5584f8",

- **Production-Ready**: Comprehensive error handling, logging, validation

- **CORS-Compliant**: Backend proxies external APIs to avoid browser restrictions  "location_id": "87ca5344-8ffb-4013-94a7-518b68910a56", ### 4. Run Example Usage

- **Modular**: Clean separation of concerns for easy maintenance

- **Scalable**: Stateless design suitable for cloud deployment  "bulk_update_payload": {



---    "employeeSchedules": [...],```bash



**Built for production veterinary hospital scheduling with enterprise-grade reliability and AI optimization.**    "validateOnly": falsepython example_usage.py

  },```

  "generation_metadata": {

    "employee_count": 12,### 5. Start FastAPI Server

    "schedule_count": 168,

    "operating_days": 7```bash

  }python main_scheduler.py

}```

```

Then visit `http://localhost:8000/docs` for the interactive API documentation.

## 🔧 Configuration

## 🔐 Authentication Flow

Set environment variables or update `config.py`:

- `OPENAI_API_KEY`: Your OpenAI API key for AI generation1. **Login**: POST to `/auth/login` with email/password

- `AUTH_BASE_URL`: HapiVet authentication service URL2. **Get User Context**: Automatically fetches accessible tenants and locations

- `HOSPITAL_API_BASE_URL`: Hospital data service URL3. **Token Management**: Handles token expiration and refresh

4. **Multi-Tenant Support**: Switch between different tenants and locations

## 🐳 Deployment

### Sample Authentication Response

**Development:**

```bash```json

uvicorn app:app --host 0.0.0.0 --port 8000 --reload{

```  "success": true,

  "message": "Authentication successful",

**Production Docker:**  "user_id": "c748a39a-34d0-4c5d-f16f-08ddef95269f",

```bash  "current_tenant_id": "578de342-ae62-47ae-8f35-8285c7fccd5c",

docker-compose up -d  "current_location_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",

```  "accessible_tenants_locations": [

    {

## 📡 Additional Endpoints      "tenant_id": "578de342-ae62-47ae-8f35-8285c7fccd5c",

      "tenant_name": "Xsa",

- `GET /api/v1/health` - Health check      "location_id": "519d3177-9d46-4bd1-bf8e-dc52227db602",

- `GET /api/v1/context/validate` - JWT validation only      "location_name": "sddsasafsa",

- `GET /api/v1/hospital/hours` - Hospital operating hours      "is_current": true

- `GET /api/v1/hospital/availability` - Employee availability    }

  ],

## 🔒 Authentication  "has_multiple_tenants": true,

  "has_multiple_locations": false

All endpoints require a valid JWT token in the `Authorization: Bearer <token>` header. The token must contain:}

- `tenant_id`: Hospital organization identifier```

- `business_location_id`: Specific location within tenant

- `user_id`: Authenticated user identifier## 🛠️ Available Tools



## ⚡ Key Features### 1. Hospital Hours Tool

- **Endpoint**: `/tools/hospital-hours`

- **Multi-tenant**: Supports multiple hospital organizations- **Function**: Get hospital operating hours

- **AI-Powered**: Uses OpenAI for intelligent schedule optimization  - **Data**: Days of week, open/close times, time slots

- **Production-Ready**: Comprehensive error handling, logging, validation

- **CORS-Compliant**: Backend proxies external APIs to avoid browser restrictions### 2. Break Timings Tool

- **Modular**: Clean separation of concerns for easy maintenance- **Endpoint**: `/tools/break-timings`

- **Scalable**: Stateless design suitable for cloud deployment- **Function**: Get staff break schedules

- **Data**: Break times, duration, staff assignments

---

### 3. Holidays Tool

**Built for production veterinary hospital scheduling with enterprise-grade reliability and AI optimization.**- **Endpoint**: `/tools/holidays`
- **Function**: Get hospital holidays
- **Data**: Holiday dates, names, special schedules

### 4. Overtime Tool
- **Endpoint**: `/tools/overtime`
- **Function**: Get overtime policies
- **Data**: Overtime rules, rates, scheduling

## 🤖 AI Agent Integration

The system includes LangChain integration for natural language queries:

### Sample AI Query

```bash
POST /schedule/query
{
  "query": "What are the hospital operating hours for Monday?",
  "tenant_id": "optional",
  "location_id": "optional",
  "use_agent": true
}
```

### Agent Response

The AI agent will:
1. Understand the natural language query
2. Determine which tools to use
3. Fetch the required data
4. Provide a user-friendly response

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - Authenticate user
- `GET /auth/accessible-tenants-locations` - Get available tenants/locations

### Tools
- `POST /tools/hospital-hours` - Get operating hours
- `POST /tools/break-timings` - Get break schedules
- `POST /tools/holidays` - Get holidays
- `POST /tools/overtime` - Get overtime info

### AI Agent
- `POST /schedule/query` - Natural language scheduling queries

### Utility
- `GET /health` - Health check
- `POST /demo/quick-test` - Demo endpoint

## 🔧 Configuration

### API Endpoints

```python
API_ENDPOINTS = {
    "auth_base_url": "https://dev-hapivet-auth.azurewebsites.net",
    "scheduler_base_url": "https://dev-hapivet-sch.azurewebsites.net"
}
```

### Hospital API Endpoints

```python
HOSPITAL_API_ENDPOINTS = {
    "operating_hours": "/api/v1/HospitalOperatingHours/location",
    "break_timings": "/api/v1/BreakTimings/location",
    "holidays": "/api/v1/Holidays/location", 
    "overtime": "/api/v1/Overtime/location"
}
```

## 🧪 Testing

### Authentication Test
```bash
python test_auth.py
```

### Individual Tool Testing
```python
from auth_service import authenticate_user
from scheduling_tools import create_scheduling_tools

# Authenticate
auth_service = authenticate_user("email", "password")

# Create tools
tools = create_scheduling_tools(auth_service)

# Test hospital hours
result = tools["hospital_hours"].get_operating_hours()
print(result)
```

## 🎯 Usage Examples

### 1. Basic Tool Usage

```python
# Authenticate
auth_service = authenticate_user("email@example.com", "password")

# Get hospital hours
tools = create_scheduling_tools(auth_service)
hours = tools["hospital_hours"].get_operating_hours()

# Use specific tenant/location
hours = tools["hospital_hours"].get_operating_hours(
    tenant_id="specific-tenant-id",
    location_id="specific-location-id"
)
```

### 2. Multi-Tenant Usage

```python
# Get all accessible combinations
combinations = auth_service.get_all_accessible_tenants_and_locations()

# Use different tenant/location
for combo in combinations:
    if combo["tenant_name"] == "Target Tenant":
        hours = tools["hospital_hours"].get_operating_hours(
            tenant_id=combo["tenant_id"],
            location_id=combo["location_id"]
        )
```

### 3. FastAPI Integration

```python
from fastapi import FastAPI
from main_scheduler import app

# The app is ready to run
# uvicorn main_scheduler:app --reload
```

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Fails**
   - Check email/password in config.py
   - Verify API connectivity
   - Check token expiration

2. **Tool Errors**
   - Ensure authentication is successful first
   - Verify tenant_id and location_id are valid
   - Check API endpoint configurations

3. **Import Errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python path configuration

### Debug Steps

1. Run `test_auth.py` first
2. Check API connectivity
3. Verify credentials
4. Test individual tools
5. Check logs for detailed error messages

## 🚧 Future Enhancements

1. **Additional Tools**
   - Staff scheduling
   - Appointment management
   - Resource allocation

2. **Advanced Features**
   - Real-time updates
   - Webhook integration
   - Advanced AI queries

3. **Security Improvements**
   - Enhanced token management
   - Role-based access control
   - Audit logging

## 📝 Notes

- Replace test credentials with actual values
- API endpoints may need adjustment based on actual documentation
- Token expiration is handled automatically
- Multi-tenant support is built-in
- LangChain integration allows natural language queries

---

**Happy Scheduling! 🏥✨**