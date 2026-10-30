variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP region (Default: southamerica-west1 Santiago, Chile)"
  default     = "southamerica-west1"
}

variable "container_image" {
  type        = string
  description = "Container image URI in Artifact Registry or Docker Hub"
  default     = "southamerica-west1-docker.pkg.dev/my-project/ops-sentinel-repo/ops-sentinel:latest"
}

variable "telegram_chat_id" {
  type        = string
  description = "Destination Telegram Chat ID for alerts"
}

variable "monitored_targets_json" {
  type        = string
  description = "JSON-encoded array of URLs to monitor"
  default     = "[{\"name\":\"Main API\",\"url\":\"https://httpbin.org/status/200\",\"interval_seconds\":60,\"expected_status\":200}]"
}
