"""
Data Processing Utilities for Schedule Generation
Handles normalization, validation, and transformation of scheduling data
"""
import re
import json
from datetime import datetime
from typing import Any, Dict, List, Union


def format_timespan(value: Any) -> Any:
    """Format timespan values to standardized HH:MM:SS format"""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        hours = value.get('hours')
        minutes = value.get('minutes')
        seconds = value.get('seconds', 0)
        if hours is not None and minutes is not None:
            try:
                return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            except (ValueError, TypeError):
                pass
        ticks = value.get('ticks')
        if ticks is not None:
            try:
                total_seconds = int(ticks) / 10_000_000
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            except (ValueError, TypeError):
                return value
    return value


def normalize_timespans(payload: Any) -> Any:
    """Recursively normalize timespan objects in payload"""
    if isinstance(payload, dict):
        if {'hours', 'minutes'}.issubset(payload.keys()) or 'ticks' in payload:
            formatted = format_timespan(payload)
            if isinstance(formatted, str):
                return formatted
        return {key: normalize_timespans(val) for key, val in payload.items()}
    if isinstance(payload, list):
        return [normalize_timespans(item) for item in payload]
    return payload


def sanitize_timestring(value: Any) -> Any:
    """Sanitize and validate time string format"""
    formatted = format_timespan(value)
    if isinstance(formatted, str):
        cleaned = formatted.strip()
        if re.match(r'^\d{2}:\d{2}$', cleaned):
            cleaned = f"{cleaned}:00"
        if re.match(r'^\d{2}:\d{2}:\d{2}$', cleaned):
            return cleaned
        try:
            parsed = datetime.fromisoformat(cleaned.replace('Z', '+00:00'))
            return parsed.strftime('%H:%M:%S')
        except ValueError:
            return cleaned
    return formatted


def summarize_operating_hours(raw: Any) -> Any:
    """Extract and normalize hospital operating hours"""
    normalized = normalize_timespans(raw)
    if isinstance(normalized, dict):
        for candidate in (
            normalized.get('items'),
            normalized.get('operatingHours'),
            normalized.get('operating_hours'),
            normalized.get('data'),
        ):
            if isinstance(candidate, list):
                summary: List[Dict[str, Any]] = []
                for entry in candidate:
                    summary.append({
                        'dayOfWeek': entry.get('dayOfWeek'),
                        'isOpen': entry.get('isOpen'),
                        'notes': entry.get('notes'),
                        'timeSlots': [
                            {
                                'startTime': sanitize_timestring(slot.get('startTime')),
                                'endTime': sanitize_timestring(slot.get('endTime')),
                            }
                            for slot in (entry.get('timeSlots') or [])
                        ],
                    })
                return summary
    return normalized


def summarize_availability(raw: Dict[str, Any], max_entries: int = 12) -> List[Dict[str, Any]]:
    """Extract and normalize employee availability data"""
    normalized = normalize_timespans(raw or {})
    groups: List[Dict[str, Any]] = []
    for group in normalized.get('employeeGroups', []):
        entry = {
            'employeeId': group.get('employeeId'),
            'employeeName': group.get('employeeName'),
            'availabilityCount': group.get('availabilityCount'),
            'availabilities': [],
        }
        for availability in (group.get('availabilities') or [])[:max_entries]:
            entry['availabilities'].append({
                'availabilityId': availability.get('id'),
                'dayOfWeek': availability.get('dayOfWeek'),
                'minimumHours': availability.get('minimumHours'),
                'maximumHours': availability.get('maximumHours'),
                'isAvailable': availability.get('isAvailable'),
                'priority': availability.get('priority'),
                'isPreferredDay': availability.get('isPreferredDay'),
                'allowOverride': availability.get('allowOverride'),
                'effectiveStartDate': availability.get('effectiveStartDate'),
                'effectiveEndDate': availability.get('effectiveEndDate'),
                'isActive': availability.get('isActive'),
                'isApproved': availability.get('isApproved'),
                'timeSlots': [
                    {
                        'startTime': sanitize_timestring(slot.get('startTime')),
                        'endTime': sanitize_timestring(slot.get('endTime')),
                        'priority': slot.get('priority'),
                        'isPreferred': slot.get('isPreferred'),
                        'sortOrder': slot.get('sortOrder'),
                    }
                    for slot in (availability.get('timeSlots') or [])
                ],
                'notes': availability.get('notes'),
            })
        groups.append(entry)
    return groups


def sanitize_schedule_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize AI-generated schedule payload"""
    if not isinstance(payload, dict):
        raise ValueError('Schedule payload must be a JSON object')

    schedules = payload.get('employeeSchedules')
    if not isinstance(schedules, list) or not schedules:
        raise ValueError('employeeSchedules must be a non-empty list')

    for employee_entry in schedules:
        if 'employeeId' not in employee_entry:
            raise ValueError('Each employee schedule must include employeeId')
        employee_entry.setdefault('schedules', [])
        for schedule in employee_entry['schedules']:
            schedule.setdefault('isActive', True)
            schedule.setdefault('breaks', [])
            if 'id' not in schedule or schedule['id'] in ('', None):
                schedule['id'] = None

            work_date = schedule.get('workDate')
            if isinstance(work_date, datetime):
                schedule['workDate'] = work_date.isoformat()
            elif isinstance(work_date, str):
                cleaned = work_date.strip()
                try:
                    parsed = datetime.fromisoformat(cleaned.replace('Z', '+00:00'))
                    schedule['workDate'] = parsed.isoformat()
                except ValueError:
                    if re.match(r'^\d{4}-\d{2}-\d{2}$', cleaned):
                        schedule['workDate'] = f"{cleaned}T00:00:00Z"

            time_slots = schedule.get('timeSlots') or []
            sanitized_slots = []
            for slot in time_slots:
                sanitized_slots.append({
                    **{k: v for k, v in slot.items() if k not in {'startTime', 'endTime'}},
                    'startTime': sanitize_timestring(slot.get('startTime')),
                    'endTime': sanitize_timestring(slot.get('endTime')),
                })
            schedule['timeSlots'] = sanitized_slots

    payload.setdefault('validateOnly', False)
    return payload


def summarize_generated_schedule(payload: Dict[str, Any]) -> Dict[str, int]:
    """Generate summary statistics for a schedule payload"""
    employee_entries = payload.get('employeeSchedules', [])
    total_schedules = sum(len(entry.get('schedules', [])) for entry in employee_entries)
    total_slots = sum(
        len(schedule.get('timeSlots', []))
        for entry in employee_entries
        for schedule in entry.get('schedules', [])
    )
    return {
        'employee_count': len(employee_entries),
        'schedule_count': total_schedules,
        'time_slot_count': total_slots,
    }