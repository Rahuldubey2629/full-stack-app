output "cluster_name" {
  description = "EKS cluster name."
  value       = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint."
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_arn" {
  description = "EKS cluster ARN."
  value       = aws_eks_cluster.this.arn
}

output "cluster_security_group_id" {
  description = "Cluster security group ID."
  value       = aws_security_group.cluster.id
}

output "node_group_arn" {
  description = "Node group ARN."
  value       = aws_eks_node_group.this.arn
}

output "oidc_provider_arn" {
  description = "OIDC provider ARN for the cluster."
  value       = aws_iam_openid_connect_provider.this.arn
}

output "ebs_csi_role_arn" {
  description = "IAM role ARN used by the EBS CSI driver."
  value       = aws_iam_role.ebs_csi.arn
}
