#!/bin/bash
# Startup script for Azure App Service
# This tells Azure App Service how to start your FastAPI application

# Start the FastAPI application using uvicorn
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1