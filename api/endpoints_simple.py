"""
Simplified API Endpoints - NO AUTH for initial deployment
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "hospital-scheduler-agent",
        "version": "1.0.0",
        "environment": os.environ.get("WEBSITE_SITE_NAME", "local")
    }


@router.post("/schedule/generate")
async def generate_schedule_endpoint():
    """
    Placeholder for schedule generation - AI not yet enabled
    """
    return {
        "success": False,
        "message": "AI scheduling service is being deployed. Please check back soon.",
        "status": "service_unavailable"
    }


@router.get("/hospital/hours")
async def get_hospital_hours():
    """Placeholder for hospital hours"""
    return {
        "success": False,
        "message": "Service being deployed",
        "status": "unavailable"
    }


@router.get("/hospital/availability")
async def get_employee_availability():
    """Placeholder for employee availability"""
    return {
        "success": False,
        "message": "Service being deployed",
        "status": "unavailable"
    }


@router.get("/context/validate")
async def validate_context():
    """Placeholder for context validation"""
    return {
        "success": True,
        "message": "Authentication will be enabled in next deployment phase",
        "status": "auth_pending"
    }
