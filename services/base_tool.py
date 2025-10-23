"""
Base Tool Class for Hospital Scheduling System
Provides common functionality for all scheduling tools
"""

import requests
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from services.auth_service import AuthenticationService, AuthCredentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Data class to hold API response information"""
    success: bool
    data: Optional[Dict[Any, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None

class BaseSchedulingTool(ABC):
    """
    Base class for all hospital scheduling tools
    Provides common authentication, API calling, and error handling functionality
    """
    
    def __init__(self, 
                 auth_service: AuthenticationService,
                 api_base_url: str = "https://dev-hapivet-sch.azurewebsites.net"):
        """
        Initialize the base tool
        
        Args:
            auth_service: Authenticated AuthenticationService instance
            api_base_url: Base URL for the scheduling API
        """
        self.auth_service = auth_service
        self.api_base_url = api_base_url
        self.session = requests.Session()
        
    @abstractmethod
    def get_endpoint_path(self) -> str:
        """
        Get the API endpoint path for this tool
        Must be implemented by subclasses
        
        Returns:
            API endpoint path (e.g., "/api/v1/HospitalOperatingHours/location")
        """
        pass
    
    @abstractmethod
    def get_tool_name(self) -> str:
        """
        Get the name of this tool
        Must be implemented by subclasses
        
        Returns:
            Tool name (e.g., "HospitalHours")
        """
        pass
    
    def _make_api_request(self, 
                         method: str = "GET", 
                         endpoint_path: str = None,
                         params: Dict[str, Any] = None,
                         json_data: Dict[str, Any] = None,
                         additional_headers: Dict[str, str] = None) -> APIResponse:
        """
        Make an authenticated API request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint_path: API endpoint path (if None, uses get_endpoint_path())
            params: Query parameters
            json_data: JSON payload for POST/PUT requests
            additional_headers: Additional headers to include
            
        Returns:
            APIResponse object containing the result
        """
        try:
            # Use provided endpoint or default to tool's endpoint
            if endpoint_path is None:
                endpoint_path = self.get_endpoint_path()
            
            url = f"{self.api_base_url}{endpoint_path}"
            
            # Get authentication headers
            headers = self.auth_service.get_auth_headers()
            
            # Add any additional headers
            if additional_headers:
                headers.update(additional_headers)
            
            logger.info(f"Making {method} request to: {url}")
            
            # Make the request
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=30
            )
            
            # Log response status
            logger.info(f"Response status: {response.status_code}")
            
            # Handle response
            if response.status_code == 200:
                try:
                    data = response.json()
                    return APIResponse(
                        success=True,
                        data=data,
                        status_code=response.status_code
                    )
                except ValueError as e:
                    logger.error(f"Failed to parse JSON response: {str(e)}")
                    return APIResponse(
                        success=False,
                        error=f"Invalid JSON response: {str(e)}",
                        status_code=response.status_code
                    )
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg += f": {error_data['message']}"
                    elif 'error' in error_data:
                        error_msg += f": {error_data['error']}"
                except:
                    error_msg += f": {response.text}"
                
                logger.error(error_msg)
                return APIResponse(
                    success=False,
                    error=error_msg,
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout:
            error_msg = "API request timed out"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg)
            
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to API"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error during API request: {str(e)}"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg)
    
    def fetch_data(self, tenant_id: str = None, location_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Fetch data using this tool
        
        Args:
            tenant_id: Tenant ID (if None, uses from auth service)
            location_id: Location ID (if None, uses from auth service)
            **kwargs: Additional parameters specific to the tool
            
        Returns:
            Dictionary containing the fetched data or error information
        """
        try:
            # Use provided credentials or get from auth service
            if tenant_id is None or location_id is None:
                auth_tenant_id, auth_location_id = self.auth_service.get_credentials()
                tenant_id = tenant_id or auth_tenant_id
                location_id = location_id or auth_location_id
            
            # Prepare parameters
            params = {
                "tenantId": tenant_id,
                "locationId": location_id,
                **kwargs
            }
            
            # Make API request
            response = self._make_api_request(params=params)
            
            if response.success:
                logger.info(f"{self.get_tool_name()} data fetched successfully")
                return {
                    "success": True,
                    "data": response.data,
                    "tool": self.get_tool_name()
                }
            else:
                logger.error(f"Failed to fetch {self.get_tool_name()} data: {response.error}")
                return {
                    "success": False,
                    "error": response.error,
                    "tool": self.get_tool_name()
                }
                
        except Exception as e:
            error_msg = f"Error in {self.get_tool_name()}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "tool": self.get_tool_name()
            }
    
    def validate_credentials(self) -> bool:
        """
        Validate that authentication is still valid
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            return self.auth_service.is_token_valid()
        except Exception as e:
            logger.error(f"Credential validation failed: {str(e)}")
            return False
    
    def refresh_authentication(self, credentials: AuthCredentials) -> bool:
        """
        Refresh authentication if needed
        
        Args:
            credentials: User credentials for re-authentication
            
        Returns:
            True if authentication was refreshed, False if still valid
        """
        try:
            return self.auth_service.refresh_token_if_needed(credentials)
        except Exception as e:
            logger.error(f"Authentication refresh failed: {str(e)}")
            return False