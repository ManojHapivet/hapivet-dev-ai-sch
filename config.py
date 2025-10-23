"""
Configuration file for Hospital Scheduling System
Store test credentials and API endpoints
Supports both local development and Azure App Service production environments
"""

import os
from dotenv import load_dotenv

# Load .env file in development (ignored in production)
if not os.environ.get("WEBSITE_SITE_NAME"):
    load_dotenv()




# API Endpoints (Azure Functions compatible)
API_ENDPOINTS = {
    "auth_base_url": os.environ.get("AUTH_BASE_URL", "https://dev-hv-auth.azurewebsites.net"),
    "scheduler_base_url": os.environ.get("SCHEDULER_BASE_URL", "https://dev-hapivet-sch.azurewebsites.net")
}

# Test credentials for local development/demo purposes
TEST_CREDENTIALS = {
    "email": os.environ.get("TEST_EMAIL", "santosh@ibolinva.com"),
    "password": os.environ.get("TEST_PASSWORD", "Password@123"),
    "tenant_domain": os.environ.get("TEST_TENANT_DOMAIN"),
    "location_id": os.environ.get("TEST_LOCATION_ID")
}

# Hospital API Endpoints (adjust these based on actual API documentation)
HOSPITAL_API_ENDPOINTS = {
    "operating_hours": "/api/v1/HospitalOperatingHours/location",
    "break_timings": "/api/v1/BreakTimings/location",
    "holidays": "/api/v1/Holidays/location",
    "overtime": "/api/v1/Overtime/location",
    "staff_schedule": "/api/v1/StaffSchedule/location",
    "appointments": "/api/v1/Appointments/location"
}

# OpenAI API Configuration (Azure Functions compatible)
OPENAI_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.1,
    "api_key": os.environ.get("OPENAI_API_KEY")
}

# Request timeout settings
REQUEST_TIMEOUT = 30

# Logging configuration
LOGGING_LEVEL = "INFO"

# CORS Configuration
def get_cors_origins():
    """Get CORS origins from environment or default"""
    cors_origins_env = os.environ.get("CORS_ORIGINS", "")
    if cors_origins_env:
        return [origin.strip() for origin in cors_origins_env.split(",")]

    # Default origins based on environment
    if os.environ.get("WEBSITE_SITE_NAME"):  # Production (Azure App Service)
        return [
            "https://dev-hv-sch-ai.azurewebsites.net",
            "https://*.azurewebsites.net",
            "https://localhost:3000"  # For testing
        ]
    else:  # Development
        return [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "https://localhost:3000"
        ]

# Production environment check
IS_PRODUCTION = os.environ.get("WEBSITE_SITE_NAME") is not None
