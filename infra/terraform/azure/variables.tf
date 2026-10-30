variable "resource_group_name" {
  type        = string
  description = "Azure Resource Group name"
  default     = "rg-ops-sentinel"
}

variable "location" {
  type        = string
  description = "Azure region (e.g. brazilsouth or eastus)"
  default     = "brazilsouth"
}

variable "container_image" {
  type        = string
  description = "Docker image repository URL"
  default     = "docker.io/library/ops-sentinel:latest"
}

variable "telegram_chat_id" {
  type        = string
  description = "Telegram Chat ID for alerts"
}
