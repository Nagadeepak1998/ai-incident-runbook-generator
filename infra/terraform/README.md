# Terraform Skeleton

This directory is intentionally small. It creates an ECR repository and CloudWatch log
group that would support a containerized deployment while avoiding runtime compute by
default.

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
```

