#!/usr/bin/env python3
"""
Test Azure Functions locally
"""
import json
import requests
import os

# Azure Functions local development URL
FUNCTIONS_BASE_URL = "http://localhost:7071/api"

def test_validate_context():
    """Test JWT validation function"""
    print("Testing ValidateContext function...")
    
    # Use a test JWT token (replace with actual token)
    jwt_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    try:
        response = requests.get(
            f"{FUNCTIONS_BASE_URL}/ValidateContext",
            headers={
                "Authorization": jwt_token,
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_schedule_generator():
    """Test schedule generation function"""
    print("\nTesting ScheduleGenerator function...")
    
    payload = {
        "jwt_token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "query": "Create a simple 3-day schedule for testing",
        "use_agent": True,
        "start_date": "2025-10-08",
        "end_date": "2025-10-10"
    }
    
    try:
        response = requests.post(
            f"{FUNCTIONS_BASE_URL}/ScheduleGenerator",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # AI generation may take longer
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get("success"):
            print("✅ Schedule generation successful!")
            print(f"Generated schedules: {len(result.get('bulk_update_payload', {}).get('employeeSchedules', []))}")
        else:
            print(f"❌ Error: {result.get('error')}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run Azure Functions tests"""
    print("🧪 Testing Azure Functions Locally")
    print("=" * 50)
    print("Make sure to start functions with: func start")
    print("=" * 50)
    
    test_validate_context()
    test_schedule_generator()

if __name__ == "__main__":
    main()