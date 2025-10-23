# Quick redeploy script for Docker container
param(
    [string]$version = "latest"
)

$ErrorActionPreference = "Stop"

Write-Host "🐳 Redeploying HapiVet Scheduler AI (FULL VERSION with AI)..." -ForegroundColor Cyan
Write-Host ""

# Build new image
Write-Host "📦 Building Docker image..." -ForegroundColor Yellow
docker build -t hapivet-scheduler-ai:$version .
if ($LASTEXITCODE -ne 0) { throw "Docker build failed" }

# Tag for ACR
Write-Host "🏷️  Tagging image..." -ForegroundColor Yellow
docker tag hapivet-scheduler-ai:$version hapivetregistry7299.azurecr.io/hapivet-scheduler-ai:$version

# Login to ACR
Write-Host "🔐 Logging into Azure Container Registry..." -ForegroundColor Yellow
az acr login --name hapivetregistry7299
if ($LASTEXITCODE -ne 0) { throw "ACR login failed" }

# Push to ACR
Write-Host "⬆️  Pushing to Azure Container Registry..." -ForegroundColor Yellow
docker push hapivetregistry7299.azurecr.io/hapivet-scheduler-ai:$version
if ($LASTEXITCODE -ne 0) { throw "Docker push failed" }

# Update App Service
Write-Host "🔄 Updating App Service configuration..." -ForegroundColor Yellow
az webapp config container set `
  --name "dev-hv-sch-ai" `
  --resource-group "dev-hv-sch-ai_group" `
  --docker-custom-image-name "hapivetregistry7299.azurecr.io/hapivet-scheduler-ai:$version"
if ($LASTEXITCODE -ne 0) { throw "App Service update failed" }

# Restart
Write-Host "🔄 Restarting application..." -ForegroundColor Yellow
az webapp restart --name "dev-hv-sch-ai" --resource-group "dev-hv-sch-ai_group"
if ($LASTEXITCODE -ne 0) { throw "App restart failed" }

Write-Host ""
Write-Host "✅ Deployment complete! Waiting 30 seconds for container to start..." -ForegroundColor Green
Start-Sleep -Seconds 30

# Test
Write-Host "🧪 Testing deployment..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://dev-hv-sch-ai.azurewebsites.net/api/v1/health"
    Write-Host "✅ Health check PASSED!" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor Green
    Write-Host "   Service: $($response.service)" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Deployment successful! Application is running with FULL functionality." -ForegroundColor Green
    Write-Host "🌐 URL: https://dev-hv-sch-ai.azurewebsites.net" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Health check FAILED: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs with: az webapp log tail --name dev-hv-sch-ai --resource-group dev-hv-sch-ai_group" -ForegroundColor Yellow
}
