"""
AI Agent for Schedule Generation
Handles the core AI logic for generating hospital schedules
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, timedelta
from textwrap import dedent
import json
import re
import logging
from typing import Dict, Any, List

from config import OPENAI_CONFIG
from .data_processors import (
    normalize_timespans, 
    summarize_operating_hours, 
    summarize_availability,
    sanitize_schedule_payload,
    summarize_generated_schedule
)

logger = logging.getLogger(__name__)

# AI Agent Configuration
SCHEDULE_SYSTEM_PROMPT = (
    'You are an expert veterinary hospital workforce scheduler. Plan coverage for all operating hours while '
    'respecting employee availability, distributing workload fairly, and highlighting any assumptions in '
    'schedule descriptions if necessary. Return only the requested JSON payload.'
)

DEFAULT_SCHEDULE_INSTRUCTIONS = (
    'Create a balanced two-week staffing plan covering all hospital operating hours, ensuring veterinarian, '
    'technician, and support teams have appropriate coverage. Respect published availability, avoid overtime '
    'conflicts, and call out any assumptions or gaps that cannot be resolved with current staffing.'
)

SCHEDULE_SCHEMA_GUIDANCE = (
    'an object with `employeeSchedules` (array) and `validateOnly` (boolean). Each employee schedule must '
    'list `employeeId` and an array `schedules`. Each schedule entry requires `id` (use null for new shifts), '
    '`title`, `workDate` (ISO 8601), and `timeSlots` (each with `startTime` and `endTime` in HH:MM:SS). '
    'Optional fields include `description`, `isActive`, `breaks`, and per-slot metadata.'
)

SCHEDULE_HUMAN_PROMPT = dedent("""
Generate a two-week schedule for tenant {tenant_id} at location {location_id} covering {start_date} through {end_date}.
Instructions: {user_query}.

Operating hours JSON:
```json
{operating_hours_json}
```

Employee availability JSON (day-level availability with constraints):
```json
{availability_json}
```

IMPORTANT SCHEDULING RULES:
1. Each employee's availability is defined per day-of-week (1=Monday, 2=Tuesday, etc.)
2. Respect dayOfWeek constraints - only schedule employees on days they're available
3. Honor time slot boundaries (e.g., 09:00:00-17:00:00) for each day
4. Consider minimumHours/maximumHours per day (e.g., 8-10 hours)
5. Prioritize isPreferredDay=true and higher priority values
6. Only use approved availabilities (isApproved=true) unless allowOverride=true
7. Schedule within effectiveStartDate/effectiveEndDate ranges

