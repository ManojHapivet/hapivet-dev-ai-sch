"""
Azure Function: Hospital Schedule Generator
Serverless AI-powered schedule generation for hospital staff
"""
import json
import logging
import os
import sys
from typing import Dict, Any

import azure.functions as func

# Add project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schedule_agent import ScheduleAgent
from services.auth_service import AuthenticationService
from services.scheduling_tools import HospitalHoursTool, EmployeeAvailabilityTool
from config import API_ENDPOINTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function entry point for schedule generation
    
    Expected payload:
    {
        "jwt_token": "Bearer ...",
        "query": "Create a comprehensive schedule...",
        "use_agent": true,
        "start_date": "2025-10-08",  // Optional
        "end_date": "2025-10-22"     // Optional
    }
    """
    logger.info('Schedule generation function triggered')
    
    try:
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Invalid JSON in request body"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate required fields
        jwt_token = req_body.get('jwt_token')
        if not jwt_token:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "jwt_token is required"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Extract parameters
        query = req_body.get('query', 'Create a comprehensive schedule')
        use_agent = req_body.get('use_agent', True)
        start_date = req_body.get('start_date')
        end_date = req_body.get('end_date')
        
        logger.info(f'Processing schedule generation with use_agent={use_agent}')
        
        # Initialize authentication service
        auth_service = AuthenticationService(
            base_url=API_ENDPOINTS["auth_base_url"],
            scheduler_base_url=API_ENDPOINTS["scheduler_base_url"]
        )
        
        # Set the token directly (bypassing login since we have JWT)
        auth_service.access_token = jwt_token.replace('Bearer ', '') if jwt_token.startswith('Bearer ') else jwt_token
        
        # Get tenant/location context from token
        try:
            tenant_id, location_id = auth_service.get_credentials()
        except Exception as e:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": f"Failed to extract tenant context from JWT: {str(e)}"
                }),
                status_code=401,
                mimetype="application/json"
            )
        
        # Initialize scheduling tools
        hospital_tool = HospitalHoursTool(auth_service)
        availability_tool = EmployeeAvailabilityTool(auth_service)
        
        # Fetch hospital data
        logger.info('Fetching hospital operating hours')
        hospital_hours_result = hospital_tool.get_operating_hours(tenant_id, location_id)
        
        if not hospital_hours_result.get("success"):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": f"Failed to fetch operating hours: {hospital_hours_result.get('error')}"
                }),
                status_code=502,
                mimetype="application/json"
            )
        
        logger.info('Fetching employee availability')
        availability_result = availability_tool.search_availability(
            tenant_id=tenant_id,
            location_id=location_id,
            is_available=True,
            is_active=True
        )
        
        if not availability_result.get("success"):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": f"Failed to fetch employee availability: {availability_result.get('error')}"
                }),
                status_code=502,
                mimetype="application/json"
            )
        
        # Initialize and run AI agent
        logger.info('Initializing AI schedule agent')
        schedule_agent = ScheduleAgent()
        
        # Generate schedule
        logger.info('Generating AI schedule')
        result = schedule_agent.generate_schedule(
            tenant_id=tenant_id,
            location_id=location_id,
            hospital_hours=hospital_hours_result.get("operating_hours") or hospital_hours_result.get("data"),
            employee_availability=availability_result.get("data") or {},
            user_query=query,
            use_ai=use_agent,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add serverless execution info
        result["execution_context"] = "azure_functions"
        result["function_name"] = "ScheduleGenerator"
        
        logger.info('Schedule generation completed successfully')
        
        return func.HttpResponse(
            json.dumps(result, default=str),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Schedule generation failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}",
                "execution_context": "azure_functions"
            }),
            status_code=500,
            mimetype="application/json"
        )