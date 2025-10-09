# 🚀 Advanced GCP Deployment Guide for AIRMS

This guide provides **three different deployment approaches** for AIRMS on Google Cloud Platform, each with different benefits and use cases.

## 🎯 Deployment Options

### 1. **Terraform + Cloud Run** (Recommended for Production)
- **Infrastructure as Code** with Terraform
- **Serverless** with automatic scaling
- **Managed databases** with Cloud SQL
- **Enterprise-grade** monitoring and security

### 2. **Advanced Cloud Build** (Enhanced CI/CD)
- **Multi-stage builds** with optimization
- **Advanced caching** for faster builds
- **Security scanning** built-in
- **Flexible substitutions**

### 3. **Google Kubernetes Engine (GKE)** (For Complex Workloads)
- **Full container orchestration**
- **Advanced networking** and load balancing
- **Horizontal pod autoscaling**
- **Custom resource management**

---

## 🏗️ Option 1: Terraform + Cloud Run Deployment

### Prerequisites
```powershell
# Install Terraform
# Download from: https://www.terraform.io/downloads.html

# Verify installation
terraform version

# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login
```

### Quick Start
```powershell
# Navigate to project root
cd "F:\New folder\airms\AIRMS-main"

# Copy and configure variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars

# Edit terraform.tfvars with your values:
# project_id = "your-gcp-project-id"
# region = "us-central1"
# environment = "dev"
# domain_name = "airms.yourdomain.com"  # Optional

# Plan the deployment
.\deploy-terraform.ps1 -ProjectId "your-project-id" -Action plan

# Apply the deployment
.\deploy-terraform.ps1 -ProjectId "your-project-id" -Action apply -AutoApprove
```

### What Gets Created
- ✅ **Artifact Registry** for container images
- ✅ **Cloud SQL PostgreSQL** database
- ✅ **Secret Manager** for sensitive data
- ✅ **Cloud Run services** for frontend and backend
- ✅ **Service accounts** with proper IAM
- ✅ **Monitoring and alerting** setup
- ✅ **Load balancing** and SSL certificates

### Benefits
- 🎯 **Infrastructure as Code** - Reproducible deployments
- 🔒 **Enterprise Security** - Secret management, IAM, encryption
- 📊 **Built-in Monitoring** - Logs, metrics, alerts
- 💰 **Cost Optimized** - Pay only for what you use
- 🚀 **Auto-scaling** - Handles traffic spikes automatically

---

## 🔧 Option 2: Advanced Cloud Build

### Features
- **Multi-stage Docker builds** for optimization
- **Parallel builds** for frontend and backend
- **Security scanning** with Container Analysis
- **Health checks** after deployment
- **Flexible environment configurations**

### Usage
```powershell
# Deploy using advanced Cloud Build
gcloud builds submit --config=cloudbuild-advanced.yaml --project=your-project-id \
  --substitutions=_ENVIRONMENT=prod,_REGION=us-central1,_ARTIFACT_REPO=airms-prod

# Or use the existing script with advanced features
.\gcp-deploy.ps1 -ProjectId "your-project-id" -Environment "prod" -Component "all"
```

### Advanced Substitutions
```yaml
# Customize build parameters
_BACKEND_MEMORY: '4Gi'
_BACKEND_CPU: '4'
_BACKEND_MIN_INSTANCES: '2'
_BACKEND_MAX_INSTANCES: '20'
_FRONTEND_MEMORY: '2Gi'
_FRONTEND_CPU: '2'
```

---

## ☸️ Option 3: Google Kubernetes Engine (GKE)

### When to Use GKE
- Complex microservices architecture
- Need for advanced networking
- Custom resource requirements
- Multi-region deployments
- Advanced security policies

### Quick Start
```powershell
# Create GKE cluster and deploy
.\deploy-gke.ps1 -ProjectId "your-project-id" -Action create

# Deploy to existing cluster
.\deploy-gke.ps1 -ProjectId "your-project-id" -Action deploy

# Update deployment
.\deploy-gke.ps1 -ProjectId "your-project-id" -Action update

# Delete cluster
.\deploy-gke.ps1 -ProjectId "your-project-id" -Action delete
```

### GKE Features
- ✅ **Horizontal Pod Autoscaling** (HPA)
- ✅ **Ingress with SSL termination**
- ✅ **Workload Identity** for security
- ✅ **Network policies** for isolation
- ✅ **Persistent volumes** for storage

