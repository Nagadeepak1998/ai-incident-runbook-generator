variable "aws_region" {
  description = "AWS region for review-only infrastructure resources."
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Name used for ECR and log resources."
  type        = string
  default     = "ai-incident-runbook-generator"
}

