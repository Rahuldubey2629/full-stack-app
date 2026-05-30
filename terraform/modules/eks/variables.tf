variable "cluster_name" {
  description = "Name of the EKS cluster."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for the cluster."
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the cluster and node groups."
  type        = list(string)
}

variable "cluster_role_arn" {
  description = "IAM role ARN for the EKS control plane."
  type        = string
}

variable "node_role_arn" {
  description = "IAM role ARN for EKS worker nodes."
  type        = string
}

variable "node_instance_type" {
  description = "EC2 instance type for worker nodes."
  type        = string
  default     = "t3.small"
}

variable "node_count" {
  description = "Desired number of worker nodes."
  type        = number
  default     = 2
}

variable "environment" {
  description = "Environment tag value."
  type        = string
  default     = "production"
}

variable "tags" {
  description = "Additional tags to apply to resources."
  type        = map(string)
  default     = {}
}
