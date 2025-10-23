"""
Request and Response Models for Hospital Scheduler API
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScheduleQueryRequest(BaseModel):
    """Request model for schedule generation"""
    query: Optional[str] = None
    use_agent: bool = True
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD


class LoginRequest(BaseModel):
    """Request model for authentication (legacy support)"""
    email: str
    password: str
    tenant_domain: Optional[str] = None
    location_id: Optional[str] = None


class QueryRequest(BaseModel):
    """Generic query request model"""
    tenant_id: Optional[str] = None
    location_id: Optional[str] = None
    tool_name: str = "hospital_hours"


class TenantLocationRequest(BaseModel):
    """Request model for tenant/location specific operations"""
    tenant_id: str
    location_id: str


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    authenticated: bool = False
    tools_loaded: bool = False


class ScheduleResponse(BaseModel):
    """Schedule generation response model"""
    success: bool
    tenant_id: str
    location_id: str
    schedule_window: dict
    bulk_update_payload: Optional[dict] = None
    generation_metadata: Optional[dict] = None
    error: Optional[str] = None