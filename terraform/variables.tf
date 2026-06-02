variable "aws_region" {
  description = "Region where we will deploy DevPulse."
  type        = string
  default     = "ap-southeast-2"
}

variable "name_prefix" {
  description = "Prefix used for naming resources."
  type        = string
  default     = "devpulse"
}

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
  default     = "devpulse-cluster"
}

variable "cluster_version" {
  description = "Kubernetes version for the EKS cluster."
  type        = string
  default     = "1.34"
}

variable "environment" {
  description = "Environment tag value."
  type        = string
  default     = "production"
}

variable "node_instance_type" {
  description = "EC2 instance type for worker nodes."
  type        = string
  default     = "t3.small"
}

variable "node_count" {
  description = "Desired number of worker nodes."
  type        = number
  default     = 3
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "Availability zones to use."
  type        = list(string)
  default     = ["ap-southeast-2a", "ap-southeast-2b", "ap-southeast-2c"]
}

variable "public_subnets" {
  description = "CIDR blocks for public subnets."
  type        = list(string)
  default     = ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  description = "CIDR blocks for private subnets."
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
}

variable "enable_nat_gateway" {
  description = "Whether to create NAT gateways for private subnets."
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Whether to use a single NAT gateway for all private subnets."
  type        = bool
  default     = true
}

variable "ecr_repository_names" {
  description = "List of ECR repository names to create."
  type        = list(string)
  default     = ["devpulse-backend", "devpulse-frontend"]
}