Respond with JSON that matches {schema_guidance}.
""").strip()

SCHEDULE_PROMPT = ChatPromptTemplate.from_messages([
    ('system', SCHEDULE_SYSTEM_PROMPT),
    ('human', SCHEDULE_HUMAN_PROMPT),
])


class ScheduleAgent:
    """AI Agent for generating hospital schedules"""
    
    def __init__(self):
        """Initialize the AI agent with OpenAI LLM"""
        self.llm = ChatOpenAI(
            model=OPENAI_CONFIG["model"],
            temperature=OPENAI_CONFIG["temperature"],
            openai_api_key=OPENAI_CONFIG["api_key"]
        )
    
    def generate_schedule(
        self,
        tenant_id: str,
        location_id: str,
        hospital_hours: Dict[str, Any],
        employee_availability: Dict[str, Any],
        user_query: str = None,
        use_ai: bool = True,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive schedule for specified date range
        
        Args:
            tenant_id: Tenant identifier
            location_id: Hospital location identifier
            hospital_hours: Operating hours data
            employee_availability: Staff availability data
            user_query: Custom scheduling instructions
            use_ai: Whether to use AI generation or return context only
            start_date: Schedule start date (YYYY-MM-DD format, optional)
            end_date: Schedule end date (YYYY-MM-DD format, optional)
            
        Returns:
            Dict containing schedule or context data
        """
        # Set up schedule window - use provided dates or default to 14 days
        if start_date:
            try:
                schedule_start = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                logger.warning(f"Invalid start_date format: {start_date}, using default")
                schedule_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            schedule_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if end_date:
            try:
                schedule_end = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59, microsecond=0) + timedelta(days=1)
            except ValueError:
                logger.warning(f"Invalid end_date format: {end_date}, using default")
                schedule_end = schedule_start + timedelta(days=14)
        else:
            schedule_end = schedule_start + timedelta(days=14)
        
        # Process and normalize data
        operating_hours_summary = summarize_operating_hours(hospital_hours)
        availability_summary = summarize_availability(employee_availability)
        
        # Calculate metadata
        operating_days = 0
        if isinstance(operating_hours_summary, list):
            operating_days = len([h for h in operating_hours_summary if isinstance(h, dict) and h.get("isOpen")])
        elif isinstance(operating_hours_summary, dict):
            operating_days = 1 if operating_hours_summary.get("isOpen") else 0
        
        base_response = {
            "success": True,
            "tenant_id": tenant_id,
            "location_id": location_id,
            "schedule_window": {
                "startDate": schedule_start.date().isoformat(),
                "endDate": (schedule_end - timedelta(days=1)).date().isoformat()
            },
            "operating_hours": operating_hours_summary,
            "employee_availability": availability_summary if isinstance(availability_summary, list) else [],
            "generation_metadata": {
                "employee_count": len(availability_summary) if isinstance(availability_summary, list) else 0,
                "operating_days": operating_days
            }
        }
        
        # If AI generation is disabled, return context only
        if not use_ai:
            base_response["mode"] = "context_only"
            return base_response
        
        # Generate AI schedule
        try:
            user_instructions = user_query or DEFAULT_SCHEDULE_INSTRUCTIONS
            
            # Create AI prompt
            messages = SCHEDULE_PROMPT.format_messages(
                tenant_id=tenant_id,
                location_id=location_id,
                start_date=schedule_start.date().isoformat(),
                end_date=(schedule_end - timedelta(days=1)).date().isoformat(),
                user_query=user_instructions,
                operating_hours_json=json.dumps(operating_hours_summary, indent=2),
                availability_json=json.dumps(availability_summary, indent=2),
                schema_guidance=SCHEDULE_SCHEMA_GUIDANCE
            )
            
            # Invoke AI agent
            llm_result = self.llm.invoke(messages)
            raw_content = getattr(llm_result, "content", str(llm_result))
            logger.info(f"Raw AI response: {raw_content[:500]}...")  # Log first 500 chars
            
            # Process AI response
            parsed_payload = self._extract_json_object(raw_content)
            logger.info(f"Extracted payload keys: {list(parsed_payload.keys()) if parsed_payload else 'None'}")
            
            if parsed_payload:
                emp_schedules = parsed_payload.get('employeeSchedules', [])
                logger.info(f"Employee schedules found: {len(emp_schedules) if isinstance(emp_schedules, list) else 'Not a list'}")
            
            sanitized_payload = sanitize_schedule_payload(parsed_payload)
            schedule_meta = summarize_generated_schedule(sanitized_payload)
            
            logger.info("AI schedule generated successfully", extra={
                'tenant_id': tenant_id,
                'location_id': location_id,
                'employee_count': schedule_meta.get('employee_count'),
                'schedule_count': schedule_meta.get('schedule_count')
            })
            
            # Add AI-generated data to response
            base_response.update({
                "instructions_used": user_instructions,
                "bulk_update_payload": sanitized_payload,
                "generation_metadata": schedule_meta,
                "raw_agent_output": raw_content
            })
            
            return base_response
            
        except Exception as exc:
            logger.error(f"AI schedule generation failed: {exc}")
            raise Exception(f"Schedule generation failed: {str(exc)}")
    
    def _extract_json_object(self, text: str) -> Dict[str, Any]:
        """Extract JSON object from AI response text, handling markdown code blocks"""
        logger.info(f"Extracting JSON from text: {text[:200]}...")
        
        # First, try direct JSON parsing
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Try extracting from markdown code blocks
        code_block_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # ```json ... ```
            r'```\s*(\{.*?\})\s*```',      # ``` ... ```
            r'`(\{.*?\})`',                # `{...}`
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    candidate = match.group(1).strip()
                    logger.info(f"Found JSON candidate in code block: {candidate[:100]}...")
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue
        
        # Fallback: extract any JSON-like object
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                candidate = match.group(0).strip()
                logger.info(f"Found JSON candidate from regex: {candidate[:100]}...")
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        logger.error(f"Could not extract valid JSON from text: {text}")
        raise ValueError('Generated content was not valid JSON')