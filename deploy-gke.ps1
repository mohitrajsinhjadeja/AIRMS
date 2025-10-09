param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory = $false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory = $false)]
    [string]$ClusterName = "airms-cluster",
    
    [Parameter(Mandatory = $false)]
    [string]$NodeCount = "3",
    
    [Parameter(Mandatory = $false)]
    [string]$MachineType = "e2-standard-4",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("create", "deploy", "update", "delete")]
    [string]$Action = "create"
)

$ErrorActionPreference = "Stop"

# Colors
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
    
    # Check gcloud
    try {
        $gcloudAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
        if ([string]::IsNullOrEmpty($gcloudAccount)) {
            Write-ColoredOutput "❌ Not authenticated with Google Cloud. Run: gcloud auth login" $Red
            exit 1
        }
        Write-ColoredOutput "✅ Google Cloud authenticated as: $gcloudAccount" $Green
    }
    catch {
        Write-ColoredOutput "❌ Google Cloud SDK not found" $Red
        exit 1
    }
    
    # Check kubectl
    try {
        kubectl version --client --short 2>$null | Out-Null
        Write-ColoredOutput "✅ kubectl found" $Green
    }
    catch {
        Write-ColoredOutput "❌ kubectl not found. Please install kubectl." $Red
        exit 1
    }
}

function Enable-APIs {
    Write-ColoredOutput "🔧 Enabling required APIs..." $Blue
    $apis = @(
        "container.googleapis.com",
        "cloudbuild.googleapis.com",
        "containerregistry.googleapis.com",
        "compute.googleapis.com"
    )
    
    foreach ($api in $apis) {
        Write-ColoredOutput "  Enabling $api..." $Yellow
        gcloud services enable $api --project=$ProjectId
    }
    Write-ColoredOutput "✅ APIs enabled" $Green
}

function Create-GKECluster {
    Write-ColoredOutput "🚀 Creating GKE cluster: $ClusterName..." $Blue
    
    try {
        gcloud container clusters create $ClusterName `
            --project=$ProjectId `
            --region=$Region `
            --machine-type=$MachineType `
            --num-nodes=$NodeCount `
            --enable-autoscaling `
            --min-nodes=1 `
            --max-nodes=10 `
            --enable-autorepair `
            --enable-autoupgrade `
            --enable-ip-alias `
            --network=default `
            --subnetwork=default `
            --enable-stackdriver-kubernetes `
            --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver `
            --workload-pool=$ProjectId.svc.id.goog
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ GKE cluster created successfully!" $Green
            
            # Get cluster credentials
            gcloud container clusters get-credentials $ClusterName --region=$Region --project=$ProjectId
            Write-ColoredOutput "✅ Cluster credentials configured" $Green
            
            return $true
        } else {
            Write-ColoredOutput "❌ Failed to create GKE cluster" $Red
            return $false
        }
    }
    catch {
        Write-ColoredOutput "❌ Cluster creation failed: $_" $Red
        return $false
    }
}

function Deploy-Application {
    Write-ColoredOutput "📦 Deploying AIRMS to Kubernetes..." $Blue
    
    $kubernetesDir = Join-Path $PSScriptRoot "kubernetes"
    if (-not (Test-Path $kubernetesDir)) {
        Write-ColoredOutput "❌ Kubernetes directory not found: $kubernetesDir" $Red
        return $false
    }
    
    try {
        # Update manifests with project ID
        $manifestFiles = Get-ChildItem -Path $kubernetesDir -Filter "*.yaml"
        foreach ($file in $manifestFiles) {
            $content = Get-Content $file.FullName -Raw
            $content = $content -replace "PROJECT_ID", $ProjectId
            Set-Content -Path $file.FullName -Value $content
        }
        
        # Apply manifests
        Write-ColoredOutput "  Creating namespace..." $Yellow
        kubectl apply -f "$kubernetesDir/namespace.yaml"
        
        Write-ColoredOutput "  Deploying backend..." $Yellow
        kubectl apply -f "$kubernetesDir/backend-deployment.yaml"
        
        Write-ColoredOutput "  Deploying frontend..." $Yellow
        kubectl apply -f "$kubernetesDir/frontend-deployment.yaml"
        
        Write-ColoredOutput "  Configuring ingress..." $Yellow
        kubectl apply -f "$kubernetesDir/ingress.yaml"
        
        # Wait for deployments
        Write-ColoredOutput "⏳ Waiting for deployments to be ready..." $Yellow
        kubectl wait --for=condition=available --timeout=300s deployment/airms-backend -n airms
        kubectl wait --for=condition=available --timeout=300s deployment/airms-frontend -n airms
        
        Write-ColoredOutput "✅ Application deployed successfully!" $Green
        
        # Show status
        Write-ColoredOutput "📊 Deployment status:" $Cyan
        kubectl get pods -n airms
        kubectl get services -n airms
        kubectl get ingress -n airms
        
        return $true
    }
    catch {
        Write-ColoredOutput "❌ Application deployment failed: $_" $Red
        return $false
    }
}

function Build-Images {
    Write-ColoredOutput "🏗️  Building container images..." $Blue
    
    try {
        # Build and push images using Cloud Build
        gcloud builds submit --config=cloudbuild-advanced.yaml --project=$ProjectId `
            --substitutions=_ENVIRONMENT=prod,_REGION=$Region,_ARTIFACT_REPO=airms-prod
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Images built and pushed successfully!" $Green
            return $true
        } else {
            Write-ColoredOutput "❌ Image build failed" $Red
            return $false
        }
    }
    catch {
        Write-ColoredOutput "❌ Image build failed: $_" $Red
        return $false
    }
}

function Delete-Cluster {
    Write-ColoredOutput "🗑️  Deleting GKE cluster: $ClusterName..." $Red
    
    $confirmation = Read-Host "Are you sure you want to delete the cluster? (yes/no)"
    if ($confirmation -ne "yes") {
        Write-ColoredOutput "❌ Deletion cancelled" $Yellow
        return $false
    }
    
    try {
        gcloud container clusters delete $ClusterName --region=$Region --project=$ProjectId --quiet
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Cluster deleted successfully" $Green
            return $true
        } else {
            Write-ColoredOutput "❌ Failed to delete cluster" $Red
            return $false
        }
    }
    catch {
        Write-ColoredOutput "❌ Cluster deletion failed: $_" $Red
        return $false
    }
}

# Main execution
try {
    Write-ColoredOutput "🌟 AIRMS GKE Deployment Script" $Cyan
    Write-ColoredOutput "Project: $ProjectId | Cluster: $ClusterName | Action: $Action" $Yellow
    
    Test-Prerequisites
    
    switch ($Action) {
        "create" {
            Enable-APIs
            if (Create-GKECluster) {
                if (Build-Images) {
                    Deploy-Application
                }
            }
        }
        
        "deploy" {
            # Get cluster credentials
            gcloud container clusters get-credentials $ClusterName --region=$Region --project=$ProjectId
            if (Build-Images) {
                Deploy-Application
            }
        }
        
        "update" {
            gcloud container clusters get-credentials $ClusterName --region=$Region --project=$ProjectId
            Deploy-Application
        }
        
        "delete" {
            Delete-Cluster
        }
    }
    
    Write-ColoredOutput "🎉 Operation completed!" $Green
    
} catch {
    Write-ColoredOutput "💥 Script failed: $_" $Red
    exit 1
}
