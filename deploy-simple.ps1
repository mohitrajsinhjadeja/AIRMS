# 🚀 AIRMS Simple Deployment Script
# Universal AI Risk & Misinformation API - Quick Setup

param(
    [switch]$SkipTests = $false,
    [switch]$SkipFrontend = $false
)

Write-Host "🚀 AIRMS Universal AI Risk & Misinformation API Deployment" -ForegroundColor Cyan

function Write-Status {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Check prerequisites
Write-Host "🔍 Checking prerequisites..."

try {
    $pythonVersion = python --version 2>&1
    Write-Status "Python found: $pythonVersion"
} catch {
    Write-Error "Python not found. Please install Python 3.8+"
    exit 1
}

if (!$SkipFrontend) {
    try {
        $nodeVersion = node --version 2>&1
        Write-Status "Node.js found: $nodeVersion"
    } catch {
        Write-Error "Node.js not found. Please install Node.js 18+"
        exit 1
    }
}

# Setup backend
Write-Host "🔧 Setting up backend..."
Set-Location "backend"

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy model
Write-Host "Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file..."
    Copy-Item "../.env.template" ".env"
    Write-Host "⚠️ Please update backend/.env with your configuration" -ForegroundColor Yellow
}

Set-Location ".."

# Setup frontend
if (!$SkipFrontend) {
    Write-Host "🎨 Setting up frontend..."
    Set-Location "frontend"
    
    Write-Host "Installing Node.js dependencies..."
    npm install
    
    # Create .env.local file
    if (!(Test-Path ".env.local")) {
        Write-Host "Creating frontend .env.local file..."
        $envContent = "NEXT_PUBLIC_API_URL=http://localhost:8000`nNEXT_PUBLIC_APP_NAME=AIRMS`nNEXT_PUBLIC_APP_VERSION=1.0.0"
        $envContent | Out-File -FilePath ".env.local" -Encoding UTF8
    }
    
    Set-Location ".."
}

# Run tests
if (!$SkipTests) {
    Write-Host "🧪 Running basic tests..."
    Set-Location "backend"
    
    # Test imports
    python -c "import app.main; print('✅ Backend imports successful')"
    
    Set-Location ".."
}

# Start services
Write-Host "🚀 Starting services..."

# Start backend
Write-Host "Starting backend server..."
Set-Location "backend"
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -WindowStyle Hidden
Set-Location ".."

# Wait for backend to start
Write-Host "Waiting for backend to start..."
Start-Sleep -Seconds 10

# Test backend health
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    Write-Status "Backend health check passed: $($response.status)"
} catch {
    Write-Error "Backend health check failed. Check if the server started correctly."
}

# Start frontend
if (!$SkipFrontend) {
    Write-Host "Starting frontend server..."
    Set-Location "frontend"
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Hidden
    Set-Location ".."
    
    Write-Host "Waiting for frontend to start..."
    Start-Sleep -Seconds 15
}

# Show summary
Write-Host ""
Write-Host "🎉 AIRMS deployment completed!" -ForegroundColor Green
Write-Host "📊 Access Points:" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor White

if (!$SkipFrontend) {
    Write-Host "Frontend Dashboard: http://localhost:3000" -ForegroundColor White
}

Write-Host ""
Write-Host "🧪 Test the API:" -ForegroundColor Cyan
Write-Host 'curl -X POST "http://localhost:8000/api/v1/risk/analyze" -H "Content-Type: application/json" -d "{\"input\":\"Test content\",\"context\":{\"source\":\"test\"}}"' -ForegroundColor Gray

Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update environment variables in backend/.env" -ForegroundColor White
Write-Host "2. Configure your AI API keys (Groq, Gemini, etc.)" -ForegroundColor White
Write-Host "3. Set up your MongoDB connection" -ForegroundColor White
Write-Host "4. Test the system with: python test_complete_system.py" -ForegroundColor White

Write-Host ""
Write-Host "Press Ctrl+C to stop the servers..." -ForegroundColor Yellow

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host "Shutting down..." -ForegroundColor Yellow
}
