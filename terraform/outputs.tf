output "vpc_id" {
	description = "VPC ID."
	value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
	description = "Public subnet IDs."
	value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
	description = "Private subnet IDs."
	value       = module.vpc.private_subnet_ids
}

output "eks_cluster_name" {
	description = "EKS cluster name."
	value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
	description = "EKS cluster endpoint."
	value       = module.eks.cluster_endpoint
}

output "eks_cluster_arn" {
	description = "EKS cluster ARN."
	value       = module.eks.cluster_arn
}

output "ecr_repository_urls" {
	description = "ECR repository URLs."
	value       = module.ecr.repository_urls
}

output "eks_cluster_role_arn" {
	description = "IAM role ARN for the EKS control plane."
	value       = module.iam.cluster_role_arn
}

output "eks_node_role_arn" {
	description = "IAM role ARN for EKS worker nodes."
	value       = module.iam.node_role_arn
}
