# GCP Deployment Guide for AIRMS

## Prerequisites

1. **Google Cloud SDK installed and authenticated**
   ```powershell
   # Install gcloud CLI (if not already installed)
   # Download from: https://cloud.google.com/sdk/docs/install-windows

   # Authenticate with Google Cloud
   gcloud auth login

   # Set your default project (optional)
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Required APIs enabled** (the script will enable these automatically):
   - Cloud Build API
   - Cloud Run API
   - Container Registry API
   - Artifact Registry API

## Quick Start

### Deploy Everything
```powershell
# IMPORTANT: Run from the project root directory (F:\airms\AIRMS-main)
cd F:\airms\AIRMS-main

# Deploy both frontend and backend to GCP
.\gcp-deploy.ps1 -ProjectId "your-project-id"
```

### Deploy Specific Components
```powershell
# IMPORTANT: Run from the project root directory (F:\airms\AIRMS-main)
cd F:\airms\AIRMS-main

# Deploy only the frontend
.\gcp-deploy.ps1 -ProjectId "your-project-id" -Component "frontend"

# Deploy only the backend
.\gcp-deploy.ps1 -ProjectId "your-project-id" -Component "backend"
```

### Deploy to Different Regions/Environments
```powershell
# Deploy to staging environment in us-west1
.\gcp-deploy.ps1 -ProjectId "your-project-id" -Environment "staging" -Region "us-west1"

# Deploy to production
.\gcp-deploy.ps1 -ProjectId "your-project-id" -Environment "prod" -Region "us-central1"
```

## Manual Deployment

If you prefer to run the commands manually:

### Root Level (Deploy Both Services)
```powershell
# From the root directory
gcloud builds submit --config=cloudbuild.yaml --project=YOUR_PROJECT_ID
```

### Frontend Only
```powershell
# From the frontend directory
cd frontend
gcloud builds submit --config=cloudbuild.yaml --project=YOUR_PROJECT_ID
```

### Backend Only
```powershell
# From the backend directory  
cd backend
gcloud builds submit --config=cloudbuild.yaml --project=YOUR_PROJECT_ID
```

## Configuration

### Environment Variables (Backend)
Update the substitutions in `backend/cloudbuild.yaml`:

```yaml
substitutions:
  _ENVIRONMENT: 'dev'
  _REGION: 'us-central1'
  _SERVICE_NAME: 'airms-backend-dev'
  _MONGODB_URL: 'your-mongodb-connection-string'
  _JWT_SECRET_KEY: 'your-jwt-secret-key'
```

### Build Arguments (Frontend)
The frontend build uses the following build args:
- `NEXT_PUBLIC_API_URL`: Backend API URL (automatically configured)

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```
   Solution: Run `gcloud auth login`
   ```

2. **Project Not Found**
   ```
   Solution: Verify project ID and ensure you have access
   ```

3. **API Not Enabled**
   ```
   Solution: The script enables APIs automatically, or run:
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com
   ```

4. **Build Timeout**
   ```
   Solution: Increase timeout in cloudbuild.yaml or use larger machine type
   ```

### Viewing Logs
- **Build Logs**: https://console.cloud.google.com/cloud-build/builds?project=YOUR_PROJECT_ID
- **Service Logs**: https://console.cloud.google.com/run?project=YOUR_PROJECT_ID

### Monitoring Deployments
- **Cloud Run Console**: https://console.cloud.google.com/run?project=YOUR_PROJECT_ID
- **Container Images**: https://console.cloud.google.com/gcr/images/YOUR_PROJECT_ID

## Advanced Usage

### Custom Substitutions
```powershell
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=prod,_REGION=us-west1,_SERVICE_NAME=airms-prod \
  --project=YOUR_PROJECT_ID
```

### Using Different Machine Types
Update the `options` section in cloudbuild.yaml:
```yaml
options:
  machineType: 'E2_HIGHCPU_32'  # For faster builds
  logging: CLOUD_LOGGING_ONLY
```

## Security Considerations

1. **Environment Variables**: Store sensitive values in Google Secret Manager
2. **Authentication**: Configure proper IAM roles for services
3. **Network**: Consider VPC connections for database access
4. **HTTPS**: All Cloud Run services use HTTPS by default

## Cost Optimization

1. **Scaling**: Configure min/max instances based on usage
2. **Resources**: Adjust CPU/memory allocation per service needs
3. **Regions**: Choose regions closest to your users
4. **Build Frequency**: Use caching and conditional builds