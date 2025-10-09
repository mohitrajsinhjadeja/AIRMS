param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory = $false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory = $false)]
    [string]$DomainName = "",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("plan", "apply", "destroy")]
    [string]$Action = "plan",
    
    [Parameter(Mandatory = $false)]
    [switch]$AutoApprove
)

$ErrorActionPreference = "Stop"

# Colors for output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red
$Blue = [System.ConsoleColor]::Blue
$Cyan = [System.ConsoleColor]::Cyan

function Write-ColoredOutput {
    param([string]$Message, [System.ConsoleColor]$Color = [System.ConsoleColor]::White)
    Write-Host $Message -ForegroundColor $Color
}

function Test-Prerequisites {
    Write-ColoredOutput "🔍 Checking prerequisites..." $Blue
    
    # Check if Terraform is installed
    try {
        $terraformVersion = terraform version
        Write-ColoredOutput "✅ Terraform found: $($terraformVersion[0])" $Green
    }
    catch {
        Write-ColoredOutput "❌ Terraform not found. Please install Terraform first." $Red
        Write-ColoredOutput "   Download from: https://www.terraform.io/downloads.html" $Yellow
        exit 1
    }
    
    # Check if gcloud is installed and authenticated
    try {
        $gcloudAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
        if ([string]::IsNullOrEmpty($gcloudAccount)) {
            Write-ColoredOutput "❌ Not authenticated with Google Cloud. Run: gcloud auth login" $Red
            exit 1
        }
        Write-ColoredOutput "✅ Google Cloud authenticated as: $gcloudAccount" $Green
    }
    catch {
        Write-ColoredOutput "❌ Google Cloud SDK not found or not authenticated." $Red
        exit 1
    }
    
    # Check if project exists
    try {
        $project = gcloud projects describe $ProjectId --format="value(projectId)" 2>$null
        if ([string]::IsNullOrEmpty($project)) {
            Write-ColoredOutput "❌ Cannot access project '$ProjectId'" $Red
            exit 1
        }
        Write-ColoredOutput "✅ Project verified: $ProjectId" $Green
    }
    catch {
        Write-ColoredOutput "❌ Project verification failed" $Red
        exit 1
    }
}

function Initialize-Terraform {
    Write-ColoredOutput "🚀 Initializing Terraform..." $Blue
    
    $terraformDir = Join-Path $PSScriptRoot "terraform"
    if (-not (Test-Path $terraformDir)) {
        Write-ColoredOutput "❌ Terraform directory not found: $terraformDir" $Red
        exit 1
    }
    
    Push-Location $terraformDir
    
    try {
        # Initialize Terraform
        terraform init -upgrade
        if ($LASTEXITCODE -ne 0) {
            throw "Terraform init failed"
        }
        Write-ColoredOutput "✅ Terraform initialized successfully" $Green
        
        # Create terraform.tfvars if it doesn't exist
        $tfvarsFile = "terraform.tfvars"
        if (-not (Test-Path $tfvarsFile)) {
            Write-ColoredOutput "📝 Creating terraform.tfvars..." $Yellow
            @"
project_id = "$ProjectId"
region = "$Region"
environment = "$Environment"
domain_name = "$DomainName"
"@ | Out-File -FilePath $tfvarsFile -Encoding UTF8
            Write-ColoredOutput "✅ Created terraform.tfvars" $Green
        }
        
        return $true
    }
    catch {
        Write-ColoredOutput "❌ Terraform initialization failed: $_" $Red
        return $false
    }
    finally {
        Pop-Location
    }
}

function Invoke-TerraformPlan {
    Write-ColoredOutput "📋 Running Terraform plan..." $Blue
    
    Push-Location (Join-Path $PSScriptRoot "terraform")
    
    try {
        terraform plan -detailed-exitcode
        $exitCode = $LASTEXITCODE
        
        switch ($exitCode) {
            0 { 
                Write-ColoredOutput "✅ No changes needed" $Green
                return "no-changes"
            }
            1 { 
                Write-ColoredOutput "❌ Terraform plan failed" $Red
                return "error"
            }
            2 { 
                Write-ColoredOutput "📝 Changes detected and ready to apply" $Yellow
                return "changes"
            }
            default {
                Write-ColoredOutput "❌ Unexpected exit code: $exitCode" $Red
                return "error"
            }
        }
    }
    catch {
        Write-ColoredOutput "❌ Terraform plan failed: $_" $Red
        return "error"
    }
    finally {
        Pop-Location
    }
}