---

## 🔐 Security Best Practices

### Secret Management
```powershell
# Store secrets in Google Secret Manager
gcloud secrets create airms-jwt-secret --data-file=jwt-secret.txt
gcloud secrets create airms-db-password --data-file=db-password.txt

# Grant access to service accounts
gcloud secrets add-iam-policy-binding airms-jwt-secret \
  --member="serviceAccount:airms-backend@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Network Security
- **VPC-native clusters** for GKE
- **Private Google Access** for Cloud SQL
- **Authorized networks** for database access
- **SSL/TLS encryption** everywhere

### IAM Best Practices
- **Principle of least privilege**
- **Service-specific accounts**
- **Workload Identity** for GKE
- **Regular access reviews**

---

## 📊 Monitoring and Observability

### Built-in Monitoring
- **Cloud Monitoring** for metrics
- **Cloud Logging** for centralized logs
- **Cloud Trace** for distributed tracing
- **Error Reporting** for issue tracking

### Custom Dashboards
```powershell
# Create custom monitoring dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

### Alerting Policies
- **High error rates** (>10%)
- **High latency** (>5s response time)
- **Resource utilization** (>80% CPU/Memory)
- **Database connection** failures

---

## 💰 Cost Optimization

### Cloud Run Optimization
```yaml
# Optimize for cost
resources:
  limits:
    cpu: "1000m"      # 1 vCPU
    memory: "1Gi"     # 1GB RAM
  cpu_idle: true      # Scale to zero when idle
```

### Database Optimization
- **Right-size instances** based on usage
- **Automated backups** with retention policies
- **Read replicas** for read-heavy workloads
- **Connection pooling** to reduce overhead

### Build Optimization
- **Layer caching** in Docker builds
- **Multi-stage builds** to reduce image size
- **Parallel builds** to reduce time
- **Conditional builds** based on changes

---

## 🚀 Deployment Comparison

| Feature | Cloud Run | GKE | Traditional VMs |
|---------|-----------|-----|-----------------|
| **Setup Complexity** | Low | Medium | High |
| **Scaling** | Automatic | Manual/Auto | Manual |
| **Cost** | Pay-per-use | Fixed + Usage | Fixed |
| **Maintenance** | Minimal | Medium | High |
| **Flexibility** | Medium | High | High |
| **Security** | Built-in | Configurable | Manual |

---

## 🎯 Recommended Approach

### For Most Users: **Terraform + Cloud Run**
```powershell
# Complete deployment in one command
.\deploy-terraform.ps1 -ProjectId "your-project-id" -Environment "prod" -Action apply -AutoApprove
```

### For Enterprise: **GKE with Terraform**
```powershell
# Infrastructure with Terraform
.\deploy-terraform.ps1 -ProjectId "your-project-id" -Action apply

# Application on GKE
.\deploy-gke.ps1 -ProjectId "your-project-id" -Action create
```

### For CI/CD: **Advanced Cloud Build**
```yaml
# Set up automated deployments
trigger:
  branch: main
build:
  config: cloudbuild-advanced.yaml
```

---

## 🔧 Troubleshooting

### Common Issues

1. **Permission Denied**
   ```powershell
   # Fix: Enable required APIs
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com
   ```

2. **Build Timeout**
   ```yaml
   # Fix: Increase timeout in cloudbuild.yaml
   timeout: '3600s'  # 1 hour
   ```

3. **Database Connection**
   ```powershell
   # Fix: Check Cloud SQL proxy or connection string
   gcloud sql instances describe INSTANCE_NAME
   ```

4. **SSL Certificate Issues**
   ```powershell
   # Fix: Verify domain ownership
   gcloud compute ssl-certificates describe CERT_NAME
   ```

### Getting Help
- **Cloud Console**: https://console.cloud.google.com
- **Build Logs**: Cloud Build > History
- **Service Logs**: Cloud Run > Logs
- **Monitoring**: Cloud Monitoring > Dashboards

---

## 🎉 Next Steps

After successful deployment:

1. **Configure monitoring alerts**
2. **Set up automated backups**
3. **Configure custom domains**
4. **Implement CI/CD pipelines**
5. **Scale based on usage patterns**

Choose the deployment option that best fits your needs and scale as your requirements grow!
