# Hospital Scheduler - Azure Functions Deployment

## 🚀 Azure Functions Architecture

This project has been restructured for **serverless deployment** using Azure Functions. The monolithic FastAPI server has been replaced with event-driven functions.

### 📁 Project Structure
```
scheduler/
├── ScheduleGenerator/           # Main AI schedule generation function
│   ├── __init__.py             # Function handler
│   └── function.json           # Function configuration
├── ValidateContext/            # JWT validation function  
│   ├── __init__.py             # Function handler
│   └── function.json           # Function configuration
├── core/                       # Business logic (shared)
├── services/                   # External integrations (shared)
├── models/                     # Data models (shared)
├── host.json                   # Functions runtime config
├── local.settings.json         # Local development settings
└── requirements.txt            # Azure Functions dependencies
```

### 🔧 Azure Functions

#### 1. **ScheduleGenerator** 
- **Trigger**: HTTP POST
- **Purpose**: AI-powered schedule generation
- **Endpoint**: `/api/ScheduleGenerator`
- **Payload**:
```json
{
  "jwt_token": "Bearer eyJ...",
  "query": "Create a comprehensive schedule",
  "use_agent": true,
  "start_date": "2025-10-08",
  "end_date": "2025-10-22"
}
```

#### 2. **ValidateContext**
- **Trigger**: HTTP GET/POST  
- **Purpose**: JWT validation and context extraction
- **Endpoint**: `/api/ValidateContext`
- **Headers**: `Authorization: Bearer <jwt_token>`

### 🚀 Deployment Steps

#### Prerequisites
- Azure CLI installed
- Azure Functions Core Tools installed
- Python 3.9+ 

#### 1. **Initialize Azure Functions Project**
```bash
cd scheduler
func init --python
```

#### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

#### 3. **Local Testing**
```bash
func start
```

#### 4. **Deploy to Azure**
```bash
# Create resource group
az group create --name hospital-scheduler --location eastus

# Create storage account
az storage account create --name schedulerstorage --location eastus --resource-group hospital-scheduler --sku Standard_LRS

# Create function app
az functionapp create --resource-group hospital-scheduler --consumption-plan-location eastus --runtime python --runtime-version 3.9 --functions-version 4 --name hospital-scheduler-functions --storage-account schedulerstorage

# Deploy functions
func azure functionapp publish hospital-scheduler-functions
```

#### 5. **Configure Application Settings**
```bash
az functionapp config appsettings set --name hospital-scheduler-functions --resource-group hospital-scheduler --settings OPENAI_API_KEY="your-openai-key"
az functionapp config appsettings set --name hospital-scheduler-functions --resource-group hospital-scheduler --settings AUTH_BASE_URL="https://dev-hv-auth.azurewebsites.net"
az functionapp config appsettings set --name hospital-scheduler-functions --resource-group hospital-scheduler --settings SCHEDULER_BASE_URL="https://dev-hapivet-sch.azurewebsites.net"
```

### 📊 Benefits of Serverless Architecture

- ✅ **Cost Effective**: Pay only for execution time
- ✅ **Auto Scaling**: Handles traffic spikes automatically  
- ✅ **Zero Server Management**: No infrastructure to maintain
- ✅ **Event Driven**: Perfect for on-demand schedule generation
- ✅ **High Availability**: Built-in redundancy and failover

### 🔗 Function Endpoints

After deployment, functions will be available at:
- `https://hospital-scheduler-functions.azurewebsites.net/api/ScheduleGenerator`
- `https://hospital-scheduler-functions.azurewebsites.net/api/ValidateContext`

### 🧪 Testing Functions

Use the same JWT token and payload format as before, but call the Azure Functions endpoints instead of the local server.

### 📝 Notes

- Each function is **stateless** and **independent**
- **Shared modules** (core/, services/, models/) are imported by each function
- **OpenAI API key** is configured via environment variables
- **Cold starts** may add 1-2 seconds for the first request
- Functions have a **10-minute timeout** (configurable in host.json)