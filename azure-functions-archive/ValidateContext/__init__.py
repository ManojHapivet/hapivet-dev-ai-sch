"""
Azure Function: JWT Context Validator
Validates JWT tokens and extracts tenant/location context
"""
import json
import logging
import os
import sys
from typing import Dict, Any

import azure.functions as func

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthenticationService
from config import API_ENDPOINTS

logger = logging.getLogger(__name__)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Validate JWT token and return context information
    
    Expected headers:
    - Authorization: Bearer <jwt_token>
    """
    logger.info('JWT validation function triggered')
    
    try:
        # Get JWT token from Authorization header
        auth_header = req.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "Missing or invalid Authorization header"
                }),
                status_code=401,
                mimetype="application/json"
            )
        
        jwt_token = auth_header.replace('Bearer ', '')
        
        # Initialize authentication service
        auth_service = AuthenticationService(
            base_url=API_ENDPOINTS["auth_base_url"],
            scheduler_base_url=API_ENDPOINTS["scheduler_base_url"]
        )
        
        # Set token and validate
        auth_service.access_token = jwt_token
        
        # Extract context
        try:
            tenant_id, location_id = auth_service.get_credentials()
            
            # Get user info from token
            token_info = auth_service.token_info
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "user_id": token_info.user_id if token_info else None,
                    "tenant_id": tenant_id,
                    "location_id": location_id,
                    "email": getattr(token_info, 'email', None) if token_info else None,
                    "message": "JWT token validated successfully",
                    "execution_context": "azure_functions"
                }),
                status_code=200,
                mimetype="application/json"
            )
            
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": f"Invalid or expired token: {str(e)}"
                }),
                status_code=401,
                mimetype="application/json"
            )
        
    except Exception as e:
        logger.error(f"Context validation failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }),
            status_code=500,
            mimetype="application/json"
        )