function Invoke-TerraformApply {
    Write-ColoredOutput "🚀 Applying Terraform configuration..." $Blue
    
    Push-Location (Join-Path $PSScriptRoot "terraform")
    
    try {
        if ($AutoApprove) {
            terraform apply -auto-approve
        } else {
            terraform apply
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Terraform apply completed successfully!" $Green
            
            # Show outputs
            Write-ColoredOutput "📊 Deployment outputs:" $Cyan
            terraform output
            
            return $true
        } else {
            Write-ColoredOutput "❌ Terraform apply failed" $Red
            return $false
        }
    }
    catch {
        Write-ColoredOutput "❌ Terraform apply failed: $_" $Red
        return $false
    }
    finally {
        Pop-Location
    }
}

function Invoke-TerraformDestroy {
    Write-ColoredOutput "🗑️  Destroying Terraform-managed infrastructure..." $Red
    Write-ColoredOutput "⚠️  WARNING: This will destroy all resources!" $Yellow
    
    if (-not $AutoApprove) {
        $confirmation = Read-Host "Are you sure you want to destroy all resources? (yes/no)"
        if ($confirmation -ne "yes") {
            Write-ColoredOutput "❌ Destruction cancelled" $Yellow
            return $false
        }
    }
    
    Push-Location (Join-Path $PSScriptRoot "terraform")
    
    try {
        if ($AutoApprove) {
            terraform destroy -auto-approve
        } else {
            terraform destroy
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Infrastructure destroyed successfully" $Green
            return $true
        } else {
            Write-ColoredOutput "❌ Terraform destroy failed" $Red
            return $false
        }
    }
    catch {
        Write-ColoredOutput "❌ Terraform destroy failed: $_" $Red
        return $false
    }
    finally {
        Pop-Location
    }
}

function Build-And-Deploy-Images {
    Write-ColoredOutput "🏗️  Building and deploying container images..." $Blue
    
    try {
        # Enable required APIs
        Write-ColoredOutput "🔧 Enabling required APIs..." $Yellow
        gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com --project=$ProjectId
        
        # Submit build
        Write-ColoredOutput "🚀 Submitting Cloud Build..." $Yellow
        gcloud builds submit --config=cloudbuild-advanced.yaml --project=$ProjectId `
            --substitutions=_ENVIRONMENT=$Environment,_REGION=$Region,_ARTIFACT_REPO=airms-$Environment
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Build and deployment completed successfully!" $Green
            return $true
        } else {
            Write-ColoredOutput "❌ Build failed" $Red
            return $false
        }
    }
    catch {
        Write-ColoredOutput "❌ Build and deployment failed: $_" $Red
        return $false
    }
}

# Main execution
try {
    Write-ColoredOutput "🌟 AIRMS Advanced GCP Deployment with Terraform" $Cyan
    Write-ColoredOutput "Project: $ProjectId | Environment: $Environment | Action: $Action" $Yellow
    Write-ColoredOutput "Region: $Region | Domain: $DomainName" $Yellow
    
    # Check prerequisites
    Test-Prerequisites
    
    # Initialize Terraform
    if (-not (Initialize-Terraform)) {
        exit 1
    }
    
    switch ($Action) {
        "plan" {
            $planResult = Invoke-TerraformPlan
            if ($planResult -eq "error") {
                exit 1
            } elseif ($planResult -eq "changes") {
                Write-ColoredOutput "💡 To apply these changes, run with -Action apply" $Cyan
            }
        }
        
        "apply" {
            $planResult = Invoke-TerraformPlan
            if ($planResult -eq "error") {
                exit 1
            } elseif ($planResult -eq "changes") {
                if (Invoke-TerraformApply) {
                    Write-ColoredOutput "🏗️  Now building and deploying application images..." $Blue
                    Build-And-Deploy-Images
                }
            } elseif ($planResult -eq "no-changes") {
                Write-ColoredOutput "🏗️  Infrastructure up to date. Building and deploying images..." $Blue
                Build-And-Deploy-Images
            }
        }
        
        "destroy" {
            if (-not (Invoke-TerraformDestroy)) {
                exit 1
            }
        }
    }
    
    Write-ColoredOutput "🎉 Operation completed successfully!" $Green
    Write-ColoredOutput "📊 View your services at: https://console.cloud.google.com/run?project=$ProjectId" $Cyan
    
} catch {
    Write-ColoredOutput "💥 Script failed: $_" $Red
    exit 1
}
