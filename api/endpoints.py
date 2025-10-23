"""
API Endpoints for Hospital Scheduler
Production-ready endpoints for schedule generation and data fetching
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from models.requests import ScheduleQueryRequest
from services.auth_middleware import RequestContext, get_request_context

logger = logging.getLogger(__name__)
router = APIRouter()

# Lazy-load AI agent only when needed (to avoid import errors if langchain not installed)
_schedule_agent = None

def get_schedule_agent():
    """Lazy initialization of schedule agent"""
    global _schedule_agent
    if _schedule_agent is None:
        try:
            from core.schedule_agent import ScheduleAgent
            _schedule_agent = ScheduleAgent()
            logger.info("Schedule agent initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to initialize schedule agent: {e}")
            raise HTTPException(
                status_code=503,
                detail="AI scheduling service is currently unavailable. Please contact support."
            )
    return _schedule_agent


@router.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "hospital-scheduler-agent",
        "version": "1.0.0"
    }


@router.post("/schedule/generate")
async def generate_schedule(
    request: ScheduleQueryRequest,
    context: RequestContext = Depends(get_request_context)
):
    """
    Generate AI-powered hospital schedule
    
    This is the main endpoint that external applications will call.
    It requires a valid JWT token in the Authorization header and
    generates a comprehensive 2-week schedule based on hospital
    operating hours and employee availability.
    
    Args:
        request: Schedule generation parameters
        context: Authenticated request context (injected)
        
    Returns:
        Generated schedule with metadata and bulk update payload
    """
    try:
        # Fetch hospital operating hours
        hospital_tool = context.scheduling_tools["hospital_hours"]
        hospital_hours = hospital_tool.get_operating_hours(context.tenant_id, context.location_id)
        
        if not hospital_hours.get("success"):
            error_detail = hospital_hours.get("error", "Failed to fetch operating hours")
            raise HTTPException(status_code=502, detail=error_detail)

        # Fetch employee availability
        availability_tool = context.scheduling_tools.get("employee_availability")
        if availability_tool is None:
            raise HTTPException(status_code=500, detail="Employee availability tool is not configured")

        availability = availability_tool.search_availability(
            tenant_id=context.tenant_id,
            location_id=context.location_id,
            is_available=True,
            is_active=True
        )
        
        if not availability.get("success"):
            error_detail = availability.get("error", "Failed to fetch employee availability")
            raise HTTPException(status_code=502, detail=error_detail)

        # Generate schedule using AI agent
        agent = get_schedule_agent()
        result = agent.generate_schedule(
            tenant_id=context.tenant_id,
            location_id=context.location_id,
            hospital_hours=hospital_hours.get("operating_hours") or hospital_hours.get("data") or hospital_hours,
            employee_availability=availability.get("data") or {},
            user_query=request.query,
            use_ai=request.use_agent,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Add user context to response
        result["user_id"] = context.token_info.user_id
        
        logger.info("Schedule generated successfully", extra={
            'tenant_id': context.tenant_id,
            'location_id': context.location_id,
            'user_id': context.token_info.user_id,
            'use_ai': request.use_agent
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Schedule generation failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/hospital/hours")
async def get_hospital_hours(context: RequestContext = Depends(get_request_context)):
    """
    Get hospital operating hours via backend proxy
    
    Fetches operating hours for the authenticated tenant/location
    through the backend to avoid CORS issues in browser environments.
    """
    try:
        hospital_tool = context.scheduling_tools["hospital_hours"]
        result = hospital_tool.get_operating_hours(context.tenant_id, context.location_id)
        
        if not result.get("success"):
            error_detail = result.get("error", "Failed to fetch operating hours")
            raise HTTPException(status_code=502, detail=error_detail)
        
        return {
            "success": True,
            "tenant_id": context.tenant_id,
            "location_id": context.location_id,
            "operating_hours": result.get("operating_hours") or result.get("data") or result,
            "message": "Hospital operating hours fetched successfully"
        }
        
    except Exception as e:
        logger.error(f"Hospital hours fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hospital/availability")
async def get_employee_availability(context: RequestContext = Depends(get_request_context)):
    """
    Get employee availability via backend proxy
    
    Fetches employee availability for a 14-day window for the 
    authenticated tenant/location through the backend.
    """
    try:
        availability_tool = context.scheduling_tools.get("employee_availability")
        if availability_tool is None:
            raise HTTPException(status_code=500, detail="Employee availability tool is not configured")

        result = availability_tool.search_availability(
            tenant_id=context.tenant_id,
            location_id=context.location_id,
            is_available=True,
            is_active=True
        )
        
        if not result.get("success"):
            error_detail = result.get("error", "Failed to fetch employee availability")
            raise HTTPException(status_code=502, detail=error_detail)
        
        return {
            "success": True,
            "tenant_id": context.tenant_id,
            "location_id": context.location_id,
            "employee_availability": result.get("data") or result,
            "message": "Employee availability fetched successfully"
        }
        
    except Exception as e:
        logger.error(f"Employee availability fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/validate")
async def validate_context(context: RequestContext = Depends(get_request_context)):
    """
    Validate JWT token and return user context
    
    Used for testing authentication and extracting user/tenant context
    without performing any data operations.
    """
    return {
        "success": True,
        "user_id": context.token_info.user_id,
        "tenant_id": context.tenant_id,
        "location_id": context.location_id,
        "email": getattr(context.token_info, 'email', None),
        "message": "JWT token validated and context extracted successfully"
    }