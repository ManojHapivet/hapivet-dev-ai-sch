"""
Hospital Operating Hours Tool
Fetches hospital operating hours using the authentication service
"""

from typing import Any, Dict, List, Optional, Union
from services.base_tool import BaseSchedulingTool
from services.auth_service import AuthenticationService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HospitalHoursTool(BaseSchedulingTool):
    """
    Tool for fetching hospital operating hours
    Inherits common functionality from BaseSchedulingTool
    """
    
    def get_endpoint_path(self) -> str:
        """Get the API endpoint path for hospital operating hours"""
        return "/api/v1/HospitalOperatingHours/location"
    
    def get_tool_name(self) -> str:
        """Get the name of this tool"""
        return "HospitalHours"
    
    def get_operating_hours(self, tenant_id: str = None, location_id: str = None) -> Dict[str, Any]:
        """
        Fetch hospital operating hours
        
        Args:
            tenant_id: Tenant ID (optional, uses auth service if not provided)
            location_id: Location ID (optional, uses auth service if not provided)
            
        Returns:
            Dictionary containing operating hours data or error information
        """
        logger.info("Fetching hospital operating hours...")
        result = self.fetch_data(tenant_id=tenant_id, location_id=location_id)
        
        if result.get("success"):
            # Process and format the data if needed
            data = result.get("data", {})
            
            # Expected format based on your original code:
            # {
            #   "operating_hours": [
            #     {
            #       "dayOfWeek": <int>,
            #       "isOpen": <bool>,
            #       "timeSlots": [
            #         {
            #           "startTime": "<HH:MM:SS>",
            #           "endTime": "<HH:MM:SS>"
            #         }
            #       ],
            #       "notes": "<string>"
            #     }
            #   ]
            # }
            
            return {
                "success": True,
                "operating_hours": data,
                "tool": self.get_tool_name()
            }
        else:
            return result

class BreakTimingsTool(BaseSchedulingTool):
    """
    Tool for fetching break timings
    """
    
    def get_endpoint_path(self) -> str:
        """Get the API endpoint path for break timings"""
        return "/api/v1/BreakTimings/location"  # Adjust this based on actual API
    
    def get_tool_name(self) -> str:
        """Get the name of this tool"""
        return "BreakTimings"
    
    def get_break_timings(self, tenant_id: str = None, location_id: str = None) -> Dict[str, Any]:
        """
        Fetch break timings
        
        Args:
            tenant_id: Tenant ID (optional, uses auth service if not provided)
            location_id: Location ID (optional, uses auth service if not provided)
            
        Returns:
            Dictionary containing break timings data or error information
        """
        logger.info("Fetching break timings...")
        return self.fetch_data(tenant_id=tenant_id, location_id=location_id)

class HolidaysTool(BaseSchedulingTool):
    """
    Tool for fetching holidays
    """
    
    def get_endpoint_path(self) -> str:
        """Get the API endpoint path for holidays"""
        return "/api/v1/Holidays/location"  # Adjust this based on actual API
    
    def get_tool_name(self) -> str:
        """Get the name of this tool"""
        return "Holidays"
    
    def get_holidays(self, tenant_id: str = None, location_id: str = None, year: int = None) -> Dict[str, Any]:
        """
        Fetch holidays
        
        Args:
            tenant_id: Tenant ID (optional, uses auth service if not provided)
            location_id: Location ID (optional, uses auth service if not provided)
            year: Year for which to fetch holidays (optional)
            
        Returns:
            Dictionary containing holidays data or error information
        """
        logger.info("Fetching holidays...")
        kwargs = {}
        if year:
            kwargs["year"] = year
        return self.fetch_data(tenant_id=tenant_id, location_id=location_id, **kwargs)

class OvertimeTool(BaseSchedulingTool):
    """
    Tool for fetching overtime information
    """
    
    def get_endpoint_path(self) -> str:
        """Get the API endpoint path for overtime"""
        return "/api/v1/Overtime/location"  # Adjust this based on actual API
    
    def get_tool_name(self) -> str:
        """Get the name of this tool"""
        return "Overtime"
    
    def get_overtime_info(self, tenant_id: str = None, location_id: str = None) -> Dict[str, Any]:
        """
        Fetch overtime information
        
        Args:
            tenant_id: Tenant ID (optional, uses auth service if not provided)
            location_id: Location ID (optional, uses auth service if not provided)
            
        Returns:
            Dictionary containing overtime data or error information
        """
        logger.info("Fetching overtime information...")
        return self.fetch_data(tenant_id=tenant_id, location_id=location_id)

class EmployeeAvailabilityTool(BaseSchedulingTool):
    """Tool for fetching employee availability summaries"""

    def get_endpoint_path(self) -> str:
        """Get the API endpoint path for employee availability search"""
        return "/api/v1/EmployeeAvailability/search"

    def get_tool_name(self) -> str:
        """Get the name of this tool"""
        return "EmployeeAvailability"



    def search_availability(
        self,
        tenant_id: Optional[str] = None,
        location_id: Optional[str] = None,
        is_active: Optional[bool] = True,
        is_available: Optional[bool] = True
    ) -> Dict[str, Any]:
        """Fetch grouped employee availability information"""
        logger.info("Fetching employee availability details...")

        if tenant_id is None or location_id is None:
            auth_tenant, auth_location = self.auth_service.get_credentials()
            tenant_id = tenant_id or auth_tenant
            location_id = location_id or auth_location

        # Simple payload as per API specification
        payload: Dict[str, Any] = {}
        if is_available is not None:
            payload["isAvailable"] = is_available
        if is_active is not None:
            payload["isActive"] = is_active

        params = {
            "tenantId": tenant_id,
            "locationId": location_id
        }

        response = self._make_api_request(
            method="POST",
            endpoint_path=self.get_endpoint_path(),
            params=params,
            json_data=payload
        )

        if response.success:
            logger.info("Employee availability fetched successfully")
            return {
                "success": True,
                "data": response.data,
                "filters": payload,
                "tenant_id": tenant_id,
                "location_id": location_id,
                "tool": self.get_tool_name()
            }

        logger.error(f"Failed to fetch employee availability: {response.error}")
        return {
            "success": False,
            "error": response.error,
            "status_code": response.status_code,
            "tool": self.get_tool_name()
        }


# Convenience function to create all tools
def create_scheduling_tools(auth_service: AuthenticationService) -> Dict[str, BaseSchedulingTool]:
    """
    Create all scheduling tools with the given authentication service
    
    Args:
        auth_service: Authenticated AuthenticationService instance
        
    Returns:
        Dictionary of tool name to tool instance
    """
    return {
        "hospital_hours": HospitalHoursTool(auth_service),
        "break_timings": BreakTimingsTool(auth_service),
        "holidays": HolidaysTool(auth_service),
        "overtime": OvertimeTool(auth_service),
        "employee_availability": EmployeeAvailabilityTool(auth_service)
    }