output "repository_url" {
  description = "ECR repository URL for the service image."
  value       = aws_ecr_repository.app.repository_url
}

output "log_group_name" {
  description = "CloudWatch log group for service logs."
  value       = aws_cloudwatch_log_group.app.name
}

