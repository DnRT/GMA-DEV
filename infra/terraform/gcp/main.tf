terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.20.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Artifact Registry for Container Image
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "ops-sentinel-repo"
  description   = "Docker repository for OpsSentinel ChatOps"
  format        = "DOCKER"
}

# 2. Secret Manager for Sensitive Tokens (Ley 21.663 Zero Hardcoding)
resource "google_secret_manager_secret" "discord_webhook" {
  secret_id = "ops-sentinel-discord-webhook"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "telegram_token" {
  secret_id = "ops-sentinel-telegram-token"
  replication {
    auto {}
  }
}

# 3. Service Account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "ops-sentinel-runner"
  display_name = "OpsSentinel Cloud Run Service Account"
}

resource "google_secret_manager_secret_iam_member" "discord_secret_access" {
  secret_id = google_secret_manager_secret.discord_webhook.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "telegram_secret_access" {
  secret_id = google_secret_manager_secret.telegram_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# 4. Google Cloud Run v2 (Serverless, Resilient & Multi-zone)
resource "google_cloud_run_v2_service" "ops_sentinel" {
  name     = "ops-sentinel"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = var.container_image

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "ENVIRONMENT"
        value = "production"
      }
      env {
        name  = "PORT"
        value = "8080"
      }
      env {
        name  = "DISCORD_ENABLED"
        value = "true"
      }
      env {
        name  = "TELEGRAM_ENABLED"
        value = "true"
      }
      env {
        name  = "TELEGRAM_CHAT_ID"
        value = var.telegram_chat_id
      }
      env {
        name  = "MONITORED_TARGETS"
        value = var.monitored_targets_json
      }

      # Injected from Secret Manager
      env {
        name = "DISCORD_WEBHOOK_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.discord_webhook.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "TELEGRAM_BOT_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.telegram_token.secret_id
            version = "latest"
          }
        }
      }

      startup_probe {
        http_get {
          path = "/healthz"
          port = 8080
        }
        period_seconds   = 10
        timeout_seconds  = 5
        failure_threshold = 3
      }
    }
  }

  depends_on = [
    google_secret_manager_secret_iam_member.discord_secret_access,
    google_secret_manager_secret_iam_member.telegram_secret_access
  ]
}

# 5. Cloud Run Public / Authorized Ingress Policy
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.ops_sentinel.name
  location = google_cloud_run_v2_service.ops_sentinel.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 6. Cloud Scheduler: Trigger Daily Health Report at 09:00 CLT (Santiago)
resource "google_cloud_scheduler_job" "daily_report_trigger" {
  name             = "ops-sentinel-daily-report"
  description      = "Triggers OpsSentinel daily health report"
  schedule         = "0 9 * * *"
  time_zone        = "America/Santiago"
  attempt_deadline = "60s"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_v2_service.ops_sentinel.uri}/api/v1/report/trigger"
  }
}
