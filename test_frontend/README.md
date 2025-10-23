# 🧪 Hospital Scheduler AI Agent - Test Frontend

A simple local testing interface for the Hospital Scheduler AI Agent.

## 🚀 Quick Start

1. **Start the API server:**
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Get a JWT token:**
   ```bash
   python get_token.py
   ```

3. **Open the test interface:**
   ```bash
   # Simply open in your browser:
   test_frontend/index.html
   ```
   Or use a local server:
   ```bash
   cd test_frontend
   python -m http.server 3000
   # Then visit: http://localhost:3000
   ```

## 🔄 Testing Workflow

The frontend guides you through the complete API testing process:

1. **🔍 Health Check** - Verify server is running
2. **🎫 JWT Token** - Paste your authentication token  
3. **🧩 Context Validation** - Test token authentication
4. **🏥 Hospital Hours** - Fetch operating hours data
5. **👥 Employee Availability** - Get staff availability  
6. **🤖 AI Schedule Generation** - Generate complete schedules

## 📋 Features

- **Sequential Testing**: Each step enables the next
- **Visual Feedback**: Success/error indicators with detailed responses
- **JSON Inspection**: All API responses displayed in readable format
- **Console Logging**: Full schedule payloads logged to browser console
- **Production Ready**: Tests the exact same endpoints your apps will use

## 🎯 Production API Endpoints

The frontend tests these production endpoints:
- `POST /api/v1/schedule/generate` - Main AI schedule generation
- `GET /api/v1/health` - Server health check
- `GET /api/v1/context/validate` - JWT validation
- `GET /api/v1/hospital/hours` - Hospital operating hours
- `GET /api/v1/hospital/availability` - Employee availability

## 🔑 Authentication

All endpoints require a valid JWT token in the `Authorization: Bearer <token>` header. Use `get_token.py` to obtain a test token.

---

**This is a local testing tool only. For production, your applications will call the API endpoints directly.**