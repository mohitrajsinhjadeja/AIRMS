#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Deploy AIRMS application to Google Cloud Platform
.DESCRIPTION
    This script deploys the AIRMS application (frontend and backend) to GCP using Cloud Build and Cloud Run
.PARAMETER ProjectId
    The GCP Project ID
.PARAMETER Region
    The GCP region for deployment (default: us-central1)
.PARAMETER BuildConfig
    The Cloud Build configuration file to use (default: cloudbuild.yaml)
.PARAMETER Component
    Which component to deploy: 'all', 'frontend', or 'backend' (default: all)
.EXAMPLE
    .\deploy_gcp.ps1 -ProjectId "my-project-id"
.EXAMPLE
    .\deploy_gcp.ps1 -ProjectId "my-project-id" -Component "backend"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory = $false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory = $false)]
    [string]$BuildConfig = "cloudbuild.yaml",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet('all', 'frontend', 'backend')]
    [string]$Component = 'all'
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting AIRMS deployment to GCP..." -ForegroundColor Green
Write-Host "Project ID: $ProjectId" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan
Write-Host "Component: $Component" -ForegroundColor Cyan

# Check if gcloud is installed
try {
    $gcloudVersion = gcloud version --format="value(Google Cloud SDK)"
    Write-Host "✅ Google Cloud SDK found: $gcloudVersion" -ForegroundColor Green
} catch {
    Write-Error "❌ Google Cloud SDK not found. Please install gcloud CLI."
    exit 1
}

# Set the project
Write-Host "🔧 Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# Enable required APIs
Write-Host "🔧 Enabling required APIs..." -ForegroundColor Yellow
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "secretmanager.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "Enabling $api..." -ForegroundColor Gray
    gcloud services enable $api --quiet
}

# Create secrets if they don't exist (you'll need to set these values)
Write-Host "🔐 Checking secrets..." -ForegroundColor Yellow

$secrets = @(
    "mongodb-url",
    "gemini-api-key", 
    "jwt-secret"
)

foreach ($secret in $secrets) {
    $secretExists = gcloud secrets describe $secret --format="value(name)" 2>$null
    if (-not $secretExists) {
        Write-Host "Creating secret: $secret" -ForegroundColor Gray
        Write-Host "⚠️  Please set the value for $secret after deployment" -ForegroundColor Yellow
        echo "PLACEHOLDER_VALUE" | gcloud secrets create $secret --data-file=-
    }
}

# Deploy based on component selection
switch ($Component) {
    'all' {
        Write-Host "🏗️  Building and deploying both frontend and backend..." -ForegroundColor Yellow
        gcloud builds submit --config=$BuildConfig --substitutions=_REGION=$Region .
    }
    'frontend' {
        Write-Host "🏗️  Building and deploying frontend only..." -ForegroundColor Yellow
        Set-Location frontend
        gcloud builds submit --config=cloudbuild.yaml --substitutions=_REGION=$Region .
        Set-Location ..
    }
    'backend' {
        Write-Host "🏗️  Building and deploying backend only..." -ForegroundColor Yellow
        Set-Location backend
        gcloud builds submit --config=cloudbuild.yaml --substitutions=_REGION=$Region .
        Set-Location ..
    }
}

# Get service URLs
Write-Host "🌐 Retrieving service URLs..." -ForegroundColor Yellow

if ($Component -eq 'all' -or $Component -eq 'backend') {
    try {
        $backendUrl = gcloud run services describe airms-backend --region=$Region --format="value(status.url)" 2>$null
        if ($backendUrl) {
            Write-Host "✅ Backend deployed at: $backendUrl" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Backend URL not available yet" -ForegroundColor Yellow
    }
}

if ($Component -eq 'all' -or $Component -eq 'frontend') {
    try {
        $frontendUrl = gcloud run services describe airms-frontend --region=$Region --format="value(status.url)" 2>$null
        if ($frontendUrl) {
            Write-Host "✅ Frontend deployed at: $frontendUrl" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Frontend URL not available yet" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Update your secrets with actual values:" -ForegroundColor White
Write-Host "   - mongodb-url: Your MongoDB connection string" -ForegroundColor Gray
Write-Host "   - gemini-api-key: Your Google Gemini API key" -ForegroundColor Gray
Write-Host "   - jwt-secret: A secure JWT secret key" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Update secret values using:" -ForegroundColor White
Write-Host "   echo 'YOUR_ACTUAL_VALUE' | gcloud secrets versions add SECRET_NAME --data-file=-" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Redeploy services to pick up new secrets:" -ForegroundColor White
Write-Host "   gcloud run services update SERVICE_NAME --region=$Region" -ForegroundColor Gray
