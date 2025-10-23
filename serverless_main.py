"""
Serverless Entry Point - Azure Functions Compatible
Lightweight wrapper for both local development and Azure Functions deployment
"""
import os
import sys
import logging

# Configure logging for serverless
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_execution_context():
    """Detect if running in Azure Functions or local environment"""
    if os.environ.get('FUNCTIONS_WORKER_RUNTIME'):
        return 'azure_functions'
    elif os.environ.get('WEBSITE_SITE_NAME'):  # Azure App Service
        return 'azure_app_service'
    else:
        return 'local_development'

# Export the context for use by functions
EXECUTION_CONTEXT = get_execution_context()

# Import core functionality that works in both environments
try:
    from core.schedule_agent import ScheduleAgent
    from services.auth_service import AuthenticationService
    from services.scheduling_tools import HospitalHoursTool, EmployeeAvailabilityTool
    from config import OPENAI_CONFIG, API_ENDPOINTS
    
    print(f"✅ Core modules loaded successfully for {EXECUTION_CONTEXT}")
    
except ImportError as e:
    print(f"❌ Failed to load core modules: {e}")
    sys.exit(1)