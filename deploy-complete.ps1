# 🚀 AIRMS Complete Deployment Script
# Universal AI Risk & Misinformation API - Full System Deployment

param(
    [string]$Environment = "development",
    [string]$Platform = "local", # local, docker, gcp, aws
    [switch]$SkipTests = $false,
    [switch]$SkipFrontend = $false,
    [switch]$Verbose = $false
)

Write-Host "🚀 AIRMS Universal AI Risk & Misinformation API Deployment" -ForegroundColor Cyan
Write-Host "Environment: $Environment | Platform: $Platform" -ForegroundColor Yellow

# Configuration
$BackendPath = ".\backend"
$FrontendPath = ".\frontend"
$LogFile = "deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Write-Log {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-Prerequisites {
    Write-Log "🔍 Checking prerequisites..." "INFO"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "✅ Python found: $pythonVersion" "INFO"
    } catch {
        Write-Log "❌ Python not found. Please install Python 3.8+" "ERROR"
        exit 1
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>&1
        Write-Log "✅ Node.js found: $nodeVersion" "INFO"
    } catch {
        Write-Log "❌ Node.js not found. Please install Node.js 18+" "ERROR"
        exit 1
    }
    
    # Check Docker (if needed)
    if ($Platform -eq "docker") {
        try {
            $dockerVersion = docker --version 2>&1
            Write-Log "✅ Docker found: $dockerVersion" "INFO"
        } catch {
            Write-Log "❌ Docker not found. Please install Docker" "ERROR"
            exit 1
        }
    }
}

function Setup-Backend {
    Write-Log "🔧 Setting up backend..." "INFO"
    
    Set-Location $BackendPath
    
    # Create virtual environment
    if (!(Test-Path "venv")) {
        Write-Log "Creating Python virtual environment..." "INFO"
        python -m venv venv
    }
    
    # Activate virtual environment
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        .\venv\Scripts\Activate.ps1
    } else {
        source venv/bin/activate
    }
    
    # Install dependencies
    Write-Log "Installing Python dependencies..." "INFO"
    pip install -r requirements.txt
    
    # Download spaCy model
    Write-Log "Downloading spaCy model..." "INFO"
    python -m spacy download en_core_web_sm
    
    # Setup database
    Write-Log "Setting up database..." "INFO"
    python scripts/setup_database.py
    
    Set-Location ..
}

function Setup-Frontend {
    if ($SkipFrontend) {
        Write-Log "⏭️ Skipping frontend setup" "INFO"
        return
    }
    
    Write-Log "🎨 Setting up frontend..." "INFO"
    
    Set-Location $FrontendPath
    
    # Install dependencies
    Write-Log "Installing Node.js dependencies..." "INFO"
    npm install
    
    # Build frontend
    Write-Log "Building frontend..." "INFO"
    npm run build
    
    Set-Location ..
}

function Run-Tests {
    if ($SkipTests) {
        Write-Log "⏭️ Skipping tests" "INFO"
        return
    }
    
    Write-Log "🧪 Running comprehensive test suite..." "INFO"
    
    Set-Location $BackendPath
    
    # Run unit tests
    Write-Log "Running unit tests..." "INFO"
    python -m pytest tests/test_comprehensive_suite.py::TestUniversalAPI::test_pii_detection_module -v
    
    # Run integration tests
    Write-Log "Running integration tests..." "INFO"
    python -m pytest tests/test_comprehensive_suite.py::TestUniversalAPI::test_risk_pipeline_integration -v
    
    # Run API tests
    Write-Log "Running API tests..." "INFO"
    python -m pytest tests/test_comprehensive_suite.py::TestUniversalAPI::test_api_json_structure_validation -v
    
    # Run performance tests
    Write-Log "Running performance tests..." "INFO"
    python -m pytest tests/test_comprehensive_suite.py::TestUniversalAPI::test_concurrent_request_handling -v
    
    Set-Location ..
}

function Deploy-Local {
    Write-Log "🏠 Deploying locally..." "INFO"
    
    # Start backend
    Write-Log "Starting backend server..." "INFO"
    Set-Location $BackendPath
    Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -NoNewWindow
    
    # Wait for backend to start
    Start-Sleep -Seconds 5
    
    # Test backend health
    try {
        $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        Write-Log "✅ Backend health check passed: $($healthCheck.status)" "INFO"
    } catch {
        Write-Log "❌ Backend health check failed" "ERROR"
    }
    
    Set-Location ..
    
    if (!$SkipFrontend) {
        # Start frontend
        Write-Log "Starting frontend server..." "INFO"
        Set-Location $FrontendPath
        Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow
        Set-Location ..
        
        # Wait for frontend to start
        Start-Sleep -Seconds 10
        
        Write-Log "🎉 AIRMS deployed successfully!" "INFO"
        Write-Log "Backend: http://localhost:8000" "INFO"
        Write-Log "Frontend: http://localhost:3000" "INFO"
        Write-Log "API Docs: http://localhost:8000/docs" "INFO"
    }
}

