output "cloud_run_url" {
  description = "The public/authorized URL of the OpsSentinel Cloud Run service"
  value       = google_cloud_run_v2_service.ops_sentinel.uri
}

output "artifact_registry_repo" {
  description = "Artifact Registry Docker repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}"
}

output "audit_logging_compliance" {
  description = "Compliance badge note"
  value       = "Audit logging configured with immutable UTC timestamps compliant with Ley 21.663"
}
