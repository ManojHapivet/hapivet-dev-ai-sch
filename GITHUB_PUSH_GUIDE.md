# 🚀 GitHub Push Instructions

## Prerequisites Setup

### 1. Install Git
1. Download Git from: https://git-scm.com/downloads
2. Install with default settings
3. Restart your terminal/command prompt

### 2. Verify Git Installation
```bash
git --version
```

## Repository Setup & Push

### Option A: Automated Script (Recommended)
```bash
cd C:\Users\manoj\scheduler
.\push_to_github.bat
```

### Option B: Manual Commands

#### Step 1: Initialize Repository
```bash
cd C:\Users\manoj\scheduler
git init
```

#### Step 2: Add Files
```bash
git add .
```

#### Step 3: Create Initial Commit
```bash
git commit -m "Initial commit: Azure Functions serverless hospital scheduler with AI schedule generation"
```

#### Step 4: Add Remote Repositories
```bash
# Primary repository (ManojHapivet)
git remote add origin https://github.com/ManojHapivet/SchedulerAgent.git

# Secondary repository (ssrikanths) 
git remote add hapivet-dev https://github.com/ssrikanths/havpivet-dev-ai-sch.git
```

#### Step 5: Push to Both Repositories
```bash
# Push to ManojHapivet/SchedulerAgent
git branch -M main
git push -u origin main

# Push to ssrikanths/havpivet-dev-ai-sch  
git push hapivet-dev main
```

## Authentication Setup

If you get authentication errors, set up a Personal Access Token:

1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens
2. Generate new token with `repo` permissions
3. Use token as password when prompted

Or configure Git credentials:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Repository Links

After successful push, your code will be available at:

1. **Primary**: https://github.com/ManojHapivet/SchedulerAgent
2. **Secondary**: https://github.com/ssrikanths/havpivet-dev-ai-sch

## What's Being Pushed

### Azure Functions Structure
```
📁 ScheduleGenerator/           # AI schedule generation function
📁 ValidateContext/            # JWT validation function  
📁 core/                       # Business logic
📁 services/                   # External integrations
📁 models/                     # Data models
📁 test_frontend/             # Development test interface
📄 host.json                  # Functions runtime config
📄 requirements.txt           # Python dependencies
📄 README.md                  # Project documentation
📄 .gitignore                 # Git ignore rules
```

### Key Features
- ⚡ Serverless Azure Functions architecture
- 🤖 OpenAI GPT-4o-mini integration for AI scheduling
- 🔐 JWT authentication with multi-tenant support
- 📅 Custom date range scheduling
- 🏥 Hospital management API integration
- 💰 Cost-effective pay-per-execution model

## Troubleshooting

### If Repository Already Exists
```bash
# Force push (use carefully)
git push --force origin main
git push --force hapivet-dev main
```

### If Authentication Fails
1. Use Personal Access Token instead of password
2. Or use SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### If Push Fails Due to Different Histories
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

## Next Steps After Push

1. ✅ Verify code is visible on both GitHub repositories
2. ✅ Set up Azure Functions deployment from GitHub
3. ✅ Configure environment variables in Azure
4. ✅ Test deployed functions
5. ✅ Share repository links with team members