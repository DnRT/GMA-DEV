terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. AWS Secrets Manager
resource "aws_secretsmanager_secret" "discord_webhook" {
  name        = "ops-sentinel/discord-webhook"
  description = "Discord Webhook URL for OpsSentinel"
}

resource "aws_secretsmanager_secret" "telegram_token" {
  name        = "ops-sentinel/telegram-token"
  description = "Telegram Bot Token for OpsSentinel"
}

# 2. IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "ops_sentinel_ecs_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# 3. ECS Fargate Cluster & Task Definition
resource "aws_ecs_cluster" "cluster" {
  name = "ops-sentinel-cluster"
}

resource "aws_ecs_task_definition" "task" {
  family                   = "ops-sentinel"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "ops-sentinel"
      image     = var.container_image
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ]
      environment = [
        { name = "ENVIRONMENT", value = "production" },
        { name = "DISCORD_ENABLED", value = "true" },
        { name = "TELEGRAM_ENABLED", value = "true" },
        { name = "TELEGRAM_CHAT_ID", value = var.telegram_chat_id }
      ]
      secrets = [
        {
          name      = "DISCORD_WEBHOOK_URL"
          valueFrom = aws_secretsmanager_secret.discord_webhook.arn
        },
        {
          name      = "TELEGRAM_BOT_TOKEN"
          valueFrom = aws_secretsmanager_secret.telegram_token.arn
        }
      ]
    }
  ])
}
