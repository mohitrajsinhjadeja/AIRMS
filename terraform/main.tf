# AIRMS GCP Infrastructure with Terraform
# Advanced deployment with Cloud Run, Cloud SQL, and monitoring

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "domain_name" {
  description = "Custom domain name (optional)"
  type        = string
  default     = ""
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "artifactregistry.googleapis.com",
    "sql-component.googleapis.com",
    "sqladmin.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "secretmanager.googleapis.com",
    "compute.googleapis.com"
  ])

  service = each.key
  project = var.project_id

  disable_dependent_services = false
  disable_on_destroy         = false
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "airms_repo" {
  location      = var.region
  repository_id = "airms-${var.environment}"
  description   = "AIRMS container repository for ${var.environment}"
  format        = "DOCKER"

  depends_on = [google_project_service.required_apis]
}

# Cloud SQL instance for MongoDB alternative (PostgreSQL)
resource "google_sql_database_instance" "airms_db" {
  name             = "airms-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier                        = var.environment == "prod" ? "db-custom-2-4096" : "db-f1-micro"
    availability_type           = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    disk_type                   = "PD_SSD"
    disk_size                   = var.environment == "prod" ? 100 : 20
    disk_autoresize             = true
    disk_autoresize_limit       = var.environment == "prod" ? 500 : 100

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = var.environment == "prod"
      backup_retention_settings {
        retained_backups = var.environment == "prod" ? 30 : 7
      }
    }

    ip_configuration {
      ipv4_enabled    = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }

    database_flags {
      name  = "log_statement"
      value = "all"
    }
  }

  deletion_protection = var.environment == "prod"

  depends_on = [google_project_service.required_apis]
}

# Database
resource "google_sql_database" "airms_database" {
  name     = "airms"
  instance = google_sql_database_instance.airms_db.name
}

# Database user
resource "google_sql_user" "airms_user" {
  name     = "airms_user"
  instance = google_sql_database_instance.airms_db.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Secret Manager for sensitive data
resource "google_secret_manager_secret" "db_password" {
  secret_id = "airms-db-password-${var.environment}"

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "airms-jwt-secret-${var.environment}"

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# Service Account for Cloud Run
resource "google_service_account" "airms_backend" {
  account_id   = "airms-backend-${var.environment}"
  display_name = "AIRMS Backend Service Account"
  description  = "Service account for AIRMS backend Cloud Run service"
}

resource "google_service_account" "airms_frontend" {
  account_id   = "airms-frontend-${var.environment}"
  display_name = "AIRMS Frontend Service Account"
  description  = "Service account for AIRMS frontend Cloud Run service"
}

# IAM bindings for backend service account
resource "google_project_iam_member" "backend_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.airms_backend.email}"
}

resource "google_project_iam_member" "backend_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.airms_backend.email}"
}

resource "google_project_iam_member" "backend_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.airms_backend.email}"
}

resource "google_project_iam_member" "backend_trace_agent" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.airms_backend.email}"
}

# Cloud Run service for backend
resource "google_cloud_run_v2_service" "airms_backend" {
  name     = "airms-backend-${var.environment}"
  location = var.region

  template {
    service_account = google_service_account.airms_backend.email
    
    scaling {
      min_instance_count = var.environment == "prod" ? 1 : 0
      max_instance_count = var.environment == "prod" ? 10 : 3
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.airms_repo.repository_id}/airms-backend:latest"
      
      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = var.environment == "prod" ? "2" : "1"
          memory = var.environment == "prod" ? "2Gi" : "1Gi"
        }
        cpu_idle = true
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "DATABASE_URL"
        value = "postgresql://${google_sql_user.airms_user.name}:${random_password.db_password.result}@${google_sql_database_instance.airms_db.connection_name}/${google_sql_database.airms_database.name}"
      }

      env {
        name = "JWT_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.jwt_secret.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "CORS_ORIGINS"
        value = var.environment == "prod" ? "https://${var.domain_name}" : "*"
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3
      }
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Run service for frontend
resource "google_cloud_run_v2_service" "airms_frontend" {
  name     = "airms-frontend-${var.environment}"
  location = var.region

  template {
    service_account = google_service_account.airms_frontend.email
    
    scaling {
      min_instance_count = var.environment == "prod" ? 1 : 0
      max_instance_count = var.environment == "prod" ? 5 : 2
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.airms_repo.repository_id}/airms-frontend:latest"
      
      ports {
        container_port = 3000
      }

      resources {
        limits = {
          cpu    = var.environment == "prod" ? "1" : "0.5"
          memory = var.environment == "prod" ? "1Gi" : "512Mi"
        }
        cpu_idle = true
      }

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.airms_backend.uri
      }

      env {
        name  = "NODE_ENV"
        value = var.environment == "prod" ? "production" : "development"
      }
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [google_project_service.required_apis]
}

# IAM policy for public access
resource "google_cloud_run_service_iam_member" "backend_public" {
  service  = google_cloud_run_v2_service.airms_backend.name
  location = google_cloud_run_v2_service.airms_backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "frontend_public" {
  service  = google_cloud_run_v2_service.airms_frontend.name
  location = google_cloud_run_v2_service.airms_frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Build triggers
resource "google_cloudbuild_trigger" "backend_trigger" {
  name        = "airms-backend-${var.environment}"
  description = "Build and deploy AIRMS backend"

  github {
    owner = "your-github-username"  # Update this
    name  = "AIRMS"                 # Update this
    push {
      branch = var.environment == "prod" ? "main" : "develop"
    }
  }

  included_files = ["backend/**"]

  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build",
        "-t", "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.airms_repo.repository_id}/airms-backend:$SHORT_SHA",
        "-t", "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.airms_repo.repository_id}/airms-backend:latest",
        "./backend"
      ]
    }

    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "push",
        "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.airms_repo.repository_id}/airms-backend:$SHORT_SHA"
      ]
    }

    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "push",
        "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.airms_repo.repository_id}/airms-backend:latest"
      ]
    }

    step {
      name = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "gcloud"
      args = [
        "run", "deploy", google_cloud_run_v2_service.airms_backend.name,
        "--image", "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.airms_repo.repository_id}/airms-backend:$SHORT_SHA",
        "--region", var.region,
        "--platform", "managed"
      ]
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Monitoring and alerting
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "AIRMS High Error Rate - ${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run Error Rate"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${google_cloud_run_v2_service.airms_backend.name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.1

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = []  # Add your notification channels here

  alert_strategy {
    auto_close = "1800s"
  }

  depends_on = [google_project_service.required_apis]
}

# Outputs
output "backend_url" {
  description = "Backend Cloud Run service URL"
  value       = google_cloud_run_v2_service.airms_backend.uri
}

output "frontend_url" {
  description = "Frontend Cloud Run service URL"
  value       = google_cloud_run_v2_service.airms_frontend.uri
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.airms_db.connection_name
  sensitive   = true
}

output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.airms_repo.repository_id}"
}
