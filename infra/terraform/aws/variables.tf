variable "aws_region" {
  type        = string
  description = "AWS Region (Default: us-east-1)"
  default     = "us-east-1"
}

variable "container_image" {
  type        = string
  description = "Docker image URI (e.g. from ECR or Docker Hub)"
  default     = "public.ecr.aws/ops-sentinel/ops-sentinel:latest"
}

variable "telegram_chat_id" {
  type        = string
  description = "Destination Telegram Chat ID"
}
