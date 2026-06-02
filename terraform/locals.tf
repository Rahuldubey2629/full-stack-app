locals {
  tags = {
    Project     = "devpulse"
    Environment = var.environment
    ManagedBy  = "Terraform"
  }
}