param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory = $false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("all", "frontend", "backend")]
    [string]$Component = "all",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

# Colors
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red
$Blue = [System.ConsoleColor]::Blue

function Write-ColoredOutput {
    param([string]$Message, [System.ConsoleColor]$Color = [System.ConsoleColor]::White)
    Write-Host $Message -ForegroundColor $Color
}

function Test-GCloudAuth {
    Write-ColoredOutput "Checking Google Cloud authentication..." $Blue
    try {
        $authResult = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
        if ([string]::IsNullOrEmpty($authResult)) {
            Write-ColoredOutput "ERROR: Not authenticated. Run: gcloud auth login" $Red
            exit 1
        }
        Write-ColoredOutput "SUCCESS: Authenticated as: $authResult" $Green
        return $true
    }
    catch {
        Write-ColoredOutput "ERROR: Authentication check failed: $_" $Red
        return $false
    }
}

function Test-GCloudProject {
    param([string]$ProjectId)
    Write-ColoredOutput "Verifying project access..." $Blue
    try {
        $project = gcloud projects describe $ProjectId --format="value(projectId)" 2>$null
        if ([string]::IsNullOrEmpty($project)) {
            Write-ColoredOutput "ERROR: Cannot access project '$ProjectId'" $Red
            exit 1
        }
        Write-ColoredOutput "SUCCESS: Project verified: $ProjectId" $Green
        gcloud config set project $ProjectId
        return $true
    }
    catch {
        Write-ColoredOutput "ERROR: Project verification failed: $_" $Red
        return $false
    }
}

function Enable-RequiredAPIs {
    param([string]$ProjectId)
    Write-ColoredOutput "Enabling required APIs..." $Blue
    $apis = @("cloudbuild.googleapis.com", "run.googleapis.com", "containerregistry.googleapis.com")
    foreach ($api in $apis) {
        Write-ColoredOutput "  Enabling $api..." $Yellow
        try { gcloud services enable $api --project=$ProjectId } catch { }
    }
    Write-ColoredOutput "SUCCESS: APIs enabled" $Green
}

function Deploy-Component {
    param([string]$ComponentName, [string]$ComponentPath, [string]$ProjectId, [string]$Region, [string]$Environment)
    Write-ColoredOutput "Deploying $ComponentName..." $Blue
    try {
        $cloudBuildFile = Join-Path $ComponentPath "cloudbuild.yaml"
        if (-not (Test-Path $cloudBuildFile)) {
            Write-ColoredOutput "ERROR: cloudbuild.yaml not found in $ComponentPath" $Red
            return $false
        }
        Push-Location $ComponentPath
        $substitutions = "_ENVIRONMENT=$Environment,_REGION=$Region,_SERVICE_NAME=airms-$($ComponentName.ToLower())-$Environment"
        Write-ColoredOutput "  Submitting build..." $Yellow
        gcloud builds submit --config=cloudbuild.yaml --substitutions=$substitutions --project=$ProjectId
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "SUCCESS: $ComponentName deployed!" $Green
            return $true
        } else {
            Write-ColoredOutput "ERROR: $ComponentName deployment failed!" $Red
            return $false
        }
    }
    catch {
        Write-ColoredOutput "ERROR: Deployment failed: $_" $Red
        return $false
    }
    finally {
        Pop-Location
    }
}

# Main execution
try {
    Write-ColoredOutput "AIRMS GCP Deployment Script" $Blue
    Write-ColoredOutput "Project: $ProjectId | Component: $Component | Environment: $Environment" $Yellow
    
    if (-not (Test-GCloudAuth)) { exit 1 }
    if (-not (Test-GCloudProject -ProjectId $ProjectId)) { exit 1 }
    Enable-RequiredAPIs -ProjectId $ProjectId
    
    $rootPath = $PSScriptRoot
    $success = $false
    
    if ($Component -eq "all" -or $Component -eq "backend") {
        $backendPath = Join-Path $rootPath "backend"
        if (Test-Path $backendPath) {
            $success = Deploy-Component -ComponentName "Backend" -ComponentPath $backendPath -ProjectId $ProjectId -Region $Region -Environment $Environment
        }
    }
    
    if ($Component -eq "all" -or $Component -eq "frontend") {
        $frontendPath = Join-Path $rootPath "frontend"
        if (Test-Path $frontendPath) {
            $success = Deploy-Component -ComponentName "Frontend" -ComponentPath $frontendPath -ProjectId $ProjectId -Region $Region -Environment $Environment
        } else {
            Write-ColoredOutput "ERROR: Frontend directory not found" $Red
            $success = $false
        }
    }
    
    if ($success) {
        Write-ColoredOutput "Deployment completed successfully!" $Green
        Write-ColoredOutput "View services: https://console.cloud.google.com/run?project=$ProjectId" $Blue
    } else {
        Write-ColoredOutput "Deployment failed!" $Red
        exit 1
    }
}
catch {
    Write-ColoredOutput "Script failed: $_" $Red
    exit 1
}