function Deploy-Docker {
    Write-Log "🐳 Deploying with Docker..." "INFO"
    
    # Build and start services
    Write-Log "Building Docker containers..." "INFO"
    docker-compose build
    
    Write-Log "Starting Docker services..." "INFO"
    docker-compose up -d
    
    # Wait for services to start
    Start-Sleep -Seconds 30
    
    # Test health
    try {
        $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        Write-Log "✅ Docker deployment health check passed: $($healthCheck.status)" "INFO"
    } catch {
        Write-Log "❌ Docker deployment health check failed" "ERROR"
    }
    
    Write-Log "🎉 AIRMS deployed successfully with Docker!" "INFO"
    Write-Log "Backend: http://localhost:8000" "INFO"
    Write-Log "Frontend: http://localhost:3000" "INFO"
    Write-Log "API Docs: http://localhost:8000/docs" "INFO"
}

function Deploy-GCP {
    Write-Log "☁️ Deploying to Google Cloud Platform..." "INFO"
    
    # Check gcloud CLI
    try {
        $gcloudVersion = gcloud version 2>&1
        Write-Log "✅ gcloud CLI found" "INFO"
    } catch {
        Write-Log "❌ gcloud CLI not found. Please install Google Cloud SDK" "ERROR"
        exit 1
    }
    
    # Deploy backend
    Write-Log "Deploying backend to Google Cloud Run..." "INFO"
    Set-Location $BackendPath
    gcloud run deploy airms-backend --source . --platform managed --region us-central1 --allow-unauthenticated
    Set-Location ..
    
    if (!$SkipFrontend) {
        # Deploy frontend
        Write-Log "Deploying frontend to Google Cloud Run..." "INFO"
        Set-Location $FrontendPath
        gcloud run deploy airms-frontend --source . --platform managed --region us-central1 --allow-unauthenticated
        Set-Location ..
    }
    
    Write-Log "🎉 AIRMS deployed successfully to GCP!" "INFO"
}

function Create-EnvironmentFile {
    Write-Log "📝 Creating environment configuration..." "INFO"
    
    if (!(Test-Path "$BackendPath\.env")) {
        Write-Log "Creating backend .env file..." "INFO"
        Copy-Item ".env.template" "$BackendPath\.env"
        Write-Log "⚠️ Please update $BackendPath\.env with your configuration" "WARNING"
    }
    
    if (!(Test-Path "$FrontendPath\.env.local") -and !$SkipFrontend) {
        Write-Log "Creating frontend .env.local file..." "INFO"
        $envContent = @"
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AIRMS
NEXT_PUBLIC_APP_VERSION=1.0.0
"@
        $envContent | Out-File -FilePath "$FrontendPath\.env.local" -Encoding UTF8
    }
}

function Show-DeploymentSummary {
    Write-Log "📊 Deployment Summary" "INFO"
    Write-Log "===================" "INFO"
    Write-Log "Environment: $Environment" "INFO"
    Write-Log "Platform: $Platform" "INFO"
    Write-Log "Backend Path: $BackendPath" "INFO"
    if (!$SkipFrontend) {
        Write-Log "Frontend Path: $FrontendPath" "INFO"
    }
    Write-Log "Log File: $LogFile" "INFO"
    Write-Log "" "INFO"
    
    Write-Log "🔗 Access Points:" "INFO"
    Write-Log "Backend API: http://localhost:8000" "INFO"
    Write-Log "API Documentation: http://localhost:8000/docs" "INFO"
    Write-Log "Health Check: http://localhost:8000/health" "INFO"
    if (!$SkipFrontend) {
        Write-Log "Frontend Dashboard: http://localhost:3000" "INFO"
    }
    Write-Log "" "INFO"
    
    Write-Log "🧪 Test the API:" "INFO"
    Write-Log 'curl -X POST "http://localhost:8000/api/v1/risk/analyze" -H "Content-Type: application/json" -d "{\"input\":\"Test content\",\"context\":{\"source\":\"test\"}}"' "INFO"
    Write-Log "" "INFO"
    
    Write-Log "📚 Next Steps:" "INFO"
    Write-Log "1. Update environment variables in .env files" "INFO"
    Write-Log "2. Configure your AI API keys (Groq, Gemini, etc.)" "INFO"
    Write-Log "3. Set up your MongoDB connection" "INFO"
    Write-Log "4. Run the comprehensive test suite" "INFO"
    Write-Log "5. Monitor performance at /api/v1/analytics/real-time-metrics" "INFO"
}

# Main deployment flow
try {
    Write-Log "🚀 Starting AIRMS deployment process..." "INFO"
    
    Test-Prerequisites
    Create-EnvironmentFile
    Setup-Backend
    Setup-Frontend
    Run-Tests
    
    switch ($Platform) {
        "local" { Deploy-Local }
        "docker" { Deploy-Docker }
        "gcp" { Deploy-GCP }
        default { 
            Write-Log "❌ Unknown platform: $Platform" "ERROR"
            exit 1
        }
    }
    
    Show-DeploymentSummary
    
    Write-Log "🎉 AIRMS deployment completed successfully!" "SUCCESS"
    
} catch {
    Write-Log "❌ Deployment failed: $($_.Exception.Message)" "ERROR"
    Write-Log "Check the log file for details: $LogFile" "ERROR"
    exit 1
}

# Keep the script running for local deployment
if ($Platform -eq "local") {
    Write-Log "Press Ctrl+C to stop the servers..." "INFO"
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } catch {
        Write-Log "Shutting down servers..." "INFO"
    }
}
