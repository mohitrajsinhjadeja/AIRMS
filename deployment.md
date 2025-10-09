# AirMS Deployment Documentation

## Overview
The AirMS project is deployed across **frontend** (Vercel), **backend** (Google Cloud Run), and a **landing build process** (Cloud Build).  

This document explains the deployment process for each part of the stack and provides the live service URLs.

---

## Deployment Steps

### 1. Frontend (Vercel)
The frontend is hosted on **Vercel**.

#### Deployment Command
```bash
vercel --prod
```

#### Live URL
👉 [https://airms.vercel.app/](https://airms.vercel.app/)

---

### 2. Landing Build (Google Cloud Build)
The frontend build is also configured via **Google Cloud Build**.

#### Deployment Command
```bash
gcloud builds submit --config=cloudbuild.yaml
```

---

### 3. Backend (Google Cloud Run)
The backend is containerized, pushed to **Google Container Registry**, and deployed via **Cloud Run**.

#### Build & Push Docker Image
```bash
gcloud builds submit --tag gcr.io/airms-472612/airms-backend
```

#### Deploy to Cloud Run
```bash
gcloud run deploy airms-backend   --image gcr.io/airms-472612/airms-backend   --platform managed   --region us-central1
```

⚠️ **Note:** The original command had `us-centrall`. It should be `us-central1`.

#### Live URLs
- Backend: 👉 [https://airms-backend-1013218741719.us-central1.run.app](https://airms-backend-1013218741719.us-central1.run.app)  
- Frontend (GCP Build): 👉 [https://airms-frontend-1013218741719.us-central1.run.app](https://airms-frontend-1013218741719.us-central1.run.app)

---

## Git Cleanup & Secure Commit
To reset the Git history while excluding sensitive data (like `.env`):

```bash
git checkout --orphan latest_branch
git add --all
git reset .env
git commit -m "Initial commit without sensitive data"
git branch -D main
git branch -m main
git push -f origin main
```

---

## Summary of Services

| Component          | Platform            | Deployment Command                              | URL                                                                 |
|--------------------|---------------------|-------------------------------------------------|---------------------------------------------------------------------|
| **Frontend**       | Vercel              | `vercel --prod`                                 | [https://airms.vercel.app](https://airms.vercel.app)                |
| **Frontend Build** | Google Cloud Build  | `gcloud builds submit --config=cloudbuild.yaml` | [https://airms-frontend-1013218741719.us-central1.run.app](https://airms-frontend-1013218741719.us-central1.run.app) |
| **Backend**        | Google Cloud Run    | `gcloud run deploy airms-backend ...`           | [https://airms-backend-1013218741719.us-central1.run.app](https://airms-backend-1013218741719.us-central1.run.app) |

---
