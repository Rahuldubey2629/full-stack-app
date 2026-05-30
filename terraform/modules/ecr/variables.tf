variable "repository_names" {
  description = "List of ECR repository names to create."
  type        = list(string)
  default     = ["devpulse-backend", "devpulse-frontend", "devpulse-worker"]
}

variable "image_tag_mutability" {
  description = "Image tag mutability setting."
  type        = string
  default     = "MUTABLE"
}

variable "scan_on_push" {
  description = "Whether to scan images on push."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to resources."
  type        = map(string)
  default     = {}
}
