#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Deploy AIRMS application to Google Cloud Platform
.DESCRIPTION
    This script deploys the AIRMS application to GCP using Cloud Build and Cloud Run
.PARAMETER ProjectId
    The GCP Project ID (required)
.PARAMETER Region
    The GCP region for deployment (default: us-central1)
.PARAMETER SetupSecrets
    Create placeholder secrets if they don't exist (default: true)
.EXAMPLE
    .\deploy.ps1 -ProjectId "your-gcp-project-id"
.EXAMPLE
    .\deploy.ps1 -ProjectId "your-project" -Region "us-east1"
#>

param(
    [Parameter(Mandatory = $true, HelpMessage = "Enter your GCP Project ID")]
    [string]$ProjectId,
    
    [Parameter(Mandatory = $false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory = $false)]
    [bool]$SetupSecrets = $true
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "🚀 AIRMS - GCP Deployment Script"
Write-ColorOutput Cyan "=================================="
Write-ColorOutput White "Project ID: $ProjectId"
Write-ColorOutput White "Region: $Region"
Write-ColorOutput White ""

# Verify gcloud CLI is installed
Write-ColorOutput Yellow "🔍 Checking prerequisites..."
try {
    $gcloudVersion = (gcloud version --format="value(Google Cloud SDK)" 2>$null)
    Write-ColorOutput Green "✅ Google Cloud SDK: $gcloudVersion"
} catch {
    Write-ColorOutput Red "❌ Google Cloud SDK not found!"
    Write-ColorOutput White "Please install gcloud CLI: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Set project and authenticate
Write-ColorOutput Yellow "🔧 Configuring GCP project..."
try {
    gcloud config set project $ProjectId --quiet
    Write-ColorOutput Green "✅ Project set to: $ProjectId"
} catch {
    Write-ColorOutput Red "❌ Failed to set project. Please check your project ID and permissions."
    exit 1
}

# Enable required APIs
Write-ColorOutput Yellow "🔧 Enabling required APIs..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com", 
    "containerregistry.googleapis.com",
    "secretmanager.googleapis.com"
)

foreach ($api in $apis) {
    Write-ColorOutput Gray "  Enabling $api..."
    try {
        gcloud services enable $api --quiet
    } catch {
        Write-ColorOutput Red "❌ Failed to enable $api"
        exit 1
    }
}
Write-ColorOutput Green "✅ APIs enabled successfully"

# Create secrets if needed
if ($SetupSecrets) {
    Write-ColorOutput Yellow "🔐 Setting up secrets..."
    
    $secrets = @{
        "mongodb-url" = "mongodb+srv://username:password@cluster.mongodb.net/airms?retryWrites=true&w=majority"
        "gemini-api-key" = "your-gemini-api-key-here"
        "jwt-secret" = "your-super-secret-jwt-key-here-make-it-long-and-random"
    }
    
    foreach ($secretName in $secrets.Keys) {
        try {
            $existing = gcloud secrets describe $secretName --format="value(name)" 2>$null
            if (-not $existing) {
                Write-ColorOutput Gray "  Creating secret: $secretName"
                echo $secrets[$secretName] | gcloud secrets create $secretName --data-file=- --quiet
                Write-ColorOutput Yellow "  ⚠️  Remember to update $secretName with your actual value!"
            } else {
                Write-ColorOutput Gray "  Secret $secretName already exists"
            }
        } catch {
            Write-ColorOutput Red "❌ Failed to create secret: $secretName"
        }
    }
}

# Create service account for Cloud Run
Write-ColorOutput Yellow "👤 Setting up service account..."
$serviceAccountName = "cloudrun-service-account"
$serviceAccountEmail = "$serviceAccountName@$ProjectId.iam.gserviceaccount.com"

try {
    $existing = gcloud iam service-accounts describe $serviceAccountEmail --format="value(email)" 2>$null
    if (-not $existing) {
        gcloud iam service-accounts create $serviceAccountName --display-name="Cloud Run Service Account" --quiet
        
        # Grant necessary permissions
        $roles = @(
            "roles/secretmanager.secretAccessor",
            "roles/cloudsql.client"
        )
        
        foreach ($role in $roles) {
            gcloud projects add-iam-policy-binding $ProjectId --member="serviceAccount:$serviceAccountEmail" --role="$role" --quiet
        }
        Write-ColorOutput Green "✅ Service account created and configured"
    } else {
        Write-ColorOutput Gray "Service account already exists"
    }
} catch {
    Write-ColorOutput Yellow "⚠️  Service account setup failed, but continuing..."
}

# Start deployment
Write-ColorOutput Yellow "🚀 Starting deployment..."
Write-ColorOutput White "This will:"
Write-ColorOutput White "  1. Build Docker images for frontend and backend"
Write-ColorOutput White "  2. Push images to Google Container Registry"
Write-ColorOutput White "  3. Deploy to Cloud Run services"
Write-ColorOutput White ""

$confirmation = Read-Host "Continue with deployment? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-ColorOutput Yellow "Deployment cancelled by user"
    exit 0
}

# Run the build
Write-ColorOutput Yellow "🏗️  Running Cloud Build..."
try {
    gcloud builds submit --config=cloudbuild.yaml --substitutions="_REGION=$Region" --timeout=1800s .
    Write-ColorOutput Green "✅ Build completed successfully!"
} catch {
    Write-ColorOutput Red "❌ Build failed!"
    Write-ColorOutput White "Check the build logs above for details."
    exit 1
}

# Get deployment URLs
Write-ColorOutput Yellow "🌐 Retrieving service URLs..."

Start-Sleep -Seconds 10  # Wait for services to be ready

try {
    $backendUrl = gcloud run services describe airms-backend --region=$Region --format="value(status.url)" 2>$null
    $frontendUrl = gcloud run services describe airms-frontend --region=$Region --format="value(status.url)" 2>$null
    
    Write-ColorOutput Green "🎉 Deployment completed successfully!"
    Write-ColorOutput White ""
    Write-ColorOutput Cyan "📡 Service URLs:"
    if ($backendUrl) {
        Write-ColorOutput White "  Backend:  $backendUrl"
    }
    if ($frontendUrl) {
        Write-ColorOutput White "  Frontend: $frontendUrl"
    }
    
} catch {
    Write-ColorOutput Yellow "⚠️  Could not retrieve service URLs immediately"
    Write-ColorOutput White "You can get them later using:"
    Write-ColorOutput Gray "  gcloud run services list --region=$Region"
}

Write-ColorOutput White ""
Write-ColorOutput Cyan "📋 Post-deployment checklist:"
Write-ColorOutput White "1. Update secrets with your actual values:"
Write-ColorOutput Gray "   gcloud secrets versions add mongodb-url --data-file=-"
Write-ColorOutput Gray "   gcloud secrets versions add gemini-api-key --data-file=-"
Write-ColorOutput Gray "   gcloud secrets versions add jwt-secret --data-file=-"
Write-ColorOutput White ""
Write-ColorOutput White "2. Test your endpoints:"
Write-ColorOutput Gray "   curl \$BACKEND_URL/health"
Write-ColorOutput White ""
Write-ColorOutput White "3. Monitor your services:"
Write-ColorOutput Gray "   gcloud run services list --region=$Region"
Write-ColorOutput White ""
Write-ColorOutput Green "Happy deploying! 🚀"