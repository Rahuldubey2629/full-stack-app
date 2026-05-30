variable "cluster_name" {
  description = "Name of the EKS cluster."
  type        = string
